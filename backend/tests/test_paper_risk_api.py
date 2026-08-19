from datetime import datetime, timezone
from decimal import Decimal

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from app.accounting.service import AccountingService
from app.database import get_session
from app.main import app
from app.market_data.contracts import Quote
from app.market_data.quality import MarketDataUnavailable
from app.market_data.router import get_market_data_service
from app.models import Agent, StrategyEnum
from app.models.accounting import Fill, Order
from app.models.paper_execution import PaperRequest
from app.models.risk import RiskDecision, RiskProfile
from app.risk.bootstrap import ensure_active_risk_profile


class RealFixtureMarketData:
    name = "fixture_real"

    async def get_quote(self, symbol: str) -> Quote:
        canonical = symbol.replace("-", "/").upper()
        now = datetime.now(timezone.utc)
        return Quote(
            symbol=canonical,
            price=Decimal("100"),
            observed_at=now,
            received_at=now,
            provider=self.name,
            provider_symbol=canonical.replace("/", ""),
            timestamp_source="provider",
        )


class BtcOnlyMarketData(RealFixtureMarketData):
    def __init__(self):
        self.symbols = []

    async def get_quote(self, symbol: str) -> Quote:
        canonical = symbol.replace("-", "/").upper()
        self.symbols.append(canonical)
        if canonical != "BTC/USDT":
            raise MarketDataUnavailable("unrelated mark unavailable")
        return await super().get_quote(canonical)


@pytest.fixture
def setup_app():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)

    def _get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = _get_session
    app.dependency_overrides[get_market_data_service] = lambda: RealFixtureMarketData()
    with Session(engine) as session:
        agent = Agent(nombre="RISK-API", presupuesto_inicial=1000, presupuesto_actual=1000, estrategia=StrategyEnum.S1)
        session.add(agent); session.commit(); session.refresh(agent)
        account_id = AccountingService(session).create_account(agent.id, Decimal("1000")).id
        ensure_active_risk_profile(session)
    yield engine, account_id
    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(engine)


@pytest.mark.asyncio
async def test_paper_api_requires_risk_allow_and_idempotent_replay_creates_one_decision(setup_app):
    engine, account_id = setup_app
    params = {"request_id": "risk-ok-1", "account_id": account_id, "symbol": "BTC-USDT", "side": "BUY", "quantity": "1"}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        first = await client.post("/api/paper/orders/market", params=params)
        second = await client.post("/api/paper/orders/market", params=params)
    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["idempotent_replay"] is True
    with Session(engine) as session:
        decisions = session.exec(select(RiskDecision)).all()
        assert len(decisions) == 1
        assert decisions[0].decision == "ALLOW"
        assert decisions[0].consumed_at is not None
        assert len(session.exec(select(Fill)).all()) == 1


@pytest.mark.asyncio
async def test_risk_rejection_returns_409_and_creates_no_paper_financial_order(setup_app):
    engine, account_id = setup_app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/paper/orders/market", params={
            "request_id": "risk-reject-1", "account_id": account_id,
            "symbol": "BTC-USDT", "side": "BUY", "quantity": "3",
        })
    assert response.status_code == 409
    assert "MAX_ORDER_NOTIONAL" in response.json()["detail"]
    with Session(engine) as session:
        decisions = session.exec(select(RiskDecision)).all()
        assert len(decisions) == 1
        assert decisions[0].decision == "REJECT"
        assert session.exec(select(Order)).all() == []
        assert session.exec(select(Fill)).all() == []


@pytest.mark.asyncio
async def test_paused_risk_profile_blocks_paper_execution(setup_app):
    engine, account_id = setup_app
    with Session(engine) as session:
        profile = session.exec(select(RiskProfile).where(RiskProfile.active == True)).one()
        profile.paused = True
        session.add(profile); session.commit()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/paper/orders/market", params={
            "request_id": "risk-paused", "account_id": account_id,
            "symbol": "BTC-USDT", "side": "BUY", "quantity": "1",
        })
    assert response.status_code == 409
    assert "RISK_PAUSED" in response.json()["detail"]


@pytest.mark.asyncio
async def test_risk_reducing_sell_does_not_require_unrelated_position_mark(setup_app):
    engine, account_id = setup_app
    with Session(engine) as session:
        accounting = AccountingService(session)
        for symbol in ("BTC/USDT", "ETH/USDT"):
            order = accounting.create_order(account_id, symbol, "BUY", Decimal("1"))
            accounting.apply_fill(
                order.id,
                quantity=Decimal("1"),
                price=Decimal("100"),
                fee=Decimal("0"),
                observed_at=datetime.now(timezone.utc),
            )

    provider = BtcOnlyMarketData()
    app.dependency_overrides[get_market_data_service] = lambda: provider
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/paper/orders/market", params={
            "request_id": "risk-reducing-sell",
            "account_id": account_id,
            "symbol": "BTC-USDT",
            "side": "SELL",
            "quantity": "1",
        })

    assert response.status_code == 200
    assert provider.symbols == ["BTC/USDT"]
    with Session(engine) as session:
        decision = session.exec(
            select(RiskDecision).where(RiskDecision.side == "SELL")
        ).one()
        assert decision.decision == "ALLOW"


@pytest.mark.asyncio
async def test_missing_account_returns_404_and_request_is_completed_idempotently(setup_app):
    engine, _account_id = setup_app
    params = {
        "request_id": "missing-account",
        "account_id": 999999,
        "symbol": "BTC-USDT",
        "side": "BUY",
        "quantity": "1",
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        first = await client.post("/api/paper/orders/market", params=params)
        second = await client.post("/api/paper/orders/market", params=params)

    assert first.status_code == 404
    assert second.status_code == 404
    with Session(engine) as session:
        request = session.exec(
            select(PaperRequest).where(PaperRequest.request_id == "missing-account")
        ).one()
        assert request.status == "COMPLETED"
        assert request.http_status == 404
        assert session.exec(select(RiskDecision)).all() == []
        assert session.exec(select(Order)).all() == []

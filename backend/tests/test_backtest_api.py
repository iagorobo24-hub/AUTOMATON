from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from app.backtesting.router import get_historical_provider
from app.backtesting.runner import recover_interrupted_runs
from app.database import get_session
from app.main import app
from app.market_data.contracts import Candle
from app.models.backtesting import BacktestDataset, BacktestRun

UTC = timezone.utc
START = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
END = START + timedelta(minutes=5)


class FixtureHistoricalProvider:
    name = "fixture_real_history"

    async def fetch_candles(self, symbol, interval, start, end):
        candles = []
        for i, close in enumerate(["100", "101", "102", "103", "104"]):
            open_time = START + timedelta(minutes=i)
            close_value = Decimal(close)
            candles.append(Candle(
                symbol="BTC/USDT",
                interval="1m",
                open_time=open_time,
                close_time=open_time + timedelta(minutes=1) - timedelta(milliseconds=1),
                open=close_value - Decimal("0.2"),
                high=close_value + Decimal("0.5"),
                low=close_value - Decimal("0.5"),
                close=close_value,
                volume=Decimal("10"),
                provider=self.name,
                provider_symbol="BTCUSDT",
            ))
        return candles


@pytest.fixture
def app_db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)

    def _session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = _session
    app.dependency_overrides[get_historical_provider] = lambda: FixtureHistoricalProvider()
    yield engine
    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(engine)


@pytest.mark.asyncio
async def test_backtest_status_is_real_historical_deterministic_and_has_no_live_capability(app_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/backtests/status")

    assert response.status_code == 200
    assert response.json()["evidence_mode"] == "backtest"
    assert response.json()["historical_market_data"] == "real_only"
    assert response.json()["execution_policy"] == "backtest-v1"
    assert response.json()["deterministic"] is True
    assert response.json()["live_execution_capability"] is False
    assert response.json()["optimizer"] == "not_implemented"


@pytest.mark.asyncio
async def test_api_creates_immutable_dataset_then_runs_s1_and_returns_provenance(app_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        dataset_response = await client.post("/api/backtests/datasets", params={
            "symbol": "BTC-USDT",
            "interval": "1m",
            "start": START.isoformat(),
            "end": END.isoformat(),
        })
        assert dataset_response.status_code == 200
        dataset = dataset_response.json()
        assert dataset["status"] == "READY"
        assert len(dataset["content_sha256"]) == 64
        assert dataset["provider"] == "fixture_real_history"

        run_response = await client.post("/api/backtests/runs", params={
            "dataset_id": dataset["id"],
            "strategy_id": "S1",
            "initial_capital": "1000",
        })
        assert run_response.status_code == 200
        run = run_response.json()
        assert run["status"] == "COMPLETED"
        assert run["dataset_sha256"] == dataset["content_sha256"]
        assert run["strategy_id"] == "S1"
        assert run["strategy_version"] == "baseline-v1"
        assert run["execution_policy"] == "backtest-v1"
        assert run["trade_count"] >= 2
        assert run["final_equity"] is not None

        detail = await client.get(f"/api/backtests/runs/{run['id']}")
        assert detail.status_code == 200
        assert detail.json()["metrics"]["net_return"] == run["net_return"]
        assert detail.json()["dataset"]["content_sha256"] == dataset["content_sha256"]
        assert detail.json()["trade_count"] == run["trade_count"]


@pytest.mark.asyncio
async def test_run_rejects_missing_dataset_and_unknown_strategy(app_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        missing = await client.post("/api/backtests/runs", params={"dataset_id": 999, "strategy_id": "S1"})
        assert missing.status_code == 404

        dataset_response = await client.post("/api/backtests/datasets", params={
            "symbol": "BTC-USDT", "interval": "1m", "start": START.isoformat(), "end": END.isoformat(),
        })
        unknown = await client.post("/api/backtests/runs", params={
            "dataset_id": dataset_response.json()["id"], "strategy_id": "S99",
        })
        assert unknown.status_code == 422


def test_startup_recovery_invalidates_interrupted_running_backtests(app_db):
    with Session(app_db) as session:
        dataset = BacktestDataset(
            symbol="BTC/USDT", interval="1m", provider="fixture",
            requested_start=START, requested_end=END, actual_start=START,
            actual_end=END - timedelta(milliseconds=1), candle_count=5,
            content_sha256="a" * 64, status="READY",
        )
        session.add(dataset); session.commit(); session.refresh(dataset)
        run = BacktestRun(
            dataset_id=dataset.id, dataset_sha256=dataset.content_sha256,
            strategy_id="S1", initial_capital=Decimal("1000"),
            fee_bps=Decimal("10"), slippage_bps=Decimal("10"), position_fraction=Decimal("0.25"),
            status="RUNNING",
        )
        session.add(run); session.commit(); session.refresh(run)

        count = recover_interrupted_runs(session)
        session.refresh(run)
        assert count == 1
        assert run.status == "INVALID"
        assert run.failure_reason == "INTERRUPTED_RESTART"

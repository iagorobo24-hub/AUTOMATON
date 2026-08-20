from decimal import Decimal

from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from app.live_execution.adapter import AdapterCapabilities, SymbolRules
from app.live_execution.policy import bootstrap_live_policy
from app.live_execution.reconciliation import reconcile_live_state
from app.live_execution.service import LiveReadinessService
from app.models import LiveCircuitBreakerEvent


class Adapter:
    def __init__(self, unexpected=False, trading=False): self.unexpected = unexpected; self.trading = trading
    def capabilities(self): return AdapterCapabilities("test", self.trading, False, False, False)
    def get_symbol_rules(self, symbol): return SymbolRules(symbol, Decimal("0.001"), Decimal("0.10"), Decimal("10"))
    def get_balances(self): return {}
    def get_open_orders(self): return []
    def lookup_order(self, client_order_id): return {"client_order_id": client_order_id} if self.unexpected else None
    def get_positions(self): return []
    def get_fills(self): return []


def _engine(): return create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)


def _prepare(session):
    bootstrap_live_policy(session)
    LiveReadinessService(session, Adapter()).prepare_intent(
        candidate_id=1, source_event_id="cycle-r", symbol="BTC/USDT", side="BUY",
        quantity=Decimal("0.001"), reference_price=Decimal("10000"),
        projected_symbol_exposure=Decimal("10"), projected_portfolio_exposure=Decimal("10"), deployable_capital=Decimal("10"),
    )


def test_clean_reconciliation_for_phase10_read_only_state():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        _prepare(session)
        result = reconcile_live_state(session, Adapter())
        assert result.status == "CLEAN"
        assert result.reason_code == "MATCHED_READ_ONLY_STATE"


def test_unexpected_venue_state_fails_closed_and_trips_breaker():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        _prepare(session)
        result = reconcile_live_state(session, Adapter(unexpected=True))
        assert result.status == "RECOVERY_REQUIRED"
        event = session.exec(select(LiveCircuitBreakerEvent)).first()
        assert event is not None
        assert event.event_type == "RECONCILIATION_BLOCK"

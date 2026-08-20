from decimal import Decimal

from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from app.live_execution.adapter import AdapterCapabilities, SymbolRules
from app.live_execution.reconciliation import reconcile_live_state
from app.models import LiveCircuitBreakerEvent, LiveOrderIntent, LiveOrderRecord


class Adapter:
    def __init__(self, *, lookup=False, trading=False, open_orders=None, positions=None, fills=None):
        self.lookup = lookup
        self.trading = trading
        self.open_orders = open_orders or []
        self.positions = positions or []
        self.fills = fills or []

    def capabilities(self): return AdapterCapabilities("test", self.trading, False, False, False)
    def get_symbol_rules(self, symbol): return SymbolRules(symbol, Decimal("0.001"), Decimal("0.10"), Decimal("10"))
    def get_balances(self): return {}
    def get_open_orders(self): return self.open_orders
    def lookup_order(self, client_order_id): return {"client_order_id": client_order_id} if self.lookup else None
    def get_positions(self): return self.positions
    def get_fills(self): return self.fills


def _engine(): return create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)


def _prepared_intent(session):
    intent = LiveOrderIntent(
        candidate_id=1,
        client_order_id="live:test-client",
        intent_fingerprint="a" * 64,
        source_event_id="cycle-r",
        symbol="BTC/USDT",
        side="BUY",
        quantity=Decimal("0.001"),
        reference_price=Decimal("10000"),
        requested_notional=Decimal("10"),
        projected_symbol_exposure=Decimal("10"),
        projected_portfolio_exposure=Decimal("10"),
        status="PREPARED",
        reason_code="OK",
    )
    session.add(intent); session.commit(); session.refresh(intent)
    return intent


def test_clean_reconciliation_for_phase10_read_only_state():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        _prepared_intent(session)
        result = reconcile_live_state(session, Adapter())
        assert result.status == "CLEAN"
        assert result.reason_code == "MATCHED_READ_ONLY_STATE"


def test_unexpected_lookup_state_fails_closed_and_trips_breaker():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        _prepared_intent(session)
        result = reconcile_live_state(session, Adapter(lookup=True))
        assert result.status == "RECOVERY_REQUIRED"
        event = session.exec(select(LiveCircuitBreakerEvent)).first()
        assert event is not None
        assert event.event_type == "RECONCILIATION_BLOCK"


def test_any_unexpected_open_order_position_or_fill_fails_closed():
    for adapter in (
        Adapter(open_orders=[{"id": "external-order"}]),
        Adapter(positions=[{"symbol": "BTC/USDT", "quantity": "0.1"}]),
        Adapter(fills=[{"id": "external-fill"}]),
    ):
        engine = _engine(); SQLModel.metadata.create_all(engine)
        with Session(engine) as session:
            _prepared_intent(session)
            result = reconcile_live_state(session, adapter)
            assert result.status == "RECOVERY_REQUIRED"
            assert "UNEXPECTED_VENUE_STATE" == result.reason_code


def test_impossible_transmitted_live_order_record_fails_closed_without_replay():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        intent = _prepared_intent(session)
        session.add(LiveOrderRecord(
            intent_id=intent.id,
            client_order_id=intent.client_order_id,
            venue_order_id="venue-1",
            status="SUBMITTED",
        ))
        session.commit()
        result = reconcile_live_state(session, Adapter())
        assert result.status == "RECOVERY_REQUIRED"
        stored = session.exec(select(LiveOrderRecord)).first()
        assert stored.status == "SUBMITTED"

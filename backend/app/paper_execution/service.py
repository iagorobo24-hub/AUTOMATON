from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlmodel import Session, select

from app.accounting.service import AccountingError, AccountingService
from app.market_data.contracts import Quote
from app.models.accounting import Account, Fill, Order
from app.models.paper_execution import PaperExecution


ZERO = Decimal("0")
BPS_DENOMINATOR = Decimal("10000")


class PaperExecutionError(ValueError):
    pass


@dataclass(frozen=True)
class PaperExecutionPolicy:
    slippage_bps: Decimal = Decimal("10")
    fee_bps: Decimal = Decimal("10")
    max_quote_age_seconds: int = 30
    max_future_skew_seconds: int = 5
    version: str = "paper-v1"

    def __post_init__(self):
        if Decimal(self.slippage_bps) < ZERO:
            raise ValueError("slippage_bps cannot be negative")
        if Decimal(self.fee_bps) < ZERO:
            raise ValueError("fee_bps cannot be negative")
        if self.max_quote_age_seconds <= 0:
            raise ValueError("max_quote_age_seconds must be positive")
        if self.max_future_skew_seconds < 0:
            raise ValueError("max_future_skew_seconds cannot be negative")
        if not self.version.strip():
            raise ValueError("policy version is required")


@dataclass(frozen=True)
class PaperExecutionResult:
    execution_id: int
    order_id: int
    fill_id: int
    account_id: int
    symbol: str
    side: str
    quantity: Decimal
    market_price: Decimal
    fill_price: Decimal
    fee: Decimal
    provider: str
    observed_at: datetime
    policy_version: str


class PaperExecutionService:
    """Deterministic virtual execution against already-validated real quotes.

    Phase 3 intentionally accepts operator-originated requests only. Strategy
    automation remains disconnected until the independent Risk phase exists.
    This service has no exchange credentials, account APIs or Live adapter.
    """

    def __init__(
        self,
        session: Session,
        *,
        policy: PaperExecutionPolicy | None = None,
        clock=None,
    ):
        self.session = session
        self.policy = policy or PaperExecutionPolicy()
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self.accounting = AccountingService(session)

    def _now_utc(self) -> datetime:
        value = self._clock()
        if value.tzinfo is None:
            raise PaperExecutionError("execution clock must be timezone-aware")
        return value.astimezone(timezone.utc)

    def _validate_quote(self, symbol: str, quote: Quote, now: datetime) -> str:
        canonical = symbol.strip().upper()
        if canonical != quote.symbol:
            raise PaperExecutionError("quote symbol does not match requested symbol")
        if quote.evidence_mode != "real":
            raise PaperExecutionError("Paper execution requires real market evidence")
        if not quote.provider.strip() or not quote.provider_symbol.strip():
            raise PaperExecutionError("quote provider provenance is required")

        age = now - quote.observed_at
        if age > timedelta(seconds=self.policy.max_quote_age_seconds):
            raise PaperExecutionError("real market quote is stale")
        if age < -timedelta(seconds=self.policy.max_future_skew_seconds):
            raise PaperExecutionError("real market quote is future-dated")
        return canonical

    def _fill_price(self, side: str, market_price: Decimal) -> Decimal:
        slippage = Decimal(self.policy.slippage_bps) / BPS_DENOMINATOR
        if side == "BUY":
            return market_price * (Decimal("1") + slippage)
        return market_price * (Decimal("1") - slippage)

    def execute_market_order(
        self,
        *,
        account_id: int,
        symbol: str,
        side: str,
        quantity: Decimal,
        quote: Quote,
        origin: str = "operator",
    ) -> PaperExecutionResult:
        if origin != "operator":
            raise PaperExecutionError(
                "Phase 3 accepts operator orders only; automated execution waits for Risk"
            )
        side = side.strip().upper()
        if side not in {"BUY", "SELL"}:
            raise PaperExecutionError("only BUY and SELL market orders are supported")
        quantity = Decimal(quantity)
        if quantity <= ZERO:
            raise PaperExecutionError("quantity must be positive")

        account = self.session.get(Account, account_id)
        if account is None:
            raise PaperExecutionError("account not found")

        now = self._now_utc()
        canonical = self._validate_quote(symbol, quote, now)
        market_price = Decimal(quote.price)
        fill_price = self._fill_price(side, market_price)
        if fill_price <= ZERO:
            raise PaperExecutionError("configured slippage produced invalid fill price")
        fee = quantity * fill_price * Decimal(self.policy.fee_bps) / BPS_DENOMINATOR

        try:
            order = self.accounting.create_order(account_id, canonical, side, quantity)
        except AccountingError as exc:
            raise PaperExecutionError(str(exc)) from exc

        execution = PaperExecution(
            account_id=account.id,
            agent_id=account.agente_id,
            order_id=order.id,
            symbol=canonical,
            side=side,
            requested_quantity=quantity,
            origin=origin,
            policy_version=self.policy.version,
            provider=quote.provider,
            provider_symbol=quote.provider_symbol,
            quote_observed_at=quote.observed_at,
            quote_received_at=quote.received_at,
            market_price=market_price,
            fill_price=fill_price,
            slippage_bps=Decimal(self.policy.slippage_bps),
            fee_bps=Decimal(self.policy.fee_bps),
            fee=fee,
            status="PENDING",
        )
        self.session.add(execution)
        self.session.commit()
        self.session.refresh(execution)

        try:
            fill = self.accounting.apply_fill(
                order.id,
                quantity=quantity,
                price=fill_price,
                fee=fee,
                observed_at=quote.observed_at,
                evidence_mode="paper",
            )
        except AccountingError as exc:
            self.session.refresh(order)
            order.status = "CANCELLED"
            order.updated_at = now
            execution.status = "REJECTED"
            execution.rejection_reason = str(exc)[:256]
            execution.updated_at = now
            self.session.add(order)
            self.session.add(execution)
            self.session.commit()
            raise PaperExecutionError(str(exc)) from exc

        execution.fill_id = fill.id
        execution.status = "FILLED"
        execution.updated_at = now
        self.session.add(execution)
        self.session.commit()
        self.session.refresh(execution)

        return PaperExecutionResult(
            execution_id=execution.id,
            order_id=order.id,
            fill_id=fill.id,
            account_id=account.id,
            symbol=canonical,
            side=side,
            quantity=quantity,
            market_price=market_price,
            fill_price=fill_price,
            fee=fee,
            provider=quote.provider,
            observed_at=quote.observed_at,
            policy_version=self.policy.version,
        )

    def recover_pending(self) -> dict[str, int]:
        """Conservatively reconcile executions left PENDING across a restart.

        A pending execution is never re-submitted. If accounting already has the
        full fill, the provenance row is linked to it. If no fill exists, the
        order is cancelled. Ambiguous partial state is marked for manual
        reconciliation and left financially untouched.
        """
        now = self._now_utc()
        recovered_filled = 0
        cancelled = 0
        pending = self.session.exec(
            select(PaperExecution).where(PaperExecution.status == "PENDING")
        ).all()

        for execution in pending:
            order = self.session.get(Order, execution.order_id)
            fills = self.session.exec(
                select(Fill).where(Fill.order_id == execution.order_id)
            ).all()

            if order is not None and order.status == "FILLED" and len(fills) == 1:
                execution.fill_id = fills[0].id
                execution.status = "FILLED"
                execution.updated_at = now
                self.session.add(execution)
                recovered_filled += 1
                continue

            if not fills:
                if order is not None and order.status not in {"FILLED", "CANCELLED"}:
                    order.status = "CANCELLED"
                    order.updated_at = now
                    self.session.add(order)
                execution.status = "CANCELLED"
                execution.rejection_reason = "recovered_unfilled_after_restart"
                execution.updated_at = now
                self.session.add(execution)
                cancelled += 1
                continue

            execution.status = "RECOVERY_REQUIRED"
            execution.rejection_reason = "ambiguous_partial_accounting_state"
            execution.updated_at = now
            self.session.add(execution)

        self.session.commit()
        return {"filled": recovered_filled, "cancelled": cancelled}

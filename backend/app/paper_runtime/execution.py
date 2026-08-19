import hashlib
from datetime import datetime, timezone
from decimal import Decimal

from sqlmodel import Session, select

from app.market_data.quality import MarketDataQualityError, MarketDataUnavailable
from app.market_data.service import MarketDataService
from app.models import (
    Account,
    PaperExecution,
    PaperRequest,
    PaperRuntimeAgent,
    PaperRuntimeCycle,
    PaperRuntimeEvent,
    PaperRuntimeSession,
    Position,
)
from app.paper_execution.service import PaperExecutionError, PaperExecutionService
from app.risk.bootstrap import ensure_active_risk_profile
from app.risk.service import RiskError, RiskService


ZERO = Decimal("0")
RUNTIME_POSITION_FRACTION = Decimal("0.25")
PAPER_COMPOUNDED_COST_FACTOR = Decimal("1.002001")


class PaperRuntimeExecutionError(ValueError):
    pass


def runtime_request_id(cycle: PaperRuntimeCycle) -> str:
    raw = (
        f"runtime-v1|{cycle.session_id}|{cycle.agent_id}|{cycle.symbol}|"
        f"{cycle.candle_close.isoformat()}|{cycle.signal}"
    )
    return "runtime:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _request_fingerprint(account_id: int, symbol: str, side: str, quantity: Decimal) -> str:
    normalized = format(Decimal(quantity).normalize(), "f")
    return hashlib.sha256(f"{account_id}|{symbol}|{side}|{normalized}".encode("utf-8")).hexdigest()


def _touch_cycle(session: Session, cycle: PaperRuntimeCycle, *, outcome: str, error: str | None = None) -> PaperRuntimeCycle:
    cycle.outcome = outcome
    cycle.error_detail = error[:256] if error else None
    session.add(cycle)
    attachment = session.exec(
        select(PaperRuntimeAgent).where(
            PaperRuntimeAgent.session_id == cycle.session_id,
            PaperRuntimeAgent.agent_id == cycle.agent_id,
        )
    ).first()
    if attachment is not None:
        attachment.last_outcome = outcome
        attachment.updated_at = datetime.now(timezone.utc)
        session.add(attachment)
    session.commit(); session.refresh(cycle)
    return cycle


def _mark_recovery_required(session: Session, cycle: PaperRuntimeCycle, reason: str) -> PaperRuntimeCycle:
    runtime = session.get(PaperRuntimeSession, cycle.session_id)
    if runtime is not None:
        runtime.status = "RECOVERY_REQUIRED"
        runtime.last_error = reason[:256]
        runtime.updated_at = datetime.now(timezone.utc)
        session.add(runtime)
        session.add(PaperRuntimeEvent(session_id=runtime.id, event_type="RECOVERY_REQUIRED", reason=reason[:256]))
    return _touch_cycle(session, cycle, outcome="RECOVERY_REQUIRED", error=reason)


def _completed_replay(session: Session, cycle: PaperRuntimeCycle, request: PaperRequest) -> PaperRuntimeCycle | None:
    if request.status == "RECOVERY_REQUIRED" or request.status == "PROCESSING":
        return _mark_recovery_required(session, cycle, "runtime request has ambiguous Paper recovery state")
    if request.status != "COMPLETED":
        return None
    if request.execution_id is None:
        return _touch_cycle(session, cycle, outcome="REJECTED_PAPER", error=request.error_detail or "Paper request failed")
    execution = session.get(PaperExecution, request.execution_id)
    if execution is None:
        return _mark_recovery_required(session, cycle, "runtime request points to missing Paper execution")
    cycle.paper_execution_id = execution.id
    if execution.status == "FILLED":
        return _touch_cycle(session, cycle, outcome="FILLED")
    if execution.status == "RECOVERY_REQUIRED":
        return _mark_recovery_required(session, cycle, execution.rejection_reason or "Paper recovery required")
    return _touch_cycle(session, cycle, outcome="REJECTED_PAPER", error=execution.rejection_reason or execution.status)


async def execute_runtime_cycle(
    session: Session,
    cycle_id: int,
    market_data: MarketDataService,
) -> PaperRuntimeCycle:
    cycle = session.get(PaperRuntimeCycle, cycle_id)
    if cycle is None:
        raise PaperRuntimeExecutionError("runtime cycle not found")
    if cycle.outcome not in {"INTENT_BUY", "INTENT_SELL", "FILLED", "REJECTED_RISK", "REJECTED_PAPER", "RECOVERY_REQUIRED"}:
        return cycle
    if cycle.outcome in {"FILLED", "REJECTED_RISK", "REJECTED_PAPER", "RECOVERY_REQUIRED"}:
        return cycle

    runtime = session.get(PaperRuntimeSession, cycle.session_id)
    if runtime is None or runtime.status != "RUNNING":
        raise PaperRuntimeExecutionError("runtime session is not RUNNING")
    account = session.get(Account, cycle.account_id)
    if account is None:
        return _mark_recovery_required(session, cycle, "runtime accounting account is missing")

    request_id = runtime_request_id(cycle)
    cycle.request_id = request_id
    session.add(cycle); session.commit(); session.refresh(cycle)
    existing = session.exec(select(PaperRequest).where(PaperRequest.request_id == request_id)).first()
    if existing is not None:
        replay = _completed_replay(session, cycle, existing)
        if replay is not None:
            return replay
        return _mark_recovery_required(session, cycle, "runtime request is not safely replayable")

    try:
        quote = await market_data.get_quote(cycle.symbol)
    except MarketDataUnavailable:
        return _touch_cycle(session, cycle, outcome="SKIPPED_PROVIDER_UNAVAILABLE", error="real market-data provider unavailable")
    except MarketDataQualityError:
        return _touch_cycle(session, cycle, outcome="SKIPPED_MARKET_DATA_INVALID", error="real market-data quality validation failed")

    side = "BUY" if cycle.outcome == "INTENT_BUY" else "SELL"
    positions = session.exec(
        select(Position).where(Position.account_id == account.id, Position.quantity > ZERO)
    ).all()
    current = next((position for position in positions if position.symbol == cycle.symbol), None)
    if side == "BUY":
        available = max(ZERO, Decimal(account.cash) - Decimal(account.reserved_cash))
        budget = available * RUNTIME_POSITION_FRACTION
        quantity = budget / (Decimal(quote.price) * PAPER_COMPOUNDED_COST_FACTOR)
        if quantity <= ZERO:
            return _touch_cycle(session, cycle, outcome="REJECTED_PAPER", error="no available cash for runtime BUY")
    else:
        if current is None or Decimal(current.quantity) <= ZERO:
            return _touch_cycle(session, cycle, outcome="NO_ACTION_ALREADY_FLAT")
        quantity = Decimal(current.quantity)

    request = PaperRequest(
        request_id=request_id,
        request_fingerprint=_request_fingerprint(account.id, cycle.symbol, side, quantity),
        account_id=account.id,
        status="PROCESSING",
    )
    session.add(request); session.commit(); session.refresh(request)

    market_prices: dict[str, Decimal] = {quote.symbol: Decimal(quote.price)}
    if side == "BUY":
        try:
            for position in positions:
                if position.symbol in market_prices:
                    continue
                mark = await market_data.get_quote(position.symbol)
                market_prices[mark.symbol] = Decimal(mark.price)
        except (MarketDataUnavailable, MarketDataQualityError):
            request.status = "RETRYABLE"
            request.http_status = 503
            request.error_detail = "real marks unavailable for runtime Risk evaluation"
            session.add(request); session.commit()
            return _touch_cycle(session, cycle, outcome="SKIPPED_PROVIDER_UNAVAILABLE", error=request.error_detail)

    try:
        decision = RiskService(session).evaluate(
            account_id=account.id,
            symbol=cycle.symbol,
            side=side,
            quantity=quantity,
            quote=quote,
            market_prices=market_prices,
            profile=ensure_active_risk_profile(session),
        )
    except RiskError as exc:
        request.status = "COMPLETED"; request.http_status = 409; request.error_detail = str(exc)[:256]
        session.add(request); session.commit()
        return _touch_cycle(session, cycle, outcome="REJECTED_RISK", error=str(exc))

    cycle.risk_decision_id = decision.id
    session.add(cycle); session.commit(); session.refresh(cycle)
    if decision.decision != "ALLOW":
        request.status = "COMPLETED"
        request.http_status = 409
        request.error_detail = f"Risk rejected runtime order: {decision.reason_code}"[:256]
        session.add(request); session.commit()
        return _touch_cycle(session, cycle, outcome="REJECTED_RISK", error=request.error_detail)

    try:
        result = PaperExecutionService(session).execute_market_order(
            account_id=account.id,
            symbol=cycle.symbol,
            side=side,
            quantity=quantity,
            quote=quote,
            origin="strategy_runtime",
            request=request,
            risk_decision=decision,
        )
    except PaperExecutionError as exc:
        if exc.execution_id is not None:
            request.execution_id = exc.execution_id
        request.status = "COMPLETED"
        request.http_status = 409
        request.error_detail = str(exc)[:256]
        session.add(request); session.commit()
        execution = session.get(PaperExecution, exc.execution_id) if exc.execution_id else None
        if execution is not None and execution.status == "RECOVERY_REQUIRED":
            return _mark_recovery_required(session, cycle, str(exc))
        return _touch_cycle(session, cycle, outcome="REJECTED_PAPER", error=str(exc))

    request.execution_id = result.execution_id
    request.status = "COMPLETED"
    request.http_status = 200
    request.error_detail = None
    cycle.paper_execution_id = result.execution_id
    session.add(request); session.add(cycle); session.commit()
    return _touch_cycle(session, cycle, outcome="FILLED")

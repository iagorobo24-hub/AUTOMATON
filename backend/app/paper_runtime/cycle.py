from datetime import datetime, timezone

from sqlmodel import Session, select

from app.market_data.service import MarketDataService
from app.models import (
    Account,
    Agent,
    AgentStatus,
    PaperRuntimeAgent,
    PaperRuntimeCycle,
    PaperRuntimeSession,
    Position,
)
from app.services.strategies import get_strategy


class PaperRuntimeCycleError(ValueError):
    pass


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise PaperRuntimeCycleError("runtime candle timestamps must be timezone-aware")
    return value.astimezone(timezone.utc)


async def evaluate_agent_cycle(
    session: Session,
    runtime_session_id: int,
    agent_id: int,
    market_data: MarketDataService,
    *,
    history_limit: int = 100,
) -> PaperRuntimeCycle | None:
    runtime = session.get(PaperRuntimeSession, runtime_session_id)
    if runtime is None:
        raise PaperRuntimeCycleError("runtime session not found")
    if runtime.status != "RUNNING":
        raise PaperRuntimeCycleError("runtime session is not RUNNING")

    attachment = session.exec(
        select(PaperRuntimeAgent).where(
            PaperRuntimeAgent.session_id == runtime.id,
            PaperRuntimeAgent.agent_id == agent_id,
            PaperRuntimeAgent.enabled == True,  # noqa: E712
        )
    ).first()
    if attachment is None:
        raise PaperRuntimeCycleError("agent is not enabled in runtime session")

    agent = session.get(Agent, agent_id)
    if agent is None or agent.estado != AgentStatus.ACTIVO:
        raise PaperRuntimeCycleError("runtime evaluation requires an active agent")
    account = session.exec(select(Account).where(Account.agente_id == agent.id)).first()
    if account is None:
        raise PaperRuntimeCycleError("runtime agent has no accounting account")

    candles = await market_data.get_candles(
        runtime.symbol,
        interval=runtime.interval,
        limit=history_limit,
    )
    if not candles:
        raise PaperRuntimeCycleError("real market-data history is empty")
    latest = candles[-1]
    candle_close = _utc(latest.close_time)
    existing = session.exec(
        select(PaperRuntimeCycle).where(
            PaperRuntimeCycle.session_id == runtime.id,
            PaperRuntimeCycle.agent_id == agent.id,
            PaperRuntimeCycle.candle_close == candle_close,
        )
    ).first()
    if existing is not None:
        return None
    if attachment.last_candle_close is not None and _utc(attachment.last_candle_close) >= candle_close:
        return None

    prices = [float(candle.close) for candle in candles]
    signal = get_strategy(agent.estrategia.value).calcular_señal(prices)
    position = session.exec(
        select(Position).where(
            Position.account_id == account.id,
            Position.symbol == runtime.symbol,
            Position.quantity > 0,
        )
    ).first()

    if signal == "HOLD":
        outcome = "NO_ACTION_HOLD"
    elif signal == "BUY":
        outcome = "NO_ACTION_ALREADY_LONG" if position is not None else "INTENT_BUY"
    elif signal == "SELL":
        outcome = "INTENT_SELL" if position is not None else "NO_ACTION_ALREADY_FLAT"
    else:
        raise PaperRuntimeCycleError(f"unsupported strategy signal: {signal}")

    cycle = PaperRuntimeCycle(
        session_id=runtime.id,
        agent_id=agent.id,
        account_id=account.id,
        symbol=runtime.symbol,
        interval=runtime.interval,
        candle_close=candle_close,
        signal=signal,
        outcome=outcome,
    )
    session.add(cycle)
    session.flush()
    now = datetime.now(timezone.utc)
    attachment.last_candle_close = candle_close
    attachment.last_signal = signal
    attachment.last_outcome = outcome
    attachment.last_cycle_id = cycle.id
    attachment.updated_at = now
    runtime.last_cycle_at = now
    runtime.heartbeat_at = now
    runtime.updated_at = now
    session.add(attachment)
    session.add(runtime)
    session.commit()
    session.refresh(cycle)
    return cycle

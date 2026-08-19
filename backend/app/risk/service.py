from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlmodel import Session, select

from app.accounting.integrity import AccountingIntegrityService
from app.accounting.service import AccountingError, AccountingService
from app.market_data.contracts import Quote
from app.models import Agent, AgentStatus
from app.models.accounting import Account, Position
from app.models.paper_execution import PaperExecution
from app.models.risk import RiskDecision, RiskProfile
from app.risk.bootstrap import ensure_active_risk_profile

ZERO = Decimal("0")
ONE = Decimal("1")
PAPER_COST_RESERVE = Decimal("0.002")  # 10 bps slippage + 10 bps fee


class RiskError(ValueError):
    pass


class RiskService:
    """Persistent, deterministic, fail-closed Paper risk authorization."""

    def __init__(self, session: Session, *, clock=None):
        self.session = session
        self.accounting = AccountingService(session)
        self.integrity = AccountingIntegrityService(session)
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def _now(self) -> datetime:
        value = self._clock()
        if value.tzinfo is None:
            raise RiskError("risk clock must be timezone-aware")
        return value.astimezone(timezone.utc)

    def _persist(
        self,
        *,
        account: Account,
        agent: Agent,
        profile: RiskProfile,
        symbol: str,
        side: str,
        quantity: Decimal,
        quote: Quote,
        requested_notional: Decimal,
        equity: Decimal,
        total_exposure_before: Decimal,
        projected_total_exposure: Decimal,
        symbol_exposure_before: Decimal,
        projected_symbol_exposure: Decimal,
        open_positions_before: int,
        projected_open_positions: int,
        drawdown_pct: Decimal,
        decision: str,
        reason_code: str,
        reason: str,
    ) -> RiskDecision:
        item = RiskDecision(
            account_id=account.id,
            agent_id=agent.id,
            profile_id=profile.id,
            profile_version=profile.version,
            symbol=symbol,
            side=side,
            quantity=quantity,
            provider=quote.provider or "unknown",
            quote_observed_at=quote.observed_at,
            market_price=Decimal(quote.price),
            requested_notional=requested_notional,
            equity=equity,
            funded_capital=account.funded_capital,
            total_exposure_before=total_exposure_before,
            projected_total_exposure=projected_total_exposure,
            symbol_exposure_before=symbol_exposure_before,
            projected_symbol_exposure=projected_symbol_exposure,
            open_positions_before=open_positions_before,
            projected_open_positions=projected_open_positions,
            realized_pnl=account.realized_pnl,
            drawdown_pct=drawdown_pct,
            decision=decision,
            reason_code=reason_code,
            reason=reason[:256],
        )
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def evaluate(
        self,
        *,
        account_id: int,
        symbol: str,
        side: str,
        quantity: Decimal,
        quote: Quote,
        market_prices: dict[str, Decimal],
        profile: RiskProfile | None = None,
    ) -> RiskDecision:
        now = self._now()
        profile = profile or ensure_active_risk_profile(self.session)
        account = self.session.get(Account, account_id)
        if account is None:
            raise RiskError("account not found")
        agent = self.session.get(Agent, account.agente_id)
        if agent is None:
            raise RiskError("account agent not found")

        symbol = symbol.strip().upper()
        side = side.strip().upper()
        quantity = Decimal(quantity)
        price = Decimal(quote.price)
        requested_notional = quantity * price if quantity > ZERO and price > ZERO else ZERO

        positions = self.session.exec(
            select(Position).where(Position.account_id == account.id, Position.quantity > ZERO)
        ).all()
        current_position = next((p for p in positions if p.symbol == symbol), None)
        open_before = len(positions)
        symbol_before = (
            current_position.quantity * Decimal(market_prices.get(symbol, price))
            if current_position is not None
            else ZERO
        )

        # Conservative placeholders keep every rejection inspectable even before
        # a complete Accounting valuation is available.
        equity = account.cash + sum(
            (p.quantity * Decimal(market_prices[p.symbol]) for p in positions if p.symbol in market_prices),
            ZERO,
        )
        total_before = max(ZERO, equity - account.cash)
        projected_total = total_before
        projected_symbol = symbol_before
        projected_open = open_before
        if side == "BUY":
            projected_total += requested_notional
            projected_symbol += requested_notional
            if current_position is None:
                projected_open += 1
        elif side == "SELL":
            projected_total = max(ZERO, total_before - requested_notional)
            projected_symbol = max(ZERO, symbol_before - requested_notional)
            if current_position is not None and quantity >= current_position.quantity:
                projected_open = max(0, open_before - 1)

        high_water = max(account.funded_capital, account.funded_capital + account.realized_pnl)
        drawdown = ZERO if high_water <= ZERO or equity >= high_water else (high_water - equity) / high_water

        def reject(code: str, reason: str) -> RiskDecision:
            return self._persist(
                account=account, agent=agent, profile=profile, symbol=symbol, side=side,
                quantity=quantity, quote=quote, requested_notional=requested_notional,
                equity=equity, total_exposure_before=total_before,
                projected_total_exposure=projected_total,
                symbol_exposure_before=symbol_before,
                projected_symbol_exposure=projected_symbol,
                open_positions_before=open_before, projected_open_positions=projected_open,
                drawdown_pct=drawdown, decision="REJECT", reason_code=code, reason=reason,
            )

        if not profile.active:
            return reject("NO_ACTIVE_PROFILE", "risk profile is not active")
        if profile.paused:
            return reject("RISK_PAUSED", "risk circuit breaker is paused")
        if agent.estado != AgentStatus.ACTIVO:
            return reject("AGENT_INACTIVE", "Paper risk requires an active agent")
        if side not in {"BUY", "SELL"} or quantity <= ZERO or price <= ZERO:
            return reject("INVALID_ORDER", "side, quantity and price must define a positive BUY/SELL order")
        if quote.evidence_mode != "real" or not quote.provider.strip():
            return reject("NON_REAL_MARKET_DATA", "risk requires provider-provenanced real market data")
        age = now - quote.observed_at
        if age > timedelta(seconds=profile.max_quote_age_seconds):
            return reject("STALE_MARKET_DATA", "market quote is older than the active risk profile allows")
        if age < -timedelta(seconds=5):
            return reject("FUTURE_MARKET_DATA", "market quote timestamp is in the future")
        if quote.symbol != symbol:
            return reject("SYMBOL_MISMATCH", "quote symbol does not match requested symbol")
        try:
            _, quote_currency = symbol.split("/", 1)
        except ValueError:
            return reject("INVALID_SYMBOL", "symbol must use BASE/QUOTE format")
        if quote_currency.upper() != account.currency.upper():
            return reject("CURRENCY_MISMATCH", "market quote currency must match account currency")

        unresolved = self.session.exec(
            select(PaperExecution).where(
                PaperExecution.account_id == account.id,
                PaperExecution.status == "RECOVERY_REQUIRED",
            )
        ).first()
        if unresolved is not None:
            return reject("PAPER_RECOVERY_REQUIRED", "Paper execution recovery is unresolved")

        # A risk-reducing SELL must remain possible when an unrelated market mark
        # is temporarily unavailable. Structural Accounting integrity is still
        # mandatory, and the position being reduced is marked by the current real quote.
        if side == "SELL":
            issues = self.integrity.issues(account.id)
            if issues:
                return reject("ACCOUNTING_INVALID", ",".join(issues))
            if current_position is None or current_position.quantity < quantity:
                return reject("OVERSELL", "sell quantity exceeds the existing long position")
            symbol_before = current_position.quantity * price
            requested_notional = quantity * price
            projected_symbol = max(ZERO, symbol_before - requested_notional)
            projected_open = max(0, open_before - (1 if quantity == current_position.quantity else 0))
            return self._persist(
                account=account,
                agent=agent,
                profile=profile,
                symbol=symbol,
                side=side,
                quantity=quantity,
                quote=quote,
                requested_notional=requested_notional,
                equity=equity,
                total_exposure_before=total_before,
                projected_total_exposure=max(ZERO, total_before - requested_notional),
                symbol_exposure_before=symbol_before,
                projected_symbol_exposure=projected_symbol,
                open_positions_before=open_before,
                projected_open_positions=projected_open,
                drawdown_pct=drawdown,
                decision="ALLOW",
                reason_code="ALLOW",
                reason="risk-reducing SELL passed structural accounting, data and recovery gates",
            )

        if any(p.symbol not in market_prices for p in positions):
            return reject("ACCOUNTING_MARKS_INCOMPLETE", "real marks are required for every open position")
        try:
            report = self.accounting.reconcile(account.id, market_prices)
        except AccountingError as exc:
            return reject("ACCOUNTING_INVALID", str(exc))
        if not report.ok:
            return reject("ACCOUNTING_INVALID", ",".join(report.issues))

        snapshot = report.snapshot
        equity = snapshot.equity
        total_before = snapshot.exposure
        symbol_before = current_position.quantity * Decimal(market_prices[symbol]) if current_position else ZERO
        requested_notional = quantity * price
        high_water = max(account.funded_capital, account.funded_capital + account.realized_pnl)
        drawdown = ZERO if high_water <= ZERO or equity >= high_water else (high_water - equity) / high_water
        projected_total = total_before + requested_notional
        projected_symbol = symbol_before + requested_notional
        projected_open = open_before + (1 if current_position is None else 0)

        if requested_notional > profile.max_order_notional:
            return reject("MAX_ORDER_NOTIONAL", "order notional exceeds absolute risk cap")
        if equity <= ZERO or requested_notional > equity * profile.max_order_equity_pct:
            return reject("MAX_ORDER_EQUITY_PCT", "order notional exceeds equity percentage cap")
        if projected_total > equity * profile.max_total_exposure_pct:
            return reject("MAX_TOTAL_EXPOSURE", "projected total exposure exceeds risk cap")
        if projected_symbol > equity * profile.max_symbol_exposure_pct:
            return reject("MAX_SYMBOL_EXPOSURE", "projected symbol concentration exceeds risk cap")
        if projected_open > profile.max_open_positions:
            return reject("MAX_OPEN_POSITIONS", "projected open-position count exceeds risk cap")
        if account.realized_pnl < -(account.funded_capital * profile.max_realized_loss_pct):
            return reject("MAX_REALIZED_LOSS", "realized loss limit has been reached")
        if drawdown > profile.max_drawdown_pct:
            return reject("MAX_DRAWDOWN", "drawdown limit has been reached")
        if account.cash < requested_notional * (ONE + PAPER_COST_RESERVE):
            return reject("INSUFFICIENT_CASH_RESERVE", "cash cannot cover notional plus Paper cost reserve")

        return self._persist(
            account=account, agent=agent, profile=profile, symbol=symbol, side=side,
            quantity=quantity, quote=quote, requested_notional=requested_notional,
            equity=equity, total_exposure_before=total_before,
            projected_total_exposure=projected_total,
            symbol_exposure_before=symbol_before,
            projected_symbol_exposure=projected_symbol,
            open_positions_before=open_before, projected_open_positions=projected_open,
            drawdown_pct=drawdown, decision="ALLOW", reason_code="ALLOW",
            reason="order is inside risk-v1 limits",
        )

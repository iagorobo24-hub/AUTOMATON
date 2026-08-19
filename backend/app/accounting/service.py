from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

from sqlmodel import Session, select

from app.models.accounting import Account, Fill, LedgerEntry, Order, Position


ZERO = Decimal("0")


class AccountingError(ValueError):
    pass


@dataclass(frozen=True)
class PortfolioSnapshot:
    account_id: int
    cash: Decimal
    reserved_cash: Decimal
    market_value: Decimal
    realized_pnl: Decimal
    unrealized_pnl: Decimal
    fees_paid: Decimal
    equity: Decimal
    exposure: Decimal
    funded_capital: Decimal
    reconciliation_delta: Decimal


@dataclass(frozen=True)
class ReconciliationReport:
    account_id: int
    ok: bool
    issues: tuple[str, ...]
    snapshot: PortfolioSnapshot


class AccountingService:
    """Authoritative long-only accounting for future Backtest/Paper execution.

    This service records financial state only. It does not obtain market data,
    decide strategy signals, simulate fills, or place exchange orders.
    """

    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def _positive(value: Decimal, field: str) -> Decimal:
        value = Decimal(value)
        if value <= ZERO:
            raise AccountingError(f"{field} must be positive")
        return value

    @staticmethod
    def _non_negative(value: Decimal, field: str) -> Decimal:
        value = Decimal(value)
        if value < ZERO:
            raise AccountingError(f"{field} cannot be negative")
        return value

    def _account(self, account_id: int) -> Account:
        account = self.session.get(Account, account_id)
        if account is None:
            raise AccountingError("account not found")
        return account

    def _order(self, order_id: int) -> Order:
        order = self.session.get(Order, order_id)
        if order is None:
            raise AccountingError("order not found")
        return order

    def create_account(self, agente_id: int, initial_capital: Decimal) -> Account:
        initial = self._positive(initial_capital, "initial_capital")
        existing = self.session.exec(
            select(Account).where(Account.agente_id == agente_id)
        ).first()
        if existing is not None:
            raise AccountingError("agent already has an accounting account")

        account = Account(
            agente_id=agente_id,
            initial_capital=initial,
            funded_capital=initial,
            cash=initial,
        )
        self.session.add(account)
        self.session.flush()
        self.session.add(
            LedgerEntry(
                account_id=account.id,
                entry_type="INITIAL_FUNDING",
                amount=initial,
                reason="account_creation",
            )
        )
        self.session.commit()
        self.session.refresh(account)
        return account

    def deposit(self, account_id: int, amount: Decimal, *, reason: str) -> Account:
        amount = self._positive(amount, "amount")
        if not reason.strip():
            raise AccountingError("deposit reason is required")
        account = self._account(account_id)
        account.funded_capital += amount
        account.cash += amount
        account.updated_at = datetime.now(timezone.utc)
        self.session.add(
            LedgerEntry(
                account_id=account.id,
                entry_type="DEPOSIT",
                amount=amount,
                reason=reason.strip(),
            )
        )
        self.session.add(account)
        self.session.commit()
        self.session.refresh(account)
        return account

    def transfer_to_child(
        self,
        parent_account_id: int,
        child_agent_id: int,
        amount: Decimal,
        *,
        reason: str,
    ) -> tuple[Account, Account]:
        """Transfer funded liquid capital to a new child account without minting money."""
        amount = self._positive(amount, "amount")
        reason = reason.strip()
        if not reason:
            raise AccountingError("transfer reason is required")

        parent = self._account(parent_account_id)
        existing_child = self.session.exec(
            select(Account).where(Account.agente_id == child_agent_id)
        ).first()
        if existing_child is not None:
            raise AccountingError("child agent already has an accounting account")

        available_cash = parent.cash - parent.reserved_cash
        if available_cash < amount:
            raise AccountingError("insufficient available cash for child transfer")
        if parent.funded_capital < amount:
            raise AccountingError("insufficient funded capital for child transfer")

        now = datetime.now(timezone.utc)
        parent.cash -= amount
        parent.funded_capital -= amount
        parent.updated_at = now

        child = Account(
            agente_id=child_agent_id,
            currency=parent.currency,
            initial_capital=amount,
            funded_capital=amount,
            cash=amount,
            reserved_cash=ZERO,
            realized_pnl=ZERO,
            fees_paid=ZERO,
            created_at=now,
            updated_at=now,
        )
        self.session.add(parent)
        self.session.add(child)
        self.session.flush()
        self.session.add(
            LedgerEntry(
                account_id=parent.id,
                entry_type="CAPITAL_TRANSFER_OUT",
                amount=-amount,
                reason=reason,
            )
        )
        self.session.add(
            LedgerEntry(
                account_id=child.id,
                entry_type="CAPITAL_TRANSFER_IN",
                amount=amount,
                reason=reason,
            )
        )
        self.session.commit()
        self.session.refresh(parent)
        self.session.refresh(child)
        return parent, child

    def create_order(
        self,
        account_id: int,
        symbol: str,
        side: str,
        quantity: Decimal,
    ) -> Order:
        self._account(account_id)
        canonical_symbol = symbol.strip().upper()
        if not canonical_symbol or "/" not in canonical_symbol:
            raise AccountingError("symbol must be canonical, e.g. BTC/USDT")
        normalized_side = side.strip().upper()
        if normalized_side not in {"BUY", "SELL"}:
            raise AccountingError("only BUY and SELL are supported")
        quantity = self._positive(quantity, "quantity")

        order = Order(
            account_id=account_id,
            symbol=canonical_symbol,
            side=normalized_side,
            requested_quantity=quantity,
        )
        self.session.add(order)
        self.session.commit()
        self.session.refresh(order)
        return order

    def apply_fill(
        self,
        order_id: int,
        *,
        quantity: Decimal,
        price: Decimal,
        fee: Decimal,
        observed_at: datetime,
        evidence_mode: str = "paper",
    ) -> Fill:
        quantity = self._positive(quantity, "quantity")
        price = self._positive(price, "price")
        fee = self._non_negative(fee, "fee")
        if observed_at.tzinfo is None:
            raise AccountingError("observed_at must be timezone-aware")
        observed_at = observed_at.astimezone(timezone.utc)
        if evidence_mode not in {"paper", "backtest"}:
            raise AccountingError("accounting fills must be paper or backtest evidence")

        order = self._order(order_id)
        if order.status in {"FILLED", "CANCELLED"}:
            raise AccountingError("order is not fillable")
        remaining = order.requested_quantity - order.filled_quantity
        if quantity > remaining:
            raise AccountingError("fill exceeds remaining order quantity")

        account = self._account(order.account_id)
        position = self.session.exec(
            select(Position).where(
                Position.account_id == account.id,
                Position.symbol == order.symbol,
            )
        ).first()

        if order.side == "BUY":
            total_cost = quantity * price + fee
            if account.cash < total_cost:
                raise AccountingError("insufficient cash")
            old_quantity = position.quantity if position else ZERO
            old_basis = old_quantity * position.average_cost if position else ZERO
            new_quantity = old_quantity + quantity
            new_basis = old_basis + total_cost
            if position is None:
                position = Position(
                    account_id=account.id,
                    symbol=order.symbol,
                    quantity=new_quantity,
                    average_cost=new_basis / new_quantity,
                )
            else:
                position.quantity = new_quantity
                position.average_cost = new_basis / new_quantity
            account.cash -= total_cost
        else:
            if position is None or position.quantity < quantity:
                raise AccountingError("cannot sell more than the open long position")
            net_proceeds = quantity * price - fee
            realized = net_proceeds - quantity * position.average_cost
            account.cash += net_proceeds
            account.realized_pnl += realized
            position.realized_pnl += realized
            position.quantity -= quantity
            if position.quantity == ZERO:
                position.average_cost = ZERO

        account.fees_paid += fee
        now = datetime.now(timezone.utc)
        account.updated_at = now
        position.updated_at = now
        order.filled_quantity += quantity
        order.status = (
            "FILLED"
            if order.filled_quantity == order.requested_quantity
            else "PARTIALLY_FILLED"
        )
        order.updated_at = now

        fill = Fill(
            order_id=order.id,
            account_id=account.id,
            symbol=order.symbol,
            side=order.side,
            quantity=quantity,
            price=price,
            fee=fee,
            observed_at=observed_at,
            evidence_mode=evidence_mode,
        )
        self.session.add(account)
        self.session.add(order)
        self.session.add(position)
        self.session.add(fill)
        self.session.commit()
        self.session.refresh(fill)
        return fill

    def snapshot(
        self,
        account_id: int,
        market_prices: dict[str, Decimal],
    ) -> PortfolioSnapshot:
        account = self._account(account_id)
        positions = self.session.exec(
            select(Position).where(
                Position.account_id == account_id,
                Position.quantity > ZERO,
            )
        ).all()

        market_value = ZERO
        unrealized = ZERO
        for position in positions:
            if position.symbol not in market_prices:
                raise AccountingError(
                    f"missing market price for open position {position.symbol}"
                )
            price = self._positive(market_prices[position.symbol], "market_price")
            value = position.quantity * price
            market_value += value
            unrealized += value - position.quantity * position.average_cost

        equity = account.cash + market_value
        expected_equity = account.funded_capital + account.realized_pnl + unrealized
        delta = equity - expected_equity

        return PortfolioSnapshot(
            account_id=account.id,
            cash=account.cash,
            reserved_cash=account.reserved_cash,
            market_value=market_value,
            realized_pnl=account.realized_pnl,
            unrealized_pnl=unrealized,
            fees_paid=account.fees_paid,
            equity=equity,
            exposure=market_value,
            funded_capital=account.funded_capital,
            reconciliation_delta=delta,
        )

    def reconcile(
        self,
        account_id: int,
        market_prices: dict[str, Decimal],
    ) -> ReconciliationReport:
        snapshot = self.snapshot(account_id, market_prices)
        issues: list[str] = []
        account = self._account(account_id)

        if account.cash < ZERO or account.reserved_cash < ZERO:
            issues.append("negative_cash_or_reserve")
        if snapshot.reconciliation_delta != ZERO:
            issues.append("equity_identity_mismatch")

        positions = self.session.exec(
            select(Position).where(Position.account_id == account_id)
        ).all()
        if any(position.quantity < ZERO for position in positions):
            issues.append("negative_position_quantity")

        orders = self.session.exec(
            select(Order).where(Order.account_id == account_id)
        ).all()
        for order in orders:
            fill_quantity = sum(
                (
                    fill.quantity
                    for fill in self.session.exec(
                        select(Fill).where(Fill.order_id == order.id)
                    ).all()
                ),
                ZERO,
            )
            if fill_quantity != order.filled_quantity:
                issues.append("order_fill_quantity_mismatch")
                break
            if order.filled_quantity > order.requested_quantity:
                issues.append("order_overfilled")
                break

        fills = self.session.exec(
            select(Fill).where(Fill.account_id == account_id)
        ).all()
        if any(self.session.get(Order, fill.order_id) is None for fill in fills):
            issues.append("orphan_fill")

        return ReconciliationReport(
            account_id=account_id,
            ok=not issues,
            issues=tuple(issues),
            snapshot=snapshot,
        )

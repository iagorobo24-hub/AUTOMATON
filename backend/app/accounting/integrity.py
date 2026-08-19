from sqlmodel import Session, select

from app.models.accounting import Account, Fill, Order, Position


class AccountingIntegrityService:
    """Structural accounting checks that do not require market valuation.

    Used when a risk-reducing SELL must remain possible even if an unrelated
    position temporarily lacks a trustworthy real-market mark.
    """

    def __init__(self, session: Session):
        self.session = session

    def issues(self, account_id: int) -> tuple[str, ...]:
        account = self.session.get(Account, account_id)
        if account is None:
            return ("account_not_found",)

        issues: list[str] = []
        if account.cash < 0 or account.reserved_cash < 0:
            issues.append("negative_cash_or_reserve")

        positions = self.session.exec(
            select(Position).where(Position.account_id == account_id)
        ).all()
        if any(position.quantity < 0 for position in positions):
            issues.append("negative_position_quantity")

        orders = self.session.exec(
            select(Order).where(Order.account_id == account_id)
        ).all()
        for order in orders:
            fills = self.session.exec(
                select(Fill).where(Fill.order_id == order.id)
            ).all()
            fill_quantity = sum((fill.quantity for fill in fills), 0)
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

        return tuple(issues)

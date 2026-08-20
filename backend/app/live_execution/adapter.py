from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True)
class SymbolRules:
    symbol: str
    step_size: Decimal
    tick_size: Decimal
    min_notional: Decimal


@dataclass(frozen=True)
class AdapterCapabilities:
    venue: str
    trading_enabled: bool
    credentials_present: bool
    withdrawals_enabled: bool
    trade_permission: bool


class LiveExchangeAdapter(Protocol):
    """Read-only reconciliation contract for a future Live venue adapter."""

    def capabilities(self) -> AdapterCapabilities: ...
    def get_symbol_rules(self, symbol: str) -> SymbolRules | None: ...
    def get_balances(self) -> dict[str, Decimal]: ...
    def get_open_orders(self) -> list[dict]: ...
    def lookup_order(self, client_order_id: str) -> dict | None: ...
    def get_positions(self) -> list[dict]: ...
    def get_fills(self) -> list[dict]: ...


class DisabledLiveAdapter:
    """Phase 10 adapter: intentionally incapable of transmitting real orders."""

    def capabilities(self) -> AdapterCapabilities:
        return AdapterCapabilities(
            venue="disabled",
            trading_enabled=False,
            credentials_present=False,
            withdrawals_enabled=False,
            trade_permission=False,
        )

    def get_symbol_rules(self, symbol: str) -> SymbolRules | None:
        return None

    def get_balances(self) -> dict[str, Decimal]:
        return {}

    def get_open_orders(self) -> list[dict]:
        return []

    def lookup_order(self, client_order_id: str) -> dict | None:
        return None

    def get_positions(self) -> list[dict]:
        return []

    def get_fills(self) -> list[dict]:
        return []

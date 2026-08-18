"""
Trading strategies for AUTOMATON v2.
"""
from abc import ABC, abstractmethod
from typing import Literal

Signal = Literal['BUY', 'SELL', 'HOLD']


class EstrategiaBase(ABC):
    """Base class for active SQLModel trading strategies."""

    @abstractmethod
    def calcular_señal(self, historial_precios: list[float]) -> Signal:
        """Calculate BUY, SELL or HOLD from the supplied price history."""
        raise NotImplementedError


class Strategy1(EstrategiaBase):
    """Momentum simple: buy when the last three prices rise consecutively."""

    def calcular_señal(self, historial_precios: list[float]) -> Signal:
        if len(historial_precios) < 3:
            return 'HOLD'
        p1, p2, p3 = historial_precios[-3:]
        return 'BUY' if p3 > p2 > p1 else 'HOLD'


class Strategy2(EstrategiaBase):
    """Mean reversion around the last 20 prices."""

    def calcular_señal(self, historial_precios: list[float]) -> Signal:
        if len(historial_precios) < 20:
            return 'HOLD'
        precio_actual = historial_precios[-1]
        media_20 = sum(historial_precios[-20:]) / 20
        if precio_actual < media_20 * 0.98:
            return 'BUY'
        if precio_actual > media_20 * 1.02:
            return 'SELL'
        return 'HOLD'


class Strategy3(EstrategiaBase):
    """Breakout: buy when the current price exceeds the prior 10-price high."""

    def calcular_señal(self, historial_precios: list[float]) -> Signal:
        if len(historial_precios) < 11:
            return 'HOLD'
        precio_actual = historial_precios[-1]
        maximo_10 = max(historial_precios[-11:-1])
        return 'BUY' if precio_actual > maximo_10 else 'HOLD'


class Strategy4(EstrategiaBase):
    """Hybrid of S1-S3 with deterministic confirmation rules.

    BUY requires at least two component strategies to agree. SELL is accepted
    from the mean-reversion strategy only when neither momentum nor breakout is
    signalling BUY. Otherwise the hybrid remains in HOLD.
    """

    def __init__(self) -> None:
        self._components = (Strategy1(), Strategy2(), Strategy3())

    def calcular_señal(self, historial_precios: list[float]) -> Signal:
        signals = [strategy.calcular_señal(historial_precios) for strategy in self._components]
        if signals.count('BUY') >= 2:
            return 'BUY'
        if signals[1] == 'SELL' and signals[0] != 'BUY' and signals[2] != 'BUY':
            return 'SELL'
        return 'HOLD'


def get_strategy(estrategia: str) -> EstrategiaBase:
    """Return an active strategy by canonical id; never silently substitute one."""
    strategies = {
        'S1': Strategy1,
        'S2': Strategy2,
        'S3': Strategy3,
        'S4': Strategy4,
    }
    try:
        return strategies[estrategia]()
    except KeyError as exc:
        raise ValueError(f"Unknown strategy: {estrategia}") from exc

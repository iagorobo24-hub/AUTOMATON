"""
Trading strategies for AUTOMATON v2
"""
from abc import ABC, abstractmethod
from typing import Literal


class EstrategiaBase(ABC):
    """Base class for trading strategies"""
    
    @abstractmethod
    def calcular_señal(self, historial_precios: list[float]) -> Literal['BUY', 'SELL', 'HOLD']:
        """
        Calculate trading signal based on price history
        
        Args:
            historial_precios: List of historical prices (most recent last)
            
        Returns:
            'BUY', 'SELL', or 'HOLD'
        """
        pass


class Strategy1(EstrategiaBase):
    """
    Momentum simple: compra si últimos 3 precios suben consecutivamente
    """
    def calcular_señal(self, historial_precios: list[float]) -> Literal['BUY', 'SELL', 'HOLD']:
        if len(historial_precios) < 3:
            return 'HOLD'
        
        # Últimos 3 precios
        p1, p2, p3 = historial_precios[-3], historial_precios[-2], historial_precios[-1]
        
        # Si suben consecutivamente → BUY
        if p3 > p2 > p1:
            return 'BUY'
        
        return 'HOLD'


class Strategy2(EstrategiaBase):
    """
    Mean reversion: compra si precio bajo media, vende si subió
    """
    def calcular_señal(self, historial_precios: list[float]) -> Literal['BUY', 'SELL', 'HOLD']:
        if len(historial_precios) < 20:
            return 'HOLD'
        
        precio_actual = historial_precios[-1]
        media_20 = sum(historial_precios[-20:]) / 20
        
        # Si precio < media * 0.98 → BUY (barato, debe revertir)
        if precio_actual < media_20 * 0.98:
            return 'BUY'
        
        # Si precio > media * 1.02 → SELL (caro, debe revertir)
        if precio_actual > media_20 * 1.02:
            return 'SELL'
        
        return 'HOLD'


class Strategy3(EstrategiaBase):
    """
    Breakout: compra si rompe máximo de últimas 10 velas
    """
    def calcular_señal(self, historial_precios: list[float]) -> Literal['BUY', 'SELL', 'HOLD']:
        if len(historial_precios) < 11:
            return 'HOLD'
        
        precio_actual = historial_precios[-1]
        
        # Máximo de las últimas 10 velas (excluyendo actual)
        maximo_10 = max(historial_precios[-11:-1])
        
        # Si precio actual rompe el máximo → BUY
        if precio_actual > maximo_10:
            return 'BUY'
        
        return 'HOLD'


def get_strategy(estrategia: str) -> EstrategiaBase:
    """Factory function to get strategy instance by name"""
    strategies = {
        'S1': Strategy1(),
        'S2': Strategy2(),
        'S3': Strategy3(),
    }
    return strategies.get(estrategia, Strategy1())

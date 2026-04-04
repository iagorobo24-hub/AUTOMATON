"""
Technical Indicators - Pure math implementations
No external TA library needed - all calculations from scratch
"""

import math
from typing import List, Dict, Optional


def ema(data: List[float], period: int) -> List[float]:
    """Exponential Moving Average"""
    if len(data) < period:
        return []
    multiplier = 2 / (period + 1)
    ema_values = []
    sma = sum(data[:period]) / period
    ema_values.append(sma)
    for price in data[period:]:
        ema_val = (price - ema_values[-1]) * multiplier + ema_values[-1]
        ema_values.append(ema_val)
    return ema_values


def sma(data: List[float], period: int) -> List[float]:
    """Simple Moving Average"""
    if len(data) < period:
        return []
    return [sum(data[i : i + period]) / period for i in range(len(data) - period + 1)]


def rsi(closes: List[float], period: int = 14) -> Optional[float]:
    """Relative Strength Index - returns latest value"""
    if len(closes) < period + 1:
        return None
    gains = []
    losses = []
    for i in range(1, len(closes)):
        diff = closes[i] - closes[i - 1]
        gains.append(max(0, diff))
        losses.append(max(0, -diff))
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def rsi_series(closes: List[float], period: int = 14) -> List[float]:
    """RSI for each point in series"""
    if len(closes) < period + 1:
        return []
    results = []
    for i in range(period + 1, len(closes) + 1):
        window = closes[:i]
        val = rsi(window, period)
        if val is not None:
            results.append(val)
    return results


def atr(
    highs: List[float], lows: List[float], closes: List[float], period: int = 14
) -> Optional[float]:
    """Average True Range - returns latest value"""
    if len(highs) < period + 1:
        return None
    true_ranges = []
    for i in range(1, len(highs)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i] - closes[i - 1]),
        )
        true_ranges.append(tr)
    if len(true_ranges) < period:
        return None
    return sum(true_ranges[-period:]) / period


def macd(closes: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
    """MACD indicator"""
    if len(closes) < slow + signal:
        return {"macd": 0, "signal": 0, "histogram": 0}
    ema_fast = ema(closes, fast)
    ema_slow = ema(closes, slow)
    offset = len(ema_slow) - len(ema_fast)
    macd_line = [
        ema_fast[i - offset] - ema_slow[i] for i in range(offset, len(ema_slow))
    ]
    if len(macd_line) < signal:
        return {"macd": macd_line[-1] if macd_line else 0, "signal": 0, "histogram": 0}
    signal_line = ema(macd_line, signal)
    histogram = macd_line[-1] - signal_line[-1] if signal_line else 0
    return {
        "macd": macd_line[-1] if macd_line else 0,
        "signal": signal_line[-1] if signal_line else 0,
        "histogram": histogram,
        "macd_series": macd_line,
        "signal_series": signal_line,
        "histogram_series": [
            macd_line[i] - (signal_line[i] if i < len(signal_line) else 0)
            for i in range(min(len(macd_line), len(signal_line)))
        ],
    }


def bollinger_bands(
    closes: List[float], period: int = 20, std_dev: float = 2.0
) -> Dict:
    """Bollinger Bands"""
    if len(closes) < period:
        return {"upper": 0, "middle": 0, "lower": 0, "width": 0}
    sma_val = sum(closes[-period:]) / period
    variance = sum((x - sma_val) ** 2 for x in closes[-period:]) / period
    std = math.sqrt(variance)
    upper = sma_val + std_dev * std
    lower = sma_val - std_dev * std
    width = (upper - lower) / sma_val if sma_val > 0 else 0
    return {"upper": upper, "middle": sma_val, "lower": lower, "width": width}


def highest(data: List[float], period: int) -> Optional[float]:
    """Highest value in last N periods"""
    if len(data) < period:
        return None
    return max(data[-period:])


def lowest(data: List[float], period: int) -> Optional[float]:
    """Lowest value in last N periods"""
    if len(data) < period:
        return None
    return min(data[-period:])


def percentile(data: List[float], p: float) -> float:
    """Calculate percentile value"""
    if not data:
        return 0
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * (p / 100)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_data[int(k)]
    return sorted_data[int(f)] * (c - k) + sorted_data[int(c)] * (k - f)


def is_higher_highs(
    closes: List[float], highs: List[float], min_count: int = 3
) -> bool:
    """Check if last N candles form higher highs and higher lows"""
    if len(highs) < min_count + 1 or len(closes) < min_count + 1:
        return False
    for i in range(-min_count, 0):
        if highs[i] <= highs[i - 1]:
            return False
    return True


def volume_by_hour_average(
    volumes_by_hour: Dict[int, List[float]], current_hour: int
) -> float:
    """Average volume for a specific UTC hour"""
    hour_volumes = volumes_by_hour.get(current_hour, [])
    if not hour_volumes:
        return sum(sum(v) for v in volumes_by_hour.values()) / max(
            len(volumes_by_hour), 1
        )
    return sum(hour_volumes) / len(hour_volumes)

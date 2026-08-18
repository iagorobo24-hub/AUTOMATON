import pytest

from app.services.strategies import Strategy4, get_strategy


def test_s4_requires_confirmation_to_buy():
    # Rising breakout with price above the 20-sample mean: S1 + S3 BUY, S2 not BUY.
    history = [100.0] * 17 + [101.0, 102.0, 103.0]
    assert Strategy4().calcular_señal(history) == "BUY"


def test_s4_allows_mean_reversion_sell_without_bullish_confirmation():
    history = [100.0] * 19 + [110.0]
    assert Strategy4().calcular_señal(history) == "SELL"


def test_s4_holds_when_only_one_strategy_wants_to_buy():
    # S2 sees an oversold price, while S1/S3 do not confirm.
    history = [100.0] * 19 + [90.0]
    assert Strategy4().calcular_señal(history) == "HOLD"


def test_factory_returns_real_s4_and_rejects_unknown_ids():
    assert isinstance(get_strategy("S4"), Strategy4)
    with pytest.raises(ValueError, match="Unknown strategy"):
        get_strategy("S99")

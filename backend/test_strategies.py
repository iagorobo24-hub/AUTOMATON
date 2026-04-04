from app.services.binance_service import BinanceService
from app.services.strategy_alpha import AlphaMomentumRider
from app.services.strategy_beta import BetaRangeScalper
from app.services.strategy_gamma import GammaBreakoutHunter
from app.services.regime_detector import RegimeDetector

b = BinanceService()
print("=== BINANCE TESTNET ===")
print("Connected:", b.is_connected())
print("BTC:", b.get_price("BTCUSDT"))
print("ETH:", b.get_price("ETHUSDT"))
print("SOL:", b.get_price("SOLUSDT"))

print("\n=== FETCHING 1H KLINES ===")
for sym in ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
    klines = b.get_klines(sym, "1h", 200)
    print(f"{sym}: {len(klines)} candles, last close: {klines[-1]['close']}")

print("\n=== REGIME DETECTION ===")
btc_klines = b.get_klines("BTCUSDT", "1h", 200)
detector = RegimeDetector()
regime = detector.detect(btc_klines, {})
print("Regime:", regime.value)
print("Recommended:", detector.get_recommended_strategy())

print("\n=== STRATEGY ALPHA (Momentum Rider) ===")
alpha = AlphaMomentumRider()
for sym in ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
    klines = b.get_klines(sym, "1h", 200)
    price = b.get_price(sym)
    signal = alpha.evaluate(sym, klines, btc_klines, price, 1000)
    if signal:
        print(
            f"{sym}: SIGNAL! Score={signal['score']}, Entry=${signal['entry_price']:.2f}, SL=${signal['stop_loss']:.2f}"
        )
        for r in signal["reasons"]:
            print(f"  - {r}")
    else:
        print(f"{sym}: No signal")

print("\n=== STRATEGY BETA (Range Scalper) ===")
beta = BetaRangeScalper()
for sym in ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
    klines = b.get_klines(sym, "1h", 200)
    price = b.get_price(sym)
    signal = beta.evaluate(sym, klines, btc_klines, price, 1000)
    if signal:
        print(
            f"{sym}: SIGNAL! Score={signal['score']}, Entry=${signal['entry_price']:.2f}, Direction={signal['type']}"
        )
        for r in signal["reasons"]:
            print(f"  - {r}")
    else:
        print(f"{sym}: No signal")

print("\n=== STRATEGY GAMMA (Breakout Hunter) ===")
gamma = GammaBreakoutHunter()
for sym in ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
    klines = b.get_klines(sym, "1h", 200)
    price = b.get_price(sym)
    signal = gamma.evaluate(sym, klines, btc_klines, price, 1000)
    if signal:
        print(
            f"{sym}: SIGNAL! Score={signal['score']}, Entry=${signal['entry_price']:.2f}"
        )
        for r in signal["reasons"]:
            print(f"  - {r}")
    else:
        print(f"{sym}: No signal")

print("\n=== ALL TESTS COMPLETE ===")

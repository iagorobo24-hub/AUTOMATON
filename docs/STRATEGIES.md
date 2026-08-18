# Strategies

## Status model

A strategy can be:

- **Implemented**: executable code exists in the active strategy layer.
- **Test-covered**: deterministic behavioral tests exist.
- **Backtested**: evaluated on defined historical real-market datasets.
- **Paper-validated**: forward-tested on real current market data with virtual capital.
- **Live-eligible**: only after the Live gate, never implied by the previous labels.

These states must not be collapsed into words such as "optimized" or "profitable" without evidence.

## Active simple strategies

The current SQLModel runtime exposes S1-S4:

- **S1 Momentum**: simple consecutive-price momentum signal.
- **S2 Mean Reversion**: relative-to-moving-average entry/exit logic.
- **S3 Breakout**: simple recent-high breakout.
- **S4 Hybrid**: deterministic combination of S1-S3; requires confirmation for BUY and respects S2 SELL when momentum/breakout are not buying.

These are baseline strategies for exercising the platform. Their existence and tests do **not** establish financial profitability.

## Historical Alpha/Beta/Gamma material

The former documents `Alpha_Optimizada.md`, `Beta_Optimizada.md`, `Gamma_Optimizada.md` and `Analisis_Estrategias.md` contained potentially useful research ideas:

- regime/context filtering, including BTC context;
- ATR/volatility-aware sizing and exits;
- scoring instead of brittle all-or-nothing rules;
- liquidity/spread filters;
- time-based exits;
- trailing stops;
- compression/breakout detection;
- range and momentum specialization.

Those ideas are preserved here as **research hypotheses**, not verified facts. Historical percentages such as win-rate ranges, market-time-in-range claims or breakout failure rates are not accepted as project evidence because no reproducible dataset/backtest supporting them is versioned in the repository.

## Research requirements

Before promoting a research strategy:

1. specify exact inputs, timeframe and parameters;
2. implement deterministic indicators/signals;
3. add unit tests with fixed fixtures;
4. backtest using real historical data with fees/slippage;
5. report trade count, return, drawdown and robustness, not only win rate;
6. test out-of-sample or walk-forward where practical;
7. forward-test in Paper before any Live consideration.

## Parameter discipline

Hard-coded thresholds from historical documents are hypotheses until validated. Parameter changes require a new strategy/configuration version so results remain attributable.

## No hidden fallback

Unknown strategy identifiers must fail explicitly. An agent may never be labelled as one strategy while silently executing another.

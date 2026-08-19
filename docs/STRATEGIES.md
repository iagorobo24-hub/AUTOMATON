# Strategies

## Status model

A strategy can be:

- **Implemented**: executable deterministic code exists.
- **Test-covered**: deterministic behavioral tests exist.
- **Backtest-capable**: the current Phase 5 runner can evaluate it reproducibly.
- **Backtested**: at least one valid persisted real historical run exists for an explicit dataset/configuration.
- **Paper-validated**: sufficient forward Paper evidence exists under explicit criteria.
- **Live-eligible**: only after the Live gate and explicit authorization.

These states are not interchangeable. `Backtest-capable` does **not** mean `Backtested`, and a positive Backtest does not automatically mean `profitable`, `optimized` or `validated`.

## Active S1-S4 baselines

The active strategy layer exposes:

- **S1 Momentum**: BUY when the latest three supplied prices rise consecutively; otherwise HOLD.
- **S2 Mean Reversion**: uses the latest 20 prices; BUY below 98% of the mean, SELL above 102%, otherwise HOLD.
- **S3 Breakout**: BUY when the current price exceeds the prior 10-price high; otherwise HOLD.
- **S4 Hybrid**: deterministic combination of S1-S3; BUY requires at least two BUY signals, while S2 SELL is accepted only when S1/S3 are not buying.

Phase 5 consumes these implementations **unchanged** through `get_strategy()` and identifies them as strategy evidence version `baseline-v1`.

The runner does not add strategy-specific exits. Consequently S1/S3 can remain long until `DATASET_END_EXIT` because their current algorithms do not emit SELL. That outcome is part of evaluating the baseline honestly, not something Phase 5 should silently “fix”.

## Phase 5 evaluation discipline

Backtest execution uses:

- immutable real historical dataset SHA;
- close history through candle `t` for signal computation;
- execution no earlier than candle `t+1` open;
- explicit persisted fee/slippage/allocation assumptions;
- isolated long-only financial state;
- explicit final dataset liquidation;
- persisted trades/equity/metrics.

Phase 5 must not change S1-S4 thresholds after seeing their evaluated-period outcome.

Until actual real-provider runs execute, S1-S4 are **Backtest-capable but performance-unobserved** under the new evidence contract.

## Historical Alpha/Beta/Gamma material

Former Alpha/Beta/Gamma material contains research hypotheses such as:

- regime/context filtering;
- ATR/volatility-aware sizing/exits;
- scoring;
- liquidity/spread filters;
- time exits;
- trailing stops;
- compression/breakout detection;
- range/momentum specialization.

Historical percentages from those documents remain unverified claims unless reproduced through current real-data evidence contracts.

## Research requirements

Before promoting a strategy:

1. specify exact inputs, timeframe and parameters;
2. implement deterministic signal logic;
3. add fixed-fixture tests;
4. backtest on immutable real historical data with explicit costs;
5. report return, sample size, drawdown and costs rather than only win rate;
6. use out-of-sample/walk-forward methodology where appropriate;
7. forward-test in Paper before any Live consideration.

## Parameter discipline

Parameter changes require an explicit new strategy/configuration version. Do not tune against an evaluated period and then report that same period as independent validation.

## No hidden fallback

Unknown strategy identifiers fail explicitly. A strategy label may never silently execute another implementation.

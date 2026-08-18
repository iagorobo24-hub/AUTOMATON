# Backtesting

## Purpose

Backtesting evaluates strategy behavior on historical real-market data before forward Paper testing. It is an evidence tool, not a guarantee of future returns.

## Reproducibility contract

Every run must record:

- dataset/source and time range;
- symbols/timeframe;
- strategy and parameter version;
- initial capital;
- fee model;
- slippage/fill assumptions;
- risk profile;
- code/commit identifier when practical;
- resulting metrics and trade count.

Given the same inputs, a deterministic strategy should produce the same result.

## Bias controls

The implementation must actively avoid:

- look-ahead bias;
- using incomplete future candles;
- survivorship assumptions where relevant;
- tuning and evaluating on the same period without disclosure;
- ignoring fees/slippage;
- selecting only favorable assets/periods after seeing results.

## Evaluation structure

Prefer chronological train/research and validation windows or walk-forward evaluation over one optimized in-sample result. Out-of-sample performance is required before calling a strategy promising.

## Minimum metrics

At minimum report:

- net PnL / return;
- trade count;
- win/loss counts and win rate;
- average win/loss and expectancy where meaningful;
- profit factor where meaningful;
- maximum drawdown;
- fees/costs;
- exposure/time in market;
- distribution by symbol/period when useful.

Risk-adjusted metrics such as Sharpe may be added only with clearly documented sampling and assumptions.

## Promotion gate

A backtested strategy may advance to Paper only when the dataset and assumptions are reproducible, results are not based solely on a tiny trade sample, risk is acceptable under the project criteria, and no known accounting/data-quality defect invalidates the run.

## Evidence retention

Reports should reference machine-readable run metadata rather than copy unverifiable headline numbers into strategy documentation. Historical claims without reproducible evidence remain hypotheses.

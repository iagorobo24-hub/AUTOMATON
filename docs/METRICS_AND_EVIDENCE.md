# Metrics and Evidence

## Principle

AUTOMATON is useful only if results can be traced to real inputs and explicit assumptions. A dashboard value, Backtest PASS or Research promotion is not evidence by itself.

## Evidence modes stay separate

Every financial result must identify its mode:

- synthetic;
- backtest;
- paper;
- future live.

Backtest, Paper and legacy `Trade` histories must not be merged into one undifferentiated performance curve.

## Required provenance

A valid Backtest result references immutable dataset ID/SHA-256, provider, symbol/timeframe, UTC window, strategy ID/version/source SHA, execution policy, capital/cost/allocation assumptions and run status.

A Paper result references real-time market observations, RiskDecision, PaperExecution and Accounting records. Phase 7 runtime evidence additionally links session/agent/candle cycles to those records.

## Phase 5 Backtest metrics

Completed `BacktestRun` records support initial/final equity, net PnL/return, trade/round-trip counts, wins/losses, win rate, average win/loss, expectancy, gross profit/loss, profit factor where defined, maximum drawdown, fees, exposure/time-in-market and forced exits.

Undefined values remain null. Sharpe is not part of `backtest-v1` because no sampling convention has been defined.

## Phase 8 Research evidence

`ResearchEvaluation` is a **decision snapshot**, not a new source of financial truth. It references existing Backtest and forward Paper evidence.

A `research-v1` PASS records at minimum:

- exact strategy ID/version/source SHA;
- historical Backtest run ids;
- forward Phase 7 session ids;
- worst required VALIDATION/OOS metrics used by the gate;
- unique qualifying forward closing-SELL count;
- authoritative account-level realized-PnL context;
- policy version and evaluation timestamp.

Historical comparability requires the same strategy source/configuration, symbol/timeframe, capital, execution policy, fee/slippage, allocation and historical risk-profile version.

Forward evidence is accepted only from STOPPED Phase 7 sessions on the same symbol/timeframe with matching-strategy agents and actual FILLED `PaperExecution(origin=strategy_runtime)` links. Accounts with unresolved Paper recovery or FILLED non-runtime Paper execution are rejected because current account PnL would be ambiguously attributable.

## Research labels

- **Research PASS**: this exact configuration satisfied the versioned ResearchPolicy against the referenced evidence at that time.
- **Research REJECT**: one or more explicit gates failed or evidence was missing/ambiguous.
- **PROMOTED candidate**: an operator requested promotion and a fresh evaluation passed while current source SHA still matched the historical source.

None of these labels means guaranteed profitability, statistical proof of future returns, automatic deployment, Live eligibility or production readiness.

## Reproducibility

Two Backtest runs over the same immutable dataset content and configuration should produce identical trades/equity/metrics. Research comparisons must never hide changes in source, costs or market window.

Every promotion attempt re-evaluates current evidence. An old PASS is not a reusable permission after source/evidence drift.

## Evidence language

Use conservative language:

- **Observed**: directly measured from valid persisted evidence.
- **Reproduced**: independently rerun with matching output under identical inputs/configuration.
- **Hypothesis**: trading/research idea without valid evidence.
- **Historical claim**: assertion from legacy material not revalidated under current contracts.
- **Promoted under research-v1**: passed a defined evidence gate; not a profitability guarantee.

Do not use `optimized`, `validated`, `profitable`, `safe`, `promising` or `production-ready` without an explicit criterion and supporting observed evidence.

## Invalidation

Evidence is invalid for decision-making if affected by synthetic/fabricated real-data claims, data corruption, look-ahead leakage, incorrect costs, interrupted state, source/config mismatch, recovery ambiguity or known Accounting/Paper defects.

Research also fails closed when chronological folds are incomplete/overlapping, OOS evidence is insufficient or forward PnL attribution is contaminated.

## UI/reporting rules

UI and reports must show Backtest as Backtest, Paper as Paper and Research promotion as an evidence classification. Missing metrics remain missing. Fixture tests prove software behavior, not trading performance.

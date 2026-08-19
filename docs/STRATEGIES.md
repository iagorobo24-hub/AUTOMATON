# Strategies

## Status model

A strategy can be:

- **Implemented**: executable deterministic code exists.
- **Test-covered**: deterministic behavioral tests exist.
- **Backtest-capable**: the Phase 5 runner can evaluate it reproducibly.
- **Backtested**: at least one valid persisted real historical run exists for an explicit dataset/configuration.
- **Research-evaluated**: Phase 8 has persisted a PASS/REJECT snapshot over chronological historical plus forward Paper evidence.
- **Research-promoted**: an operator requested promotion and a fresh `research-v1` evaluation passed for the exact current source/configuration.
- **Live-eligible**: only after the future Live gate and explicit authorization.

These states are not interchangeable. A positive Backtest or Research promotion does not automatically mean `profitable`, `optimized`, `safe` or future-proof.

## Active S1-S4 baselines

The active strategy layer exposes:

- **S1 Momentum**: BUY when the latest three supplied prices rise consecutively; otherwise HOLD.
- **S2 Mean Reversion**: uses the latest 20 prices; BUY below 98% of the mean, SELL above 102%, otherwise HOLD.
- **S3 Breakout**: BUY when the current price exceeds the prior 10-price high; otherwise HOLD.
- **S4 Hybrid**: deterministic combination of S1-S3; BUY requires at least two BUY signals, while S2 SELL is accepted only when S1/S3 are not buying.

Phase 5 consumes these implementations unchanged through `get_strategy()` and fingerprints the active source. Phase 7 executes the same code in forward Paper sessions. Phase 8 evaluates the resulting evidence but does not edit or tune S1-S4 automatically.

The Backtest runner does not add strategy-specific exits. S1/S3 can therefore remain long until `DATASET_END_EXIT`; that is part of evaluating the baseline honestly.

## Historical evidence discipline

Phase 5 Backtest execution uses immutable real historical datasets, next-candle execution, explicit persisted costs/allocation, isolated long-only financial state and source SHA-256 identity.

Phase 8 adds chronological research orchestration on top of those runs. A study uses repeating complete folds:

```text
TRAIN -> VALIDATION -> OOS
```

The first attached run freezes the exact strategy version/source SHA and execution assumptions. Later windows must match the same strategy source/configuration, symbol/timeframe, capital, costs, position fraction and historical risk profile and must be chronological/non-overlapping.

`research-v1` does not use TRAIN profitability as a promotion gate. VALIDATION and OOS are the holdout evidence, with OOS carrying the stricter drawdown/profit-factor/degradation checks.

## Forward Paper discipline

Historical positivity is insufficient for Research promotion.

Phase 8 also requires completed Phase 7 forward Paper evidence on the same market/timeframe:

- matching-strategy attached agents;
- persisted runtime cycles;
- unique FILLED closing SELL `PaperExecution` records with `origin=strategy_runtime`;
- positive authoritative account-level realized-PnL context;
- no unresolved Paper recovery;
- no FILLED operator/manual Paper execution contaminating that account-level PnL attribution.

Promotion additionally checks that the current strategy source SHA still matches the frozen historical SHA.

## What promotion means

A `StrategyCandidate(status=PROMOTED)` means only:

> this exact strategy/version/source fingerprint satisfied `research-v1` against explicitly referenced historical and forward evidence when the operator requested promotion.

It does not:

- mutate `services/strategies.py`;
- update a running Phase 7 session;
- auto-replicate an agent;
- prove future profitability;
- make the strategy Live-eligible.

Every promotion attempt creates a fresh evaluation. An old PASS is never silently reused after source/evidence drift.

## Historical Alpha/Beta/Gamma material

Former Alpha/Beta/Gamma material contains hypotheses such as regime/context filtering, ATR/volatility-aware sizing/exits, liquidity/spread filters, time/trailing exits and range/momentum specialization.

Historical percentages from those documents remain unverified claims until reproduced through current real-data Backtest and Research evidence contracts.

## Parameter discipline

Parameter or signal-logic changes require an explicit strategy/configuration version and a new source fingerprint. Do not tune against a window and then score the same window as independent validation.

Phase 8 deliberately has no automatic optimizer or source-mutation endpoint. New hypotheses must be implemented/reviewed explicitly before entering the same evidence pipeline.

## No hidden fallback

Unknown strategy identifiers fail explicitly. A strategy label may never silently execute another implementation.

## Current evidence limitation

The Research infrastructure is a methodology/decision boundary, not observed performance itself. Until real-provider historical and completed forward Paper studies are executed on the exact code, no S1-S4 profitability or Research PASS may be inferred from fixture tests.

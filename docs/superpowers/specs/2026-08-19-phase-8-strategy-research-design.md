# Phase 8 — Strategy Research Design

## Goal

Build a reproducible research layer that evaluates strategy configurations across chronological historical windows and forward Paper evidence without modifying S1-S4 automatically, without optimizing on the same validation window, and without enabling Live execution.

## Architectural boundary

Phase 8 adds `backend/app/strategy_research/` as a separate evidence/orchestration domain. It consumes existing Phase 5 `BacktestRun` evidence and Phase 7 `PaperRuntime`/`PaperExecution` evidence. It does not own trading balances, create exchange orders, mutate strategy source code, or replace Backtesting/Paper/Accounting/Risk.

The domain records research intent and evaluation decisions; Backtest remains historical execution truth and Paper remains forward execution truth.

## Research objects

### `ResearchPolicy`

Persistent versioned methodology contract. Initial policy: `research-v1`.

The policy defines minimum evidence and promotion gates. These limits are research rules, not profitability guarantees.

Initial gates:

- minimum 3 chronological historical evaluation windows;
- each required window must reference a `COMPLETED` Backtest run;
- each run must have `BacktestRunEvidence.strategy_code_sha256`;
- all runs in one candidate evaluation must use the same strategy id, strategy version, source SHA, execution policy, fee bps, slippage bps and position fraction;
- at least one TRAIN window, one VALIDATION window and one OOS window;
- chronological non-overlap: TRAIN ends before VALIDATION begins; VALIDATION ends before OOS begins;
- minimum 5 round trips in VALIDATION and minimum 5 in OOS;
- VALIDATION net return > 0 and expectancy > 0;
- OOS net return > 0 and expectancy > 0;
- OOS max drawdown <= 15%;
- OOS profit factor >= 1.05 when defined;
- no more than 50% relative degradation from VALIDATION net return to OOS net return when VALIDATION return is positive;
- at least one completed Phase 7 forward Paper runtime session containing the same strategy id and at least 3 FILLED closing SELL `PaperExecution` records for an attached agent using that strategy;
- aggregate forward Paper realized PnL across qualifying attached accounts > 0;
- no qualifying forward session may be `RECOVERY_REQUIRED`;
- active strategy source SHA must still equal the evaluated source SHA when promotion is requested.

Missing or ambiguous evidence fails closed.

### `ResearchStudy`

A named research experiment for one strategy/configuration family.

Fields include:

- name;
- strategy id;
- strategy version;
- policy version;
- status (`DRAFT`, `READY`, `EVALUATED`, `REJECTED`, `PROMOTED`, `ARCHIVED`);
- notes;
- timestamps.

A study does not mutate strategy implementation.

### `ResearchWindow`

Links a study to one immutable Phase 5 Backtest run and labels its role:

- `TRAIN`;
- `VALIDATION`;
- `OOS`.

The actual time window is derived from the referenced immutable `BacktestDataset`. Windows are ordered chronologically and may not overlap for promotion evaluation.

The research layer never rewrites or recomputes historical metrics.

### `ResearchEvaluation`

Immutable PASS/REJECT snapshot produced from current study evidence.

It records:

- policy version;
- strategy/source identity;
- historical run ids;
- forward session ids;
- key validation/OOS metrics;
- forward Paper close count and realized PnL;
- reason code and human-readable reason;
- timestamp.

Every promotion attempt creates a fresh evaluation. Earlier PASS evaluations cannot be reused after evidence/source drift.

### `StrategyCandidate`

Persistent promotion record for a strategy/configuration that passed a fresh evaluation.

A candidate records:

- study id;
- evaluation id;
- strategy id/version/source SHA;
- status (`PROMOTED`, `RETIRED`);
- promoted timestamp;
- optional operator note.

Promotion is manual and evidence-gated. It does **not** modify `services/strategies.py`, reconfigure runtime sessions automatically, or imply Live eligibility.

Only one active promoted candidate per exact strategy id + source SHA + strategy version is needed; duplicate promotion attempts return the existing candidate or conflict rather than creating ambiguous duplicate truth.

## Historical methodology

Phase 8 uses chronological holdout evidence rather than an optimizer.

Required ordering:

```text
TRAIN -> VALIDATION -> OOS
```

TRAIN may be used for human research/parameter ideation, but its performance is not a promotion gate except for provenance/coherence. VALIDATION is where a proposed frozen configuration is assessed. OOS is the primary historical promotion gate.

A valid comparison requires identical:

- strategy source/configuration;
- execution policy;
- fee assumptions;
- slippage assumptions;
- position fraction;
- market symbol/timeframe convention appropriate to the study.

Research evaluations must never silently combine runs from different strategy source fingerprints or cost assumptions.

## Walk-forward support

`research-v1` supports multiple repeated TRAIN/VALIDATION/OOS groups by allowing more than three windows, but the first implementation does not auto-generate or optimize those windows.

For source/static Phase 8 closure:

- windows are persisted explicitly;
- chronology and compatibility are validated;
- evaluation aggregates required VALIDATION/OOS evidence conservatively;
- no automatic parameter search exists.

Future research may add richer fold aggregation without changing the core evidence boundary.

## Forward Paper evidence

Forward validation is based on Phase 7 persisted sessions and normal Paper provenance.

A qualifying session must:

- be `STOPPED` so its observation period is complete;
- never currently be `RECOVERY_REQUIRED`;
- include an attached agent whose current strategy id matches the study;
- contain at least one persisted cycle for that agent;
- produce actual `PaperExecution(status=FILLED, origin=strategy_runtime)` records for that account;
- count closing SELL fills for round-trip evidence;
- use authoritative Accounting realized PnL for the attached account.

The first implementation uses current Account realized PnL as forward evidence context. It does not attempt to reconstruct per-session realized PnL from legacy data; if attribution is ambiguous, promotion fails closed.

Because Account realized PnL can include earlier Paper activity, Phase 8 records forward session ids and close counts and labels the PnL field as account-level forward context, not per-session attribution. A later evidence refinement may introduce per-session PnL attribution if required.

## Promotion semantics

Promotion means only:

> this exact strategy/configuration/source fingerprint satisfied `research-v1` at a specific time using explicitly referenced historical and forward Paper evidence.

Promotion does not mean:

- guaranteed profitability;
- statistical proof of future performance;
- automatic deployment;
- automatic replication;
- Live eligibility.

Promotion is rejected if the current strategy source fingerprint has changed since the historical evidence was produced.

## API

Add `/api/research`:

- `GET /status`
- `GET /policies/active`
- `POST /studies`
- `GET /studies`
- `GET /studies/{id}`
- `POST /studies/{id}/windows`
- `GET /studies/{id}/windows`
- `POST /studies/{id}/evaluate`
- `GET /studies/{id}/evaluations`
- `POST /studies/{id}/promote`
- `GET /candidates`

There is no optimizer endpoint, automatic source mutation endpoint or Live endpoint.

## UI

Settings should report `strategy_research=evidence_phase_8` and explain that promotion is evidence-gated but manual.

A small Research panel may expose studies/evaluations/candidates later, but Phase 8 does not require a strategy editor or optimizer UI. The minimum observable contract is runtime status plus API/client support.

## Recovery and persistence

All Phase 8 tables are additive for SQLite compatibility. `create_all()` can create them without adding columns to existing Phase 1-7 tables.

Research evaluations are immutable snapshots. Restart does not need to resume a long-running job because evaluation is synchronous over already persisted evidence. A partially failed transaction must not create a candidate without its evaluation.

## Tests / closure gates

Source/static closure requires authored regressions for:

- policy bootstrap;
- study/window persistence;
- chronology and non-overlap;
- mixed strategy/source/cost rejection;
- VALIDATION/OOS sample gates;
- return/expectancy/drawdown/profit-factor/degradation gates;
- forward session completeness;
- forward strategy mismatch;
- missing/ambiguous Paper evidence;
- current-source fingerprint drift;
- fresh evaluation on every promotion attempt;
- no candidate from REJECT;
- candidate persistence from PASS;
- no duplicate ambiguous candidate;
- no S1-S4 source changes;
- no optimizer/mutation/Live surface;
- runtime/API/docs coherence.

Executable certification remains separate and requires fresh exact-HEAD backend/frontend commands plus real historical and forward Paper evidence.

## Explicit exclusions

Phase 8 does not:

- change S1-S4 automatically;
- implement automatic parameter optimization;
- score and optimize on the same window;
- create new trading capital;
- change Risk/Paper/Accounting invariants;
- auto-start Phase 7 sessions;
- auto-replicate agents;
- implement or activate Live trading.

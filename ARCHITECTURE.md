# AUTOMATON Architecture

## Objective

AUTOMATON researches autonomous crypto-trading agents using **real market data and virtual capital** until explicit evidence/safety gates justify any future Live mode.

## Non-negotiable boundaries

1. Synthetic data is test-only and explicitly labelled.
2. Backtest and Paper use real market data and virtual capital.
3. Live is a separate future execution adapter.
4. Evidence preserves mode/provenance.
5. SQLModel/SQLite is the active persistence baseline.
6. Accounting is the only active Paper financial authority.
7. Every normal Paper execution requires a persisted current-profile Risk ALLOW.
8. Backtest state is isolated from Paper and uses next-candle execution.
9. Replication transfers rather than duplicates funded liquid capital.
10. Autonomous trading exists only inside explicitly started Phase 7 Paper runtime sessions.
11. Runtime restart never silently resumes an interrupted session or uncertain order.
12. Strategy Research classifies evidence; it does not mutate strategy source, optimize parameters, auto-deploy or enable Live.

## Active domains

### Market Data — Phase 1

`backend/app/market_data/` owns real current Quote/Candle contracts, provenance and quality controls. Historical Backtest access remains a separate read-only provider.

### Strategy — baseline S1-S4

`backend/app/services/strategies.py` remains baseline deterministic logic. Phase 5 fingerprints the source, Phase 7 executes it on forward candles and Phase 8 evaluates that exact fingerprint. Phase 8 never edits S1-S4 automatically.

### Risk — Phase 4

`backend/app/risk/` remains the authorization layer for both manual and autonomous Paper orders. Risk does not execute orders.

### Paper Execution — Phases 3, 4 and 7

`backend/app/paper_execution/` accepts controlled `operator` and `strategy_runtime` origins. Both require real Quote data, persisted one-time Risk ALLOW, deterministic `paper-v1` execution and Accounting mutation. Unknown origins are rejected. There is no Live exchange adapter.

### Portfolio & Accounting — Phase 2

`backend/app/accounting/` owns Account, Order, Fill, Position and LedgerEntry. Funding is separate from PnL. Phase 6 capital transfer also uses this authority.

### Backtesting — Phase 5

`backend/app/backtesting/` owns immutable historical datasets and deterministic isolated evidence. It never mutates active Paper state.

### Agent Evolution — Phase 6

`backend/app/agent_evolution/` owns evidence-aware fitness, lineage and manual replication. Runtime cycles cannot auto-replicate agents.

### Paper Runtime — Phase 7

`backend/app/paper_runtime/` owns durable autonomous Paper session orchestration. SQLite session/cycle/request/execution state is authoritative; the asyncio scheduler is only the in-process worker.

```text
new real closed candle -> S1-S4 -> intent -> Risk -> PaperExecution(strategy_runtime) -> Accounting
```

One candle is evaluated once per session/agent. Provider failure never invents data. Financial ambiguity becomes `RECOVERY_REQUIRED`, and restart never silently resumes a session or uncertain order.

### Strategy Research — Phase 8

`backend/app/strategy_research/` owns research methodology/evidence only.

Persistent records:

- `ResearchPolicy`: versioned `research-v1` methodology thresholds;
- `ResearchStudy`: one strategy research program and frozen evidence identity;
- `ResearchWindow`: explicit chronological TRAIN/VALIDATION/OOS Backtest references;
- `ResearchEvaluation`: immutable PASS/REJECT evidence snapshot;
- `StrategyCandidate`: manual promotion record for one exact strategy/version/source SHA.

#### Historical evidence flow

```text
BacktestRun + BacktestRunEvidence + BacktestDataset
                      ↓
              ResearchWindow
                      ↓
        TRAIN -> VALIDATION -> OOS
                      ↓
          research-v1 historical gate
```

The first attached Backtest freezes strategy version/source SHA, execution policy, fees, slippage and position fraction. Later windows must match those plus market symbol/timeframe, initial capital and historical risk-profile version. Windows are chronological, non-overlapping and repeat in complete TRAIN/VALIDATION/OOS folds.

`research-v1` requires positive VALIDATION/OOS return and expectancy, minimum samples, bounded OOS drawdown, sufficient profit factor when defined and limited relative degradation from VALIDATION to OOS.

#### Forward evidence flow

```text
STOPPED Phase 7 session on same market/timeframe
                      ↓
matching-strategy attached agent + runtime cycles
                      ↓
FILLED PaperExecution(origin=strategy_runtime)
                      ↓
clean Account realized-PnL context
                      ↓
research-v1 forward gate
```

The forward gate counts unique closing SELL executions and rejects unresolved Paper recovery. It also rejects qualifying accounts with any FILLED non-`strategy_runtime` Paper execution because current Account realized PnL would then be ambiguously attributable.

#### Promotion

Each promotion attempt creates a fresh ResearchEvaluation. Promotion additionally fingerprints the current active strategy source and rejects if it differs from the historical research SHA. A PASS can create one persistent StrategyCandidate for that exact strategy/version/source identity.

A candidate is **not** automatic deployment, mutation, replication, profitability proof or Live eligibility.

## Active API/UI boundary

Phase 8 mounts `/api/research/*` for status, policy, studies, windows, evaluations, manual promotion and candidates. Settings reports `strategy_research=evidence_phase_8`.

No `/api/research/optimize`, mutation or Live surface exists.

## Current runtime

`backend/app/main.py` reports:

- `runtime_mode=transition`;
- `market_data=real_contract_available`;
- `accounting=authoritative_phase_2`;
- `risk=authoritative_phase_4`;
- `paper_trading=autonomous_phase_7`;
- `backtesting=evidence_phase_5`;
- `agent_evolution=evidence_phase_6`;
- `paper_runtime=runtime_phase_7`;
- `strategy_research=evidence_phase_8`;
- `automated_trading=paper_enabled_phase_7`;
- `live_execution=disabled`.

## Verification

Static review establishes source/contract coherence only. Runtime correctness and any strategy-performance claim require fresh exact-HEAD execution plus observed historical and forward-provider evidence.

# AUTOMATON Architecture

## Objective

AUTOMATON researches autonomous crypto-trading agents using **real market data and virtual capital** until explicit evidence/safety gates justify any future Live mode.

## Non-negotiable boundaries

1. Production/Paper evidence never uses generated or mock market data.
2. Backtest and Paper use real market data and virtual capital.
3. Live is a separate future execution adapter and is currently disabled.
4. Evidence preserves mode/provenance.
5. SQLModel/SQLite is the active persistence baseline.
6. Accounting is the only active Paper financial authority.
7. Every normal Paper execution requires a persisted current-profile Risk ALLOW.
8. Backtest state is isolated from Paper and uses next-candle execution.
9. Replication transfers rather than duplicates funded liquid capital.
10. Autonomous trading exists only inside explicitly started Phase 7 Paper runtime sessions.
11. Runtime restart never silently resumes an interrupted session or uncertain order.
12. Strategy Research classifies evidence; it does not mutate strategy source, optimize parameters, auto-deploy or enable Live.
13. Phase 9 removes superseded Mongo/mock/trading implementations instead of preserving a second hidden runtime.

## Active domains

### Market Data — Phase 1

`backend/app/market_data/` owns real current Quote/Candle contracts, provenance and quality controls. Historical Backtest access remains a separate read-only provider. The removed legacy `BinanceService` and its mock fallbacks are not an alternate provider.

### Strategy — baseline S1-S4

`backend/app/services/strategies.py` is the only executable strategy service retained. Phase 5 fingerprints its source, Phase 7 executes it on forward candles and Phase 8 evaluates that exact fingerprint. Phase 9 removed the historical Alpha/Beta/Gamma/regime executables without modifying S1-S4.

### Risk — Phase 4

`backend/app/risk/` is the authorization layer for both manual and autonomous Paper orders. Risk does not execute orders. The older `risk_manager.py`/legacy router implementation was removed in Phase 9.

### Paper Execution — Phases 3, 4 and 7

`backend/app/paper_execution/` accepts controlled `operator` and `strategy_runtime` origins. Both require real Quote data, persisted one-time Risk ALLOW, deterministic `paper-v1` execution and Accounting mutation. Unknown origins are rejected. There is no Live exchange adapter.

### Portfolio & Accounting — Phase 2

`backend/app/accounting/` owns Account, Order, Fill, Position and LedgerEntry. Funding is separate from PnL. Phase 6 capital transfer also uses this authority. Removed portfolio-snapshot/trading engines are not competing financial sources.

### Backtesting — Phase 5

`backend/app/backtesting/` owns immutable historical datasets and deterministic isolated evidence. It never mutates active Paper state.

### Agent Evolution — Phase 6

`backend/app/agent_evolution/` owns evidence-aware fitness, lineage and manual replication. Runtime cycles cannot auto-replicate agents. The historical replication service was removed.

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

Historical flow:

```text
BacktestRun + BacktestRunEvidence + BacktestDataset
                      ↓
              ResearchWindow
                      ↓
        TRAIN -> VALIDATION -> OOS
                      ↓
          research-v1 historical gate
```

Forward flow:

```text
fingerprinted STOPPED Phase 7 session on same market/timeframe
                      ↓
matching-strategy attached agent + runtime cycles
                      ↓
FILLED PaperExecution(origin=strategy_runtime)
                      ↓
clean Account realized-PnL attribution
                      ↓
research-v1 forward gate
```

The first attached Backtest freezes strategy version/source SHA and execution assumptions. Later windows must remain comparable and chronological. Forward evidence requires the Phase 7 captured source fingerprint and rejects unresolved recovery or ambiguous account attribution. Every promotion attempt is a fresh evaluation; a candidate is not automatic deployment, mutation, replication, profitability proof or Live eligibility.

### Legacy boundary — Phase 9

Phase 9 physically removes the historical second architecture:

- Mongo database/injection/config/seed and Docker services;
- old auth/chat/payments/notifications/dashboard/system/simulation/trading routes;
- old Paper/trading/risk/mock/replication/registry engines;
- legacy credentialed/mock-fallback Binance service;
- executable Alpha/Beta/Gamma/regime strategy stack;
- models, dependencies, tests and unreachable frontend code used only by those subsystems.

Intentional transition records remain limited. `Agent` stays the identity/lifecycle anchor. Pre-provenance `Trade` rows remain queryable only as `legacy_unclassified` and `evidence_valid=false`; they never become Paper/Backtest/Research evidence.

## Active API/UI boundary

The backend mounts agents, quarantined trades, UI crypto browsing, Market Data, Accounting, Risk, Paper, Backtests, Evolution, Runtime and Research. The React application exposes only DashboardPro, CryptoPro, OpsMonitorPro, AgentsPage and SettingsPage routes.

No legacy simulation/system/trading/auth/payments API, Research optimizer/mutation surface or Live execution surface is mounted.

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
- `legacy_pruning=pruned_phase_9`;
- `automated_trading=paper_enabled_phase_7`;
- `live_execution=disabled`.

## Verification

Phase 9 includes static guards against reintroducing deleted backend/frontend paths, Mongo dependencies/dev infrastructure or legacy engines. Static review establishes source/contract coherence only. Runtime correctness and any strategy-performance claim require fresh exact-HEAD execution plus observed historical and forward-provider evidence.

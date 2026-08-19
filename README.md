# AUTOMATON

AUTOMATON is a local platform for developing, testing and evaluating autonomous crypto-trading agents.

## Product contract

The current product target is **autonomous Paper Trading with real market data and virtual capital**, supported by reproducible historical evidence, explicit Risk, evidence-aware agent lifecycle and disciplined Strategy Research. Synthetic/Test, Backtest, Paper and Live remain separate evidence modes.

## Current runtime

Active stack: FastAPI + SQLModel + SQLite with React/Vite.

- Synthetic `AgentEngine`: disabled from normal startup.
- Market Data: real-only, provider-neutral and fail-closed.
- Accounting: authoritative long-only financial source for active Paper state.
- Paper Execution: deterministic MARKET execution with manual `operator` and controlled `strategy_runtime` origins.
- Risk: persistent mandatory `risk-v1` authorization before every normal Paper execution.
- Backtesting: immutable real historical datasets, deterministic `backtest-v1` and strategy-source SHA-256 evidence.
- Agent Evolution: `evolution-v1` fitness, lineage/lifecycle evidence and manual non-duplicating replication.
- Paper Runtime: persistent `runtime-v1` sessions that can execute S1-S4 autonomously on new real closed candles and now capture strategy/version/source SHA at first start.
- Strategy Research: `research-v1` studies with chronological TRAIN/VALIDATION/OOS evidence, forward Phase 7 Paper provenance and manual candidate promotion.
- Automated trading: enabled **only inside explicitly started Phase 7 Paper sessions**.
- Live execution: disabled and structurally separate.

Legacy pre-provenance `Trade` rows remain excluded from valid Paper/Backtest/fitness/research evidence. Phase 7 sessions that ran before strategy-source capture existed remain readable but cannot be retroactively fingerprinted for Research promotion.

## Implemented core

### Phases 1–7

Market Data, Accounting, deterministic Paper Execution, Risk, reproducible Backtesting, evidence-aware Agent Evolution and recoverable 24/7 Paper orchestration are implemented as separate domains. S1-S4 remain baseline algorithms; infrastructure completion does not imply performance.

### Phase 8 — Strategy Research

`backend/app/strategy_research/` adds a persistent research/evidence boundary over Phase 5 and Phase 7:

```text
immutable Backtests -> TRAIN / VALIDATION / OOS
                              +
              fingerprinted stopped forward Paper
                              ↓
                       research-v1
                              ↓
                    PASS / REJECT snapshot
                              ↓
                 manual StrategyCandidate
```

`research-v1` requires, among other gates:

- complete chronological non-overlapping TRAIN/VALIDATION/OOS folds;
- identical strategy version/source SHA, market/timeframe, execution policy, capital, costs, position fraction and historical risk profile across study windows;
- at least 5 round trips in VALIDATION and OOS;
- positive VALIDATION/OOS return and expectancy;
- OOS drawdown <= 15%;
- OOS profit factor >= 1.05 when defined;
- no more than 50% relative return degradation from VALIDATION to OOS;
- stopped Phase 7 Paper evidence on the same market/timeframe;
- Phase 7 captured strategy ID/version/source SHA matching the frozen historical study identity;
- at least 3 unique FILLED `strategy_runtime` closing SELL executions;
- positive authoritative account-level realized PnL context;
- no unresolved Paper recovery;
- no FILLED execution outside the exact Research-selected forward sessions contaminating qualifying account PnL;
- current strategy source SHA still equal to the historical/forward SHA when promotion is requested.

Each promotion attempt creates a fresh evaluation. A promoted candidate is an immutable evidence classification for one exact strategy version/source SHA; it does **not** mutate S1-S4, auto-deploy a session, replicate an agent or enable Live.

## Active APIs

Phase 8 adds:

- `GET /api/research/status`
- `GET /api/research/policies/active`
- `POST /api/research/studies`
- `GET /api/research/studies`
- `GET /api/research/studies/{id}`
- `POST /api/research/studies/{id}/windows`
- `GET /api/research/studies/{id}/windows`
- `POST /api/research/studies/{id}/evaluate`
- `GET /api/research/studies/{id}/evaluations`
- `POST /api/research/studies/{id}/promote`
- `GET /api/research/candidates`

There is no Research optimizer, strategy-mutation endpoint or Live execution endpoint.

## Runtime identifiers

Current backend reports:

- `paper_trading=autonomous_phase_7`
- `paper_runtime=runtime_phase_7`
- `automated_trading=paper_enabled_phase_7`
- `agent_evolution=evidence_phase_6`
- `strategy_research=evidence_phase_8`
- `live_execution=disabled`

A Research promotion does not alter the runtime configuration automatically.

## Development order

real market data → accounting → paper execution → risk → backtesting/evidence → agent evolution → 24/7 Paper → strategy research → **legacy pruning** → live-readiness.

## Validation

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

Source/static gates are not runtime certification. Strategy promotion is not a profitability guarantee. Fresh exact-HEAD execution plus observed historical/forward evidence is required before making performance claims.

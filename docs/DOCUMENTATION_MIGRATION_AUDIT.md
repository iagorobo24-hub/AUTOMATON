# Documentation Migration Audit

This audit records what was retained from the pre-redesign documentation and why.

## Decision classes

- **RESCUE**: still valid and carried into the new source of truth.
- **HYPOTHESIS**: useful idea, but not proven by project evidence.
- **HISTORICAL**: useful only to understand previous implementation/changes.
- **DELETE**: obsolete or misleading once valid material is absorbed elsewhere.

## Source classification

| Source | Decision | Rationale |
|---|---|---|
| `README.md` | RESCUE + REWRITE | Active SQLModel/runtime facts useful; old product definition too simulator-centric. |
| `ARCHITECTURE.md` | RESCUE + REWRITE | Active boundaries useful; target architecture needed to replace transition narrative. |
| `IMPLEMENTATION_PLAN.md` | RESCUE + REWRITE | Validation discipline useful; roadmap replaced with Paper-first program. |
| `docs/ANALYSIS.md` | DELETE | Snapshot of transition state; absorbed by README/architecture/plan. |
| `docs/ARCHITECTURE.md` | DELETE | Duplicate architecture source; root `ARCHITECTURE.md` is canonical. |
| `docs/DATABASE_ARCHITECTURE.md` | RESCUE + REWRITE | SQLModel decision retained; expanded around accounting/evidence target. |
| `docs/Alpha_Optimizada.md` | HYPOTHESIS then DELETE | ATR, regime filters, scoring, trailing/time exits worth researching; performance/parameter claims are unverified. |
| `docs/Beta_Optimizada.md` | HYPOTHESIS then DELETE | Range/liquidity/relative-volatility ideas worth testing; win-rate and thresholds unverified. |
| `docs/Gamma_Optimizada.md` | HYPOTHESIS then DELETE | Compression/breakout/liquidity ideas worth testing; claimed hit rates/thresholds unverified. |
| `docs/Analisis_Estrategias.md` | HYPOTHESIS then DELETE | Useful strategy research themes; statistical claims lack reproducible repository evidence. |
| `memory/PRD.md` | HISTORICAL then DELETE | Contains useful product ideas but incorrectly marks many legacy Mongo features as DONE/current. |
| `docs/CHANGELOG.md` | HISTORICAL / KEEP | Historical record; not a source of current capability. |
| `docs/LEGACY_AUDIT.md` | HISTORICAL-TRANSITION / KEEP | Still useful while legacy code physically exists; remove after pruning is complete. |
| `GEMINI.md`, `QWEN.md` | RESCUE + REWRITE | Agent guidance remains useful but must enforce the Paper-first contract. |
| `frontend/README.md` | RESCUE + REWRITE | Tooling/routing facts useful; needs product truthfulness rules. |
| old stabilization plan under `docs/superpowers/plans/` | HISTORICAL then DELETE | Superseded by the Paper Trading redesign and roadmap. |

## Rescued product decisions

The following ideas remain part of the project because they are still coherent with the new objective:

- autonomous agents with lifecycle and lineage;
- SQLModel/SQLite as current persistence baseline;
- explicit trade/accounting history;
- real crypto market data;
- risk management and circuit breakers;
- strategy specialization and future mutation/replication;
- auditable metrics and monitoring;
- Paper before Live;
- truthfulness in UI and evidence.

## Rescued research hypotheses

These are intentionally **not** called validated:

- ATR/volatility-aware stops and sizing;
- BTC/regime context filters;
- momentum/range/breakout specialization;
- scoring systems;
- liquidity/spread filters;
- time-based exits and trailing stops;
- compression detection;
- richer Alpha/Beta/Gamma concepts.

They must earn promotion through deterministic tests, reproducible backtests and forward Paper evidence.

## Rejected claims

No historical percentage, win rate, market-regime frequency, breakout failure probability or profitability statement is retained as fact unless future project evidence reproduces it.

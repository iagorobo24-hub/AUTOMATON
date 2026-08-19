# Phase 9 — Legacy Pruning Design

## Objective

Remove superseded legacy implementations from AUTOMATON without changing the behavior of the active Phase 1–8 architecture, and prove that the remaining runtime no longer depends on Mongo, replaced trading engines, synthetic/mock production paths, dead API surfaces, or orphaned configuration/dependencies.

Phase 9 is a destructive cleanup phase, not a feature phase.

## Current baseline

Active product/runtime domains are:

- SQLModel + SQLite persistence;
- Agents / legacy Trade quarantine;
- real fail-closed Market Data;
- authoritative Accounting;
- deterministic Paper Execution;
- persistent Risk;
- reproducible Backtesting;
- Agent Evolution;
- persistent Phase 7 Paper Runtime;
- Phase 8 Strategy Research;
- active React/Vite frontend and desktop/dev tooling.

Live execution remains disabled.

The repository still contains a second historical architecture that includes Mongo services/dependencies, old simulation/Paper/trading engines, registry/mock layers, old routers and unrelated auth/chat/payments/notifications implementations.

## Core principle

Deletion is allowed only after dependency evidence shows that the candidate is not required by:

1. active runtime imports;
2. active FastAPI routes;
3. current frontend imports/API clients;
4. current tests for Phases 1–8;
5. recovery or evidence provenance paths;
6. retained development/desktop/CI tooling.

A file being unmounted from `main.py` is evidence, but not by itself sufficient proof for deletion.

## Classification

Every legacy candidate must end in one of four states:

- **ACTIVE / KEEP** — required by the current runtime or supported user-visible product.
- **TEST-ONLY / KEEP OR RELOCATE** — useful deterministic test support and prohibited from production financial/evidence paths.
- **RESEARCH REFERENCE** — only useful as a hypothesis/source of ideas; preserve concepts in documentation, not executable active architecture.
- **DELETE** — superseded and no longer referenced by any retained path.

Phase 9 must not create a broad `legacy/` graveyard. Code either has a justified retained role or is removed.

## Protected active surface

The following areas are protected from behavioral redesign during Phase 9:

- `backend/app/accounting/`;
- `backend/app/market_data/`;
- `backend/app/paper_execution/`;
- `backend/app/risk/`;
- `backend/app/backtesting/`;
- `backend/app/agent_evolution/`;
- `backend/app/paper_runtime/`;
- `backend/app/strategy_research/`;
- SQLModel models used by those domains;
- `backend/app/services/strategies.py` and baseline S1–S4 behavior;
- active agent/trade/crypto API surfaces unless audit proves a specific legacy portion is unused;
- current frontend routes/components reachable from the active application;
- recovery, idempotency and evidence contracts established in Phases 1–8.

Phase 9 may adjust imports, tests, settings and docs required by pruning, but must not change active financial semantics.

## Deletion wave 1 — superseded financial/orchestration engines

Candidates to delete after reference checks:

- `backend/app/routers/simulation.py`;
- `backend/app/routers/paper_trading.py`;
- `backend/app/routers/trading.py`;
- legacy `backend/app/routers/risk.py`;
- `backend/app/services/paper_engine.py`;
- `backend/app/services/trading_engine.py`;
- `backend/app/services/replication.py`;
- `backend/app/services/mock_engine.py`;
- `backend/app/services/registry.py`;
- `backend/app/services/portfolio_snapshot.py`.

These capabilities are already replaced by Backtesting, PaperExecution/PaperRuntime, Risk, Agent Evolution and Accounting.

Deleting them must not introduce adapter shims that preserve their old behavior.

## Deletion wave 2 — Mongo-backed inactive product subsystems

After proving no active consumers remain, remove the Mongo dependency/injection stack and inactive routers/services, including candidates such as:

- `backend/app/services/database.py`;
- `backend/app/api/deps.py`;
- legacy Mongo seed/setup code;
- inactive auth/chat/payments/notifications/dashboard/system/audit/signals/strategy-CRUD implementations;
- their dedicated Mongo-backed services/models/config where no retained consumer exists.

The exact file list is determined by the reference audit immediately before deletion. A candidate that still has a valid active consumer is not deleted merely because it was listed in an old audit document.

## Mongo dependency removal

Once the final retained Mongo consumer is removed:

- remove `motor`;
- remove `pymongo`;
- remove Mongo-only settings/environment variables;
- remove Mongo initialization/injection code;
- remove documentation implying Mongo remains an active or preserved runtime subsystem.

No empty compatibility wrapper is kept simply to preserve imports; retained imports must be migrated to the active architecture or removed with their callers.

## `binance_service.py` special case

The legacy `BinanceService` is unsafe as an active financial provider because historical behavior includes mock/generated fallback.

Before deletion:

1. identify every remaining import;
2. if an active UI/crypto route still uses it, replace only the required read-only function with the current real/fail-closed provider boundary or another already-active real data path;
3. do not copy mock fallback behavior;
4. delete `binance_service.py` when no consumer remains;
5. remove `python-binance` only if no retained code imports it.

This is migration of a dependency boundary, not redesign of Market Data.

## Synthetic `AgentEngine` special case

`services/agent_engine.py` is retained only if current deterministic tests/tooling still use it as explicit Synthetic/Test support.

If retained:

- it must remain unreachable from normal startup, Paper, Risk, Accounting, Runtime and Research evidence;
- documentation must label it TEST-ONLY;
- relocating it to a clearly test-support location is allowed if imports are updated minimally.

If no valid consumer remains, delete it.

Phase 9 must not reintroduce synthetic runtime capability merely to justify keeping this code.

## Advanced historical strategy code special case

Candidates such as:

- `strategy_alpha.py`;
- `strategy_beta.py`;
- `strategy_gamma.py`;
- `indicators.py`;
- `regime_detector.py`;

must not be promoted into the Phase 8 runtime during cleanup.

For each:

1. inspect imports and tests;
2. identify any product/research concept worth preserving;
3. document useful hypotheses in Strategy Research documentation if not already represented;
4. delete executable legacy code once no active consumer remains.

Historical performance claims remain unverified and must not be copied as evidence.

## Frontend pruning

Audit from the active `App.jsx` route/import graph.

Delete only:

- unreachable pages/components;
- API helpers for deleted endpoints;
- demo/mock financial UI that is no longer reachable or valid;
- configuration tied solely to deleted backend subsystems.

Do not redesign the visual system or active flows in Phase 9.

## Dependency/config cleanup

Dependency removal occurs after code deletion, never before.

Candidates include:

- `motor`, `pymongo` after Mongo removal;
- `PyJWT`, `passlib`, `python-multipart` if no retained auth/upload consumer remains;
- `python-binance` after legacy BinanceService removal;
- `slowapi` if no retained rate-limit consumer remains;
- other requirements/config keys only after search proves zero retained imports/usages.

Do not remove `numpy`, `pandas`, `httpx`, SQLModel/SQLite or other active dependencies without evidence.

## Tests and architecture guards

Phase 9 adds or updates regression checks so the removed architecture cannot silently return.

At minimum, exact-source tests/search gates should demonstrate:

- `app.main` does not import or initialize Mongo;
- active domains do not import `DatabaseService`;
- active financial/evidence domains do not import mock/synthetic engines;
- no legacy Paper/trading/risk routes are mounted;
- no Live execution route/adapter is introduced;
- active API route inventory remains coherent;
- S1–S4 source/behavior is unchanged;
- deleted endpoint clients are absent from active frontend imports;
- requirements/config contain no dependency/settings kept solely for deleted code.

Where executable validation is available, run all backend/frontend/build gates after each destructive wave or at minimum before final closure.

## Git/deletion safety

- Work directly on `main`, as previously authorized for this repository.
- Use incremental commits because GitHub Contents API operations are not atomic across many files.
- Before each delete, fetch the current file and confirm current references.
- Never force-push, rewrite history, merge a PR, deploy or modify Live credentials/capability.
- A failed/ambiguous reference audit stops deletion of that candidate; it does not justify guessing.

## Documentation updates

Reconcile at least:

- `docs/LEGACY_AUDIT.md`;
- `README.md`;
- `ARCHITECTURE.md`;
- `IMPLEMENTATION_PLAN.md`;
- `docs/ROADMAP.md`;
- `docs/DATABASE_ARCHITECTURE.md`;
- `GEMINI.md`;
- `QWEN.md`.

The final documentation must describe the architecture that actually remains, not historical components that were deleted.

## Explicit exclusions

Phase 9 does **not**:

- change S1–S4 algorithms or thresholds;
- change `research-v1`, `risk-v1`, `paper-v1`, `runtime-v1` or Accounting semantics;
- build replacement auth/chat/payments/notifications systems;
- create new strategies;
- optimize strategies;
- add Live exchange execution;
- add credentials/secrets;
- activate auto-replication or auto-deployment;
- perform broad unrelated refactors.

## Exit criteria

Phase 9 source/contract/static closure requires all of the following:

1. exact active runtime/import/route inventory documented;
2. every legacy candidate classified with evidence;
3. superseded engines/routers removed where no retained dependency exists;
4. Mongo stack removed if no active consumer remains;
5. legacy mock/generated financial fallback removed from production paths;
6. obsolete dependencies/settings removed after final-consumer proof;
7. dead frontend/API surfaces removed where unreachable;
8. no active Phase 1–8 contract regressed by static review;
9. `services/strategies.py` unchanged unless a purely import-path mechanical change is unavoidable and explicitly justified;
10. no Live capability introduced;
11. final exact-HEAD reference/drift audit completed;
12. documentation reconciled to the remaining source tree.

Executable certification is separate. Backend tests, frontend tests/build and relevant real-provider smoke remain required before claiming a green runtime if the environment cannot execute them.

## Expected result

After Phase 9, AUTOMATON should have one comprehensible active architecture rather than an active SQLModel system coexisting with a large unmounted Mongo/mock/trading implementation. The repository may retain a small explicitly justified TEST-ONLY or research-reference surface, but no unsupported legacy subsystem should remain merely because it is historical.

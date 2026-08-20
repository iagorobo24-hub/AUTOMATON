# AUTOMATON — Pre-Integration Acceptance Audit

**Audit date:** 2026-08-20  
**Audited implementation baseline:** `9c4f77bbf68b0d086b865581e1bcf021db593642`  
**Purpose:** decide whether the completed Phase 1–10 source/contract/static program is genuinely ready to enter integration testing.  
**Verdict:** **NO-GO** until the blocking findings below are corrected and the executable acceptance gate is observed on the corrected exact HEAD.

## 1. Acceptance standard

This audit does not treat prior phase-closure statements as proof of runtime correctness. A pre-integration GO requires all of the following to be coherent at the same exact Git state:

1. active architecture and API contracts;
2. financial/accounting/risk lifecycle invariants;
3. Market Data and historical-evidence integrity;
4. restart/recovery/idempotency behavior;
5. database referential integrity;
6. frontend actions matching actual backend semantics;
7. absence of forbidden Live/secret/order surfaces;
8. test/build harness aligned with the current architecture;
9. fresh exact-HEAD backend tests, frontend tests and frontend build;
10. no unresolved blocker whose failure would invalidate integration evidence.

Source/static review and executable certification are intentionally separate.

## 2. Verified strengths

The following were re-checked against the audited baseline and are coherent in source:

- Market Data is provider-provenanced, real-only and fail-closed for trading evidence.
- Accounting is long-only and remains the active Paper financial authority.
- Risk requires current real quotes, an active unpaused profile, accounting integrity and clean Paper recovery before normal Paper execution.
- Paper execution consumes a persisted one-time matching Risk ALLOW and has restart reconciliation instead of blind replay.
- Paper Runtime has explicit start/resume/recovery ownership, deterministic per-cycle request identity, strategy-source provenance and no process-start auto-resume.
- Backtesting is isolated from Paper, fingerprints strategy source and executes a signal no earlier than the next candle open.
- Agent Evolution conserves funded liquid capital during manual evidence-gated replication.
- Strategy Research separates TRAIN/VALIDATION/OOS and requires matching fingerprinted forward Paper evidence before promotion.
- Phase 9 removed the superseded Mongo/mock/trading runtime from active production source.
- Phase 10 keeps `live_readiness=readiness_phase_10`, `live_adapter=disabled_adapter`, `live_execution=disabled` and `real_capital_execution=disabled`.
- No active Phase 10 real-order transport or exchange-secret write path was found.
- The active strategy source S1–S4 remains the single executable strategy service.
- The repository contains a CI workflow for backend pytest, frontend Vitest and frontend build on `main` push/pull request.

These strengths do **not** override the blockers below.

## 3. Blocking findings

### B1 — Agent lifecycle can strand an open Paper position

**Classification:** confirmed functional/safety defect.  
**Severity:** blocker.

`DELETE /api/agents/{agent_id}` marks an agent `MUERTO` without first proving that the agent is flat and detached from an active/paused/recovery runtime session. Risk, however, rejects every normal Paper order when the agent is not `ACTIVO`, including a risk-reducing SELL before the SELL-specific path is reached.

Consequently, an operator can retire an agent while it still owns a long Paper position and then lose the normal Risk-authorized path to close that position.

**Required correction before GO:** lifecycle retirement must fail closed unless the agent is in a defined safe terminal state. At minimum, prove flat Accounting position state, no unresolved Paper recovery, and no runtime ownership that can continue or require recovery. Do not solve this by weakening Risk's active-agent gate.

**Required regression:** create/open-position/runtime-state cases must prove an unsafe retirement is rejected and a safe flat detached retirement remains allowed.

### B2 — Historical dataset creation can admit a not-yet-closed current candle

**Classification:** confirmed evidence-integrity defect.  
**Severity:** blocker.

The historical dataset API accepts an `end` in the future. The historical Binance provider filters a kline only against the requested `[start, end]` range and does not require `close_time <= now`. A future end can therefore make the currently open kline eligible for persistence because its scheduled close time can still be earlier than the requested future end.

That violates the immutable historical-evidence contract: a BacktestDataset must contain only completed historical candles.

**Required correction before GO:** reject future historical windows and/or enforce a provider/dataset-level closed-candle boundary against an explicit UTC clock. The invariant must be guaranteed below the API surface as well, not only by frontend behavior.

**Required regression:** a future `end` and an in-progress kline must fail closed; the same completed kline must become eligible only after its close time.

### B3 — SQLite foreign-key enforcement is not enabled

**Classification:** confirmed persistence-integrity defect.  
**Severity:** blocker.

The SQLModel models declare many foreign keys across Accounting, Risk, Paper, Runtime, Research and Live Readiness, but the active SQLite engine does not install `PRAGMA foreign_keys=ON` for each connection. SQLite foreign-key enforcement is disabled by default.

Therefore the schema currently does not guarantee referential integrity at the storage layer. Orphan/mismatched records can survive if a bug, maintenance action or unexpected code path bypasses application-level checks. This directly weakens recovery and evidence provenance.

**Required correction before GO:** enable SQLite FK enforcement on every application/test connection through the SQLAlchemy engine connection hook (or an equivalent guaranteed mechanism), then verify existing/fresh databases for violations before treating the constraint as authoritative.

**Required regression:** inserting representative orphan Accounting/Paper/Runtime/Research rows must fail under the actual configured engine, and normal valid relationships must continue to work.

## 4. Non-blocking but pre-integration cleanup findings

### C1 — Legacy test fixtures survived Phase 9

`backend/tests/conftest.py` still contains unused Mongo/JWT/legacy-agent/auto-replication fixtures. Code search found no current consumers for these fixtures. They do not currently prove a collection failure because the stale `jwt` import is inside an unused fixture, but they contradict the current architecture and make the test harness harder to trust.

**Recommendation:** remove unused legacy fixtures before executable acceptance so test support describes the product being tested.

### C2 — Crypto UI `QUICK DEPLOY` does not perform a market deployment

The terminal's `QUICK DEPLOY` button only creates a generic S1 agent/account and embeds the selected symbol in the name. It does not create or start a Paper Runtime session and does not bind the agent to the selected market/timeframe.

**Recommendation:** rename/remove the action or implement a deliberately specified runtime-deployment workflow later. Do not present agent creation as market deployment during integration tests.

### C3 — Dashboard header asserts `SYSTEM_STATUS::OPERATIONAL` statically

The detailed Dashboard cards fail closed to unknown/N-D when APIs fail, but the page header itself always prints an operational status.

**Recommendation:** derive that label from `/health` or use a neutral heading so UI truthfulness is consistent.

### C4 — Current Market Data `limit=1000` has a boundary edge

The Binance current-candle provider requests at most 1000 rows while trying to return 1000 *closed* candles. If the response includes an unfinished current candle, only 999 closed candles may remain and the request fails closed.

**Recommendation:** either document the practical max closed-candle request as 999 or paginate/request an older boundary when 1000 closed candles are required. This is availability/ergonomics, not evidence corruption because the implementation fails closed.

### C5 — Governance/CI evidence is still weak

The repository has a sensible CI definition, but no fresh exact-HEAD test/build result was observable through the available repository status interfaces during this audit. Local checkout from the audit environment is also blocked by DNS before tests can start.

**Recommendation:** the integration acceptance run must produce retained exact-HEAD output for all mandatory commands; branch protection/check requirements can be considered after the software gate is green.

## 5. Domain acceptance matrix

| Domain | Source/contract review | Pre-integration status |
|---|---|---|
| Market Data current | coherent, fail-closed | CONDITIONAL GO |
| Accounting | coherent static invariants | CONDITIONAL GO |
| Risk | coherent, but lifecycle interaction exposes B1 | NO-GO |
| Paper Execution | coherent recovery/idempotency contract | CONDITIONAL GO |
| Backtesting datasets | B2 allows non-closed historical evidence | NO-GO |
| Backtest execution/metrics | coherent static contract | CONDITIONAL GO |
| Agent Evolution | coherent static contract | CONDITIONAL GO |
| Paper Runtime | coherent static lifecycle/recovery | CONDITIONAL GO |
| Strategy Research | coherent static evidence gates | CONDITIONAL GO |
| Persistence/SQLite | B3: FK enforcement not active | NO-GO |
| Live Readiness | separate, non-executing, real capital disabled | GO for readiness-only scope |
| Frontend/API semantics | usable but C2/C3 need cleanup | CONDITIONAL GO |
| Test/build harness | CI commands defined; fresh execution unobserved | NOT CERTIFIED |

`CONDITIONAL GO` means no blocker was found in that isolated domain, but it cannot make the project integration-ready while a cross-domain blocker remains.

## 6. Mandatory acceptance gate after corrections

The corrected exact HEAD must pass **all** of the following before this audit can change to GO:

```bash
# backend
cd backend
python -m pytest tests/ -v

# frontend
cd ../frontend
npm ci
npm test -- --run
npm run build
```

Additionally execute targeted integration/recovery checks on that same code state:

1. create agent + Accounting account;
2. fetch real Market Data and prove provider/freshness provenance;
3. Paper BUY through Risk -> PaperExecution -> Accounting;
4. verify attempted retirement with open position is blocked;
5. Paper SELL to flat and reconcile Accounting exactly;
6. safe agent retirement after flat/detached state;
7. runtime start -> one-candle idempotency -> stop;
8. simulated restart/recovery: no automatic replay/resume;
9. historical dataset with future/open candle rejected;
10. historical closed dataset -> deterministic Backtest rerun equivalence;
11. Research provenance gates reject source/session mismatch;
12. SQLite FK negative tests reject orphan records;
13. Live status proves disabled adapter/execution/real-capital and no order route;
14. frontend smoke against the same backend: Dashboard, Crypto, Ops Monitor, Agents and Settings without invented success state.

For any network/provider-dependent check, unavailable external data is an explicit blocked/skip condition, never a synthetic PASS.

## 7. Final verdict

**Current verdict: NO-GO for formal integration testing.**

The project is materially more coherent than its legacy baseline and most Phase 1–10 boundaries survive a fresh static review. However, B1, B2 and B3 are real contract violations affecting financial lifecycle, historical evidence and persistence integrity respectively. Starting integration acceptance before correcting them would risk producing test evidence on a state we already know is invalid.

The appropriate next action is a **small pre-integration remediation set**, not a Phase 11 and not a new feature cycle. Once the three blockers are fixed (plus preferably the listed cleanup items) and the exact-HEAD executable gate is observed, rerun this acceptance audit and issue either GO or another evidence-backed NO-GO.

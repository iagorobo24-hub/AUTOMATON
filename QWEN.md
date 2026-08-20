# QWEN.md — AUTOMATON Project Contract

Use `docs/PRODUCT_CONTRACT.md`, `ARCHITECTURE.md`, `docs/ROADMAP.md` and `docs/LIVE_TRADING_GATE.md` as product truth. Inspect `backend/app/main.py` before claiming runtime status.

## Objective

AUTOMATON targets autonomous Paper Trading on **real market data with virtual capital**, supported by reproducible evidence, explicit Risk/recovery gates, Strategy Research and a fail-closed future Live boundary.

## Current state

- FastAPI + SQLModel + SQLite; React/Vite.
- Phases 1–8 provide Market Data, Accounting, Paper, Risk, Backtesting, Evolution, Paper Runtime and Strategy Research.
- Phase 9 pruned Mongo/mock/legacy trading code.
- Phase 10 implements Live Readiness, not Live trading.
- Runtime: `paper_trading=autonomous_phase_7`, `paper_runtime=runtime_phase_7`, `automated_trading=paper_enabled_phase_7`, `agent_evolution=evidence_phase_6`, `strategy_research=evidence_phase_8`, `legacy_pruning=pruned_phase_9`, `live_readiness=readiness_phase_10`, `live_adapter=disabled_adapter`, `live_execution=disabled`, `real_capital_execution=disabled`.

## Phase 10 rules

`backend/app/live_execution/` is independent from Paper.

- `DisabledLiveAdapter` is read/reconciliation only and cannot transmit orders.
- No `/api/live/orders`, buy/sell, credential-write, recovery-resolution shortcut or activation endpoint may exist.
- No real exchange secrets are stored.
- `live-v1` enforces absolute venue/hard limits and CANARY 10% rollout capital fraction.
- Quantity normalization never rounds upward.
- Symbol aliases canonicalize before deterministic intent identity.
- Prepared Live intents are deterministic/idempotent records only; they are never transmitted.
- Readiness verifies the promoted Research Study/PASS Evaluation/PROMOTED Candidate chain and matching strategy/version/source identity.
- Current source SHA must still match the candidate.
- Market Data must be real/fail-closed and non-executing.
- Risk must be active and Paper recovery clean.
- Any unexplained venue order/position/fill, impossible transmitted record or trading-enabled adapter causes `RECOVERY_REQUIRED` + circuit breaker; never replay.
- Positive readiness requires latest reconciliation exactly CLEAN and no unresolved historical Live recovery.
- Persistent emergency-stop changes are audited and clear cannot cross unresolved recovery.
- Every readiness evaluation preserves `real_capital_blocked=true`; runtime keeps `live_execution=disabled`.

`ARCHITECTURE_READY` is a technical classification only. It does not imply profitability, safety, exchange approval or permission to move real capital.

## Evidence and strategy rules

Backtest/Paper/Live evidence remain separate. Research promotion never auto-deploys. S1-S4 must not be tuned merely to satisfy readiness or evaluation gates.

## Future Live activation

A concrete exchange adapter, secret-management mechanism, evidence-backed venue recovery procedure and any real-capital activation require a new explicitly authorized scope after venue-specific integration/recovery tests and operational review. Do not revive deleted legacy Binance/TradingEngine code.

## Validation

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

Never claim verification without fresh exact-HEAD execution.

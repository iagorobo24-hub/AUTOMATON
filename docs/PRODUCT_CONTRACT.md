# Product Contract

## Mission

AUTOMATON exists to determine whether autonomous crypto-trading agents can make repeatable, risk-controlled decisions on real markets before any real capital is exposed.

The product is not a demo that appears active. Its value comes from trustworthy experiments, traceable decisions and evidence that can be reproduced or challenged.

## Operating modes

### Synthetic/Test
Synthetic data is permitted only for deterministic technical tests, fixtures and fault injection. Synthetic results are not financial evidence.

### Backtest
Historical real market data with virtual execution. Runs must be reproducible from a defined dataset/time window, strategy source/version, execution assumptions and initial capital.

### Paper
Current real market data with virtual funds. Agents operate forward in time behind explicit Risk and authoritative Accounting.

### Live Readiness
Phase 10 is a **technical readiness boundary**, not an execution mode. It may classify the architecture as `ARCHITECTURE_READY` while `real_capital_execution` remains `disabled`. It contains policy, venue-rule validation, idempotent future-intent records, read-only reconciliation, circuit breakers and emergency-stop state. It contains no real exchange order transport or real credential storage.

### Future Live
Current real data and real capital. Future Live remains separately prohibited until `LIVE_TRADING_GATE.md` is reviewed, a concrete venue adapter and secret-management design are audited, relevant integration/recovery evidence exists, and an explicit product decision authorizes real-capital activation.

## Truthfulness rules

- Never label synthetic/mock activity as Paper.
- Never label Live Readiness as Live trading.
- Never interpret `ARCHITECTURE_READY` as permission to move money.
- Never fabricate prices, trades, PnL, balances, fills or health telemetry.
- Unknown/unavailable data is shown as unavailable rather than invented.
- Every result preserves its mode/provenance.
- A strategy is not validated/profitable/production-ready without recorded evidence.
- Historical documentation and legacy code are not evidence of current functionality.

## Core product capabilities

1. Reliable fail-closed real market-data ingestion.
2. Deterministic/versioned strategy evaluation.
3. Explicit Risk approval before Paper execution.
4. Paper execution with realistic assumptions.
5. Correct portfolio/accounting invariants.
6. Backtesting and evidence generation.
7. Agent lifecycle, lineage and controlled evolution.
8. Monitoring, auditability and recovery for long-running Paper operation.
9. Strategy Research with holdout + forward evidence.
10. Live Readiness controls that remain incapable of real-capital execution until separately authorized.

## Out of core scope

Authentication, billing, payments, LLM chat, public APIs, multi-user tenancy and cosmetic dashboard extensions are not current priorities. Real-capital execution is also outside the completed Phase 10 scope.

## Decision principle

When there is tension between appearing operational and preserving evidence/safety, evidence and safety win.

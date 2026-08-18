# Product Contract

## Mission

AUTOMATON exists to determine whether autonomous crypto-trading agents can make repeatable, risk-controlled decisions on real markets before any real capital is exposed.

The product is not a demo that appears active. Its value comes from trustworthy experiments, traceable decisions and evidence that can be reproduced or challenged.

## Operating modes

### Synthetic/Test
Synthetic prices and virtual funds are permitted only for deterministic technical tests, fixtures and fault injection. Synthetic results are not financial evidence.

### Backtest
Historical real market data with virtual execution. Runs must be reproducible from a defined dataset/time window, strategy version, fee/slippage model and initial capital.

### Paper
Current real market data with virtual funds. Agents operate forward in time under the same explicit accounting and risk rules intended for later production evaluation.

### Live
Current real data and real capital. Live is a future mode, disabled by default and prohibited until `LIVE_TRADING_GATE.md` is satisfied and an explicit product decision authorizes implementation/activation.

## Truthfulness rules

- Never label synthetic or mock activity as Paper.
- Never fabricate prices, trades, PnL, win rate, RSI, balances, fills or health telemetry to make the UI look active.
- Unknown or unavailable data is shown as `N/D`, unavailable or equivalent.
- Every result must identify its mode and time interval.
- A strategy is not "validated", "optimized", "profitable" or "production-ready" without recorded evidence.
- Historical documentation and legacy code are not evidence of current functionality.

## Core product capabilities

1. Reliable real market-data ingestion.
2. Deterministic and versioned strategy evaluation.
3. Explicit risk approval before execution.
4. Paper execution with realistic assumptions.
5. Correct portfolio/accounting invariants.
6. Backtesting and evidence generation.
7. Agent lifecycle, lineage and controlled evolution.
8. Monitoring, auditability and recovery for long-running Paper operation.

## Out of core scope for the current program

Authentication, billing, Stripe, crypto payments, LLM chat, public APIs, multi-user tenancy and cosmetic dashboard extensions are not current priorities. They can be reconsidered only when they support a validated product need.

## Success criteria for the Paper milestone

Paper is considered implemented only when:

- market observations come from a real provider and carry timestamps/provenance;
- no random price generator or random close rule participates in Paper decisions;
- virtual orders/fills/positions reconcile to account equity;
- fees and slippage assumptions are explicit;
- risk limits can reject an order and stop trading;
- strategy/version and mode are persisted with evidence;
- the system can restart without inventing or losing open financial state;
- UI/metrics distinguish Paper from Backtest and Synthetic;
- fresh automated tests and an end-to-end Paper smoke test pass on the same HEAD.

## Decision principle

When there is tension between making the system look active and preserving evidence quality, evidence quality wins.

# Paper Trading

## Definition

Paper Trading means **real market data + virtual capital + simulated execution**. It is forward validation, not a visual simulation.

## Execution contract

A Paper order is created only after a strategy signal has passed Risk. Execution must record:

- agent and strategy/version;
- symbol and side;
- order type and requested quantity;
- decision timestamp and market observation reference;
- simulated fill price/time/quantity;
- fee and slippage assumptions;
- status transitions and rejection/cancellation reason.

## No randomness in financial semantics

Paper must not close or open trades because of an arbitrary random probability. Exits come from explicit strategy signals, stops, take-profit/trailing rules, time-based exits, risk controls or manual operator actions.

Randomness is permitted only in isolated tests/fault injection or future strategy mutation when seeded, recorded and unrelated to pretending market behavior.

## Fill model

The first Paper engine may use a deliberately conservative deterministic fill model. Complexity such as order-book depth can be added only when justified. The model must never claim exchange-grade realism it does not implement.

At minimum document and persist:

- market/limit semantics supported;
- slippage calculation;
- fees;
- partial-fill policy;
- timeout/cancellation policy;
- price source used for the fill.

## State and recovery

Open orders and positions are persistent financial state. Restarting the process must reconcile them from the database rather than resetting balances or inventing positions.

## Isolation from Live

Paper must not require exchange trading credentials. A Paper command must be structurally incapable of sending a real order. Future Live execution uses a different adapter and explicit authorization.

## Completion gate

Paper is not complete until account equity reconciles from fills/positions, risk can block orders, restarts preserve state, the UI labels Paper provenance, and fresh tests plus an end-to-end real-data/virtual-money smoke test pass.

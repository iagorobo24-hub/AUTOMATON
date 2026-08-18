# Portfolio and Accounting

## Goal

Maintain one reconciled financial source of truth for Backtest and Paper.

## Core invariants

For each account/agent, the system must be able to explain:

`equity = cash + market_value(open_positions)`

and separate:

- initial capital;
- available cash;
- reserved/committed cash where applicable;
- open-position cost basis;
- realized PnL;
- unrealized PnL;
- fees;
- total equity;
- exposure.

No UI component or strategy should maintain a competing balance calculation.

## Required records

The target model should persist explicit orders, fills and positions rather than infer all state from an ambiguous trade row. Equity snapshots may be persisted for analysis but must be derivable/reconcilable against source events.

## Realized and unrealized PnL

PnL definitions must be documented and tested for long and, if supported, short positions. Closing a position returns proceeds to cash exactly once. Fees must not disappear from accounting.

## Position lifecycle

A position must have clear state transitions and identity. Adding to, partially closing or fully closing a position must preserve cost basis and realized PnL consistently.

## Deposits and manual adjustments

Virtual funding changes are explicit ledger events with reason and timestamp. They must not be reported as trading profit.

## Replication

Agent replication creates a new financial account/allocation according to an explicit policy. It must not duplicate parent cash or turn unrealized profit into new money implicitly.

## Recovery and reconciliation

On restart, financial state is reconstructed or loaded from persisted authoritative records. The system should provide reconciliation checks that detect impossible balances, orphan fills, negative cash when forbidden, or positions inconsistent with fills.

## Completion gate

Accounting is ready for Paper only after deterministic unit tests cover open/close, fees, profit/loss, deposits, partial operations if supported, restart/reload and reconciliation invariants.

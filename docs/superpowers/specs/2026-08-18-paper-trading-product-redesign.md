# Paper Trading Product Redesign — Design Specification

**Date:** 2026-08-18

## Decision

AUTOMATON is being reoriented away from synthetic market simulation toward a research and Paper Trading platform whose immediate objective is to run autonomous agents on **real crypto market data with virtual capital**.

## Problem being corrected

The current active `AgentEngine` can generate synthetic price movement and randomly close trades. That behavior is acceptable only as isolated test infrastructure. It cannot be used to infer strategy performance or be presented as Paper Trading.

Historical documentation also mixed current and obsolete architectures and sometimes described legacy Mongo/Paper/TradingEngine capabilities as complete/current. The documentation is therefore rebuilt around product contracts rather than historical implementation claims.

## Product modes

- Synthetic/Test: generated data, virtual funds, technical validation only.
- Backtest: historical real data, virtual execution, reproducible evaluation.
- Paper: current real data, virtual capital, forward evaluation.
- Live: current real data, real capital, future gated capability.

## Target domain architecture

`Market Data -> Strategy -> Risk -> Paper Execution -> Portfolio/Accounting -> Metrics/Evidence`, with Agent Lifecycle and API/UI around those boundaries.

Each domain owns one responsibility and communicates through explicit contracts. Financial state is authoritative in the accounting layer. Strategies cannot mutate balances. Risk can block execution. Paper cannot route to a real exchange order.

## Evidence contract

Financial claims carry mode, strategy/config version, risk profile, period, capital basis, provider and fee/slippage assumptions. Missing data is not fabricated. Historical performance claims without reproducible project evidence are hypotheses.

## Strategy migration decision

S1-S4 remain baseline active strategies. Historical Alpha/Beta/Gamma documents are not retained as validated knowledge bases. Useful concepts—ATR, regime/BTC filters, scoring, liquidity filters, trailing/time exits, range/momentum/breakout specialization—are preserved as research hypotheses and must be validated through deterministic tests, real-data backtests and Paper.

## Legacy decision

Mongo `DatabaseService`, old Trading/Paper engines, registry, auth/payments/chat/notifications and legacy pages remain code-transition concerns only. New features are not built by remounting them. Concepts may be migrated to the SQLModel-centered target architecture; obsolete code is pruned after migration decisions.

## Implementation order

1. transition baseline and fresh validation;
2. real market data;
3. portfolio/accounting;
4. Paper execution;
5. risk;
6. backtesting/evidence;
7. evidence-aware agent evolution;
8. 24/7 Paper operation;
9. richer strategy research;
10. legacy pruning;
11. Live readiness, then optional Live only by explicit authorization.

## Closure criteria for the redesign documentation

The redesign is documented when one canonical README/architecture/product contract directs development, specialized domain docs define each major branch, the roadmap reflects dependency order, historical strategy/PRD documents no longer masquerade as current truth, and future coding agents are instructed not to reintroduce synthetic Paper or legacy Mongo shortcuts.

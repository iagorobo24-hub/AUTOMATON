# Agent Lifecycle

## Goal

Agents are experimental trading actors with identity, configuration, capital allocation and evidence. Their lifecycle must be observable and financially consistent.

## Core states

Current SQLModel states are `ACTIVO`, `MUERTO` and `REPLICADO`. Future refinement may add explicit paused/retired states only when required by product behavior.

## Creation

Creating an agent records at least identity, strategy/configuration version, initial virtual capital, mode and lineage metadata. Initial capital must be positive and must not be confused with trading profit.

## Operation

An active agent consumes market observations through its strategy, submits intents to Risk and can only affect financial state through the execution/accounting path.

## Death / retirement

The current balance-zero death rule is a baseline behavior, not the final research contract. Future death/retirement may also consider risk breaches, sustained underperformance, invalid configuration or experiment completion. Every termination must record a reason.

## Replication

Replication is a core product idea worth preserving, but profitability evidence must mature before replication becomes an optimization mechanism.

The current threshold-based behavior is acceptable as infrastructure testing. The target policy should require configurable evidence such as:

- minimum completed trades;
- minimum observation duration;
- acceptable drawdown;
- positive expectancy/performance criterion;
- strategy/risk version identity;
- no unresolved accounting/data-quality errors.

A child must not create money by copying a parent's balance. Capital allocation to descendants requires an explicit accounting policy.

## Lineage and mutation

Lineage should preserve parent/generation links and the configuration inherited by the child. Future parameter mutation is allowed only when seeded/recorded and evaluable as a new configuration version.

## Evidence isolation

Synthetic results may exercise lifecycle transitions but cannot trigger claims of financial fitness. Backtest and Paper evidence must remain distinguishable by mode.

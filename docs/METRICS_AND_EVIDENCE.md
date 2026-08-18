# Metrics and Evidence

## Principle

AUTOMATON is useful only if its results can be traced to real inputs and explicit assumptions. A dashboard value is not evidence by itself.

## Provenance

Every financial result must identify:

- mode: synthetic, backtest, paper or live;
- strategy/configuration version;
- risk profile/version;
- symbols/timeframe;
- observation period;
- capital basis;
- fee/slippage assumptions;
- data source;
- run/session identifier where applicable.

Results from different modes must not be merged into a single performance history without an explicit breakdown.

## Core metrics

The platform should support, where meaningful:

- cash and equity;
- realized/unrealized PnL;
- net return;
- trade count;
- wins/losses/win rate;
- average win/loss;
- expectancy;
- profit factor;
- maximum drawdown;
- exposure;
- fees/costs;
- strategy/agent uptime and error counts.

Metrics must use one accounting source of truth.

## Evidence labels

Use conservative language:

- **Observed**: directly measured from a valid run.
- **Reproduced**: independently rerun with matching result within defined tolerance.
- **Hypothesis**: design or trading idea not yet supported by project evidence.
- **Historical claim**: assertion from legacy docs/code that has not been revalidated.

Do not use `optimized`, `validated`, `profitable`, `safe` or `production-ready` without a documented criterion and supporting run evidence.

## UI rules

The UI must show mode and freshness for financial telemetry. Missing values stay missing. Synthetic/demo data may be shown only in an explicitly labelled development/test context and must never resemble Paper/Live performance.

## Evidence invalidation

A result is invalid for decision-making if affected by known data corruption/staleness, accounting defects, look-ahead bias, random market generation in a purported real-data mode, materially wrong fee/fill assumptions or mismatched code/configuration metadata.

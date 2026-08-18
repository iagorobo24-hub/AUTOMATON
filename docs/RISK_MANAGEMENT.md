# Risk Management

## Role

Risk is an independent approval layer between strategy intent and execution. A profitable-looking strategy cannot bypass it.

## Initial responsibilities

Risk should eventually control at least:

- risk per trade;
- maximum position size;
- maximum total exposure;
- maximum concurrent positions;
- per-symbol concentration;
- stop-loss requirement where applicable;
- daily/session loss limit;
- maximum drawdown;
- circuit breaker / global pause;
- stale-data rejection;
- invalid-accounting rejection.

## Position sizing

Position size must be derived from explicit capital and risk constraints. Historical ideas based on volatility/ATR are useful research candidates, but no fixed ATR multiplier or percentage is considered validated until tested.

## Stops and exits

Stop-loss, take-profit, trailing stops and time-based exits are strategy/risk rules with explicit parameters. They must not be replaced by random close probabilities.

## Drawdown

Drawdown is measured from account/equity peaks using a documented definition. Drawdown thresholds must specify their scope: agent, strategy, portfolio and/or session.

## Circuit breaker

When a critical invariant is violated—stale market data, accounting mismatch, repeated provider/execution errors, configured loss limit—the safe action is to reject new orders and surface the reason. Automatic recovery must be deliberate and observable.

## Evidence

Risk settings used for any Backtest/Paper result are part of the experiment configuration and must be persisted/versioned. Results from different risk profiles are not directly comparable unless stated.

## Historical material

The repository contains a legacy RiskManager and risk-related strategy documents. They are inputs for migration research, not active contracts. Reuse requires tests and compatibility with the SQLModel/accounting design.

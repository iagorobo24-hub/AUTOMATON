# Live Trading Gate

## Status

Live trading is **not an active product mode**. Real-capital execution must remain disabled until this gate is deliberately reviewed and approved.

## Required prerequisites

### Architecture
- Paper execution and Live execution use separate adapters.
- No default/environment setting can accidentally route a Paper command to Live.
- Trading credentials are unnecessary for Paper.
- Secret handling is reviewed and credentials are least-privilege where the exchange supports it.

### Market data and accounting
- Real market-data ingestion is stable under disconnects, stale data and gaps.
- Orders/fills/positions/equity reconcile across restart.
- Fees and exchange precision/minimums are modeled correctly enough for the intended venue.

### Risk
- Position/exposure limits are enforced independently of strategy code.
- Drawdown/loss limits and circuit breakers are tested.
- Stale data, accounting mismatch and repeated execution errors fail closed.
- A manual emergency stop exists and is tested.

### Strategy evidence
- Candidate strategy has reproducible historical evaluation.
- Candidate has meaningful forward Paper evidence over a deliberately chosen observation period and trade sample.
- Results include drawdown and costs, not only return/win rate.
- No unresolved high-severity data, accounting or execution defect affects the evidence.

### Operations
- Monitoring exposes provider/execution health and open financial state.
- Recovery/reconciliation procedures exist for process restart and partial failures.
- Audit records make order decisions and fills traceable.
- A staged rollout plan uses minimal capital and defined stop conditions.

## Explicit authorization

Passing technical gates does not automatically activate Live. A separate explicit product decision must authorize implementing/enabling real-capital execution.

## Prohibited shortcuts

- Do not reactivate the legacy TradingEngine/Binance paths as Live merely because code exists.
- Do not call exchange testnet activity "Paper" unless its semantics are documented; Paper remains virtual-capital execution under our control.
- Do not infer safety from a profitable backtest or short Paper run.

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid

class AssetBalance(BaseModel):
    total: float = 0
    available: float = 0
    reserved: float = 0
    in_orders: float = 0
    value_usd: float = 0

class TransactionSummary(BaseModel):
    total_deposits: float = 0
    total_withdrawals: float = 0
    total_trading_fees: float = 0
    total_funding_fees: float = 0
    net_trading_pnl: float = 0

class WalletLimits(BaseModel):
    max_position_value_usd: float = 500
    max_daily_loss_usd: float = 100
    daily_loss_used: float = 0
    daily_reset_at: Optional[datetime] = None

class Wallet(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    wallet_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    balances: Dict[str, AssetBalance] = {}
    total_value_usd: float = 0
    last_valuation_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    transaction_summary: TransactionSummary = TransactionSummary()
    limits: WalletLimits = WalletLimits()
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# --- Risk Profile Models ---
class PositionLimits(BaseModel):
    max_position_size_percent: float = 5
    max_positions_concurrent: int = 3
    max_exposure_single_asset_percent: float = 20
    max_exposure_correlated_assets_percent: float = 40

class LossLimits(BaseModel):
    max_loss_per_trade_percent: float = 2
    max_daily_loss_percent: float = 5
    max_weekly_loss_percent: float = 10
    max_monthly_loss_percent: float = 20
    max_drawdown_percent: float = 25

class BreachActions(BaseModel):
    on_daily_limit: str = "pause_trading"
    on_weekly_limit: str = "pause_trading"
    on_drawdown_limit: str = "stop_and_notify"
    cooldown_hours: int = 24

class VolatilityAdjustments(BaseModel):
    enabled: bool = True
    high_volatility_reduction: float = 0.5
    low_volatility_increase: float = 1.2

class RiskProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    risk_profile_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    is_template: bool = False
    parent_profile_id: Optional[str] = None
    inheritable: bool = True
    position_limits: PositionLimits = PositionLimits()
    loss_limits: LossLimits = LossLimits()
    breach_actions: BreachActions = BreachActions()
    volatility_adjustments: VolatilityAdjustments = VolatilityAdjustments()
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

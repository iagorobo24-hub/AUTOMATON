from datetime import datetime, timezone
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class Quote(BaseModel):
    model_config = ConfigDict(frozen=True)

    symbol: str
    price: Decimal
    observed_at: datetime
    received_at: datetime
    provider: str
    provider_symbol: str
    timestamp_source: Literal["provider", "retrieval"]
    evidence_mode: Literal["real"] = "real"

    @field_validator("observed_at", "received_at")
    @classmethod
    def _utc_datetime(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("market-data timestamps must be timezone-aware")
        return value.astimezone(timezone.utc)

    @field_validator("price")
    @classmethod
    def _positive_price(cls, value: Decimal) -> Decimal:
        if value <= 0:
            raise ValueError("price must be positive")
        return value

    @model_validator(mode="after")
    def _received_not_before_observed(self):
        # Small provider clock skew is handled by freshness validation. This only
        # protects obviously inverted records.
        if self.received_at < self.observed_at:
            raise ValueError("received_at cannot be before observed_at")
        return self


class Candle(BaseModel):
    model_config = ConfigDict(frozen=True)

    symbol: str
    interval: str
    open_time: datetime
    close_time: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    provider: str
    provider_symbol: str
    evidence_mode: Literal["real"] = "real"

    @field_validator("open_time", "close_time")
    @classmethod
    def _utc_datetime(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("market-data timestamps must be timezone-aware")
        return value.astimezone(timezone.utc)

    @field_validator("open", "high", "low", "close")
    @classmethod
    def _positive_price(cls, value: Decimal) -> Decimal:
        if value <= 0:
            raise ValueError("OHLC prices must be positive")
        return value

    @field_validator("volume")
    @classmethod
    def _non_negative_volume(cls, value: Decimal) -> Decimal:
        if value < 0:
            raise ValueError("volume cannot be negative")
        return value

    @model_validator(mode="after")
    def _valid_ohlc(self):
        if self.close_time <= self.open_time:
            raise ValueError("close_time must be after open_time")
        if self.high < max(self.open, self.close):
            raise ValueError("high cannot be below open/close")
        if self.low > min(self.open, self.close):
            raise ValueError("low cannot be above open/close")
        if self.high < self.low:
            raise ValueError("high cannot be below low")
        return self

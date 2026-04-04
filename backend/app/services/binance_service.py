"""
Binance Service - Real market data and trade execution
Supports both paper trading and live trading modes
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from binance.client import Client
from binance.exceptions import BinanceAPIException

from ..core.config import settings

logger = logging.getLogger(__name__)


class BinanceService:
    """Service for Binance API interaction"""

    def __init__(self):
        self.client: Optional[Client] = None
        self.is_testnet = settings.BINANCE_TESTNET
        self.paper_trading = settings.PAPER_TRADING
        self.connected = False
        self._connect()

    def _connect(self):
        """Initialize Binance client"""
        if (
            not settings.BINANCE_API_KEY
            or settings.BINANCE_API_KEY == "your_binance_api_key_here"
        ):
            logger.warning(
                "Binance API key not configured. Paper trading will use mock data."
            )
            return

        try:
            if self.is_testnet:
                self.client = Client(
                    settings.BINANCE_API_KEY, settings.BINANCE_SECRET_KEY, testnet=True
                )
                logger.info("Connected to Binance TESTNET")
            else:
                self.client = Client(
                    settings.BINANCE_API_KEY, settings.BINANCE_SECRET_KEY
                )
                logger.info(
                    f"Connected to Binance {'TESTNET' if self.is_testnet else 'MAINNET'}"
                )
            self.connected = True
        except BinanceAPIException as e:
            logger.error(f"Failed to connect to Binance: {e}")
            self.connected = False

    def is_connected(self) -> bool:
        return self.connected and self.client is not None

    # ==================== MARKET DATA ====================

    def get_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        if not self.is_connected():
            return self._mock_price(symbol)

        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker["price"])
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return self._mock_price(symbol)

    def get_ticker(self, symbol: str) -> Dict:
        """Get 24h ticker stats"""
        if not self.is_connected():
            return self._mock_ticker(symbol)

        try:
            ticker = self.client.get_24hr_ticker(symbol=symbol)
            return {
                "symbol": ticker["symbol"],
                "price": float(ticker["lastPrice"]),
                "high_24h": float(ticker["highPrice"]),
                "low_24h": float(ticker["lowPrice"]),
                "volume_24h": float(ticker["volume"]),
                "quote_volume_24h": float(ticker["quoteVolume"]),
                "change_24h_percent": float(ticker["priceChangePercent"]),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol}: {e}")
            return self._mock_ticker(symbol)

    def get_klines(
        self, symbol: str, interval: str = "4h", limit: int = 100
    ) -> List[Dict]:
        """Get candlestick data"""
        if not self.is_connected():
            return self._mock_klines(symbol, interval, limit)

        try:
            klines = self.client.get_klines(
                symbol=symbol, interval=interval, limit=limit
            )
            return [
                {
                    "timestamp": datetime.fromtimestamp(k[0] / 1000, tz=timezone.utc),
                    "open": float(k[1]),
                    "high": float(k[2]),
                    "low": float(k[3]),
                    "close": float(k[4]),
                    "volume": float(k[5]),
                    "close_time": datetime.fromtimestamp(k[6] / 1000, tz=timezone.utc),
                    "quote_volume": float(k[7]),
                    "trades": k[8],
                }
                for k in klines
            ]
        except Exception as e:
            logger.error(f"Error fetching klines for {symbol}: {e}")
            return self._mock_klines(symbol, interval, limit)

    def get_orderbook(self, symbol: str, depth: int = 10) -> Dict:
        """Get order book snapshot"""
        if not self.is_connected():
            return self._mock_orderbook(symbol, depth)

        try:
            book = self.client.get_order_book(symbol=symbol, limit=depth)
            return {
                "symbol": symbol,
                "bids": [[float(b[0]), float(b[1])] for b in book["bids"]],
                "asks": [[float(a[0]), float(a[1])] for a in book["asks"]],
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            logger.error(f"Error fetching orderbook for {symbol}: {e}")
            return self._mock_orderbook(symbol, depth)

    # ==================== ACCOUNT ====================

    def get_balance(self, asset: str = "USDT") -> float:
        """Get account balance for an asset"""
        if not self.is_connected() or self.paper_trading:
            return 1000.0

        try:
            account = self.client.get_account()
            for balance in account["balances"]:
                if balance["asset"] == asset:
                    return float(balance["free"])
            return 0.0
        except Exception as e:
            logger.error(f"Error fetching balance for {asset}: {e}")
            return 1000.0

    def get_account_info(self) -> Dict:
        """Get full account info"""
        if not self.is_connected():
            return {"paper_trading": True, "balance_usdt": 1000.0}

        try:
            account = self.client.get_account()
            return {
                "can_trade": account.get("canTrade", False),
                "can_withdraw": account.get("canWithdraw", False),
                "can_deposit": account.get("canDeposit", False),
                "balances": {
                    b["asset"]: {"free": float(b["free"]), "locked": float(b["locked"])}
                    for b in account["balances"]
                    if float(b["free"]) > 0 or float(b["locked"]) > 0
                },
            }
        except Exception as e:
            logger.error(f"Error fetching account info: {e}")
            return {"error": str(e)}

    # ==================== TRADE EXECUTION ====================

    def place_market_order(self, symbol: str, side: str, quantity: float) -> Dict:
        """Place a market order"""
        if self.paper_trading or not self.is_connected():
            return self._mock_order(symbol, side, quantity)

        try:
            order = self.client.create_order(
                symbol=symbol, side=side.upper(), type="MARKET", quantity=quantity
            )
            logger.info(
                f"Order placed: {side} {quantity} {symbol} @ {order.get('fills', [{}])[0].get('price', 'N/A')}"
            )
            return {
                "order_id": str(order["orderId"]),
                "symbol": symbol,
                "side": side,
                "type": "market",
                "quantity": quantity,
                "price": float(order["fills"][0]["price"]) if order.get("fills") else 0,
                "status": order["status"],
                "timestamp": datetime.fromtimestamp(
                    order["transactTime"] / 1000, tz=timezone.utc
                ).isoformat(),
            }
        except BinanceAPIException as e:
            logger.error(f"Order failed: {e}")
            return {"error": str(e), "symbol": symbol, "side": side}

    def place_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        time_in_force: str = "GTC",
    ) -> Dict:
        """Place a limit order"""
        if self.paper_trading or not self.is_connected():
            return self._mock_order(symbol, side, quantity, price)

        try:
            order = self.client.create_order(
                symbol=symbol,
                side=side.upper(),
                type="LIMIT",
                timeInForce=time_in_force,
                quantity=quantity,
                price=f"{price:.8f}",
            )
            return {
                "order_id": str(order["orderId"]),
                "symbol": symbol,
                "side": side,
                "type": "limit",
                "quantity": quantity,
                "price": price,
                "status": order["status"],
                "timestamp": datetime.fromtimestamp(
                    order["transactTime"] / 1000, tz=timezone.utc
                ).isoformat(),
            }
        except BinanceAPIException as e:
            logger.error(f"Limit order failed: {e}")
            return {"error": str(e), "symbol": symbol, "side": side}

    def cancel_order(self, symbol: str, order_id: int) -> bool:
        """Cancel an open order"""
        if self.paper_trading or not self.is_connected():
            return True

        try:
            self.client.cancel_order(symbol=symbol, orderId=order_id)
            return True
        except Exception as e:
            logger.error(f"Failed to cancel order {order_id}: {e}")
            return False

    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get open orders"""
        if self.paper_trading or not self.is_connected():
            return []

        try:
            if symbol:
                orders = self.client.get_open_orders(symbol=symbol)
            else:
                orders = self.client.get_open_orders()
            return orders
        except Exception as e:
            logger.error(f"Error fetching open orders: {e}")
            return []

    # ==================== MOCK FALLBACKS ====================

    def _mock_price(self, symbol: str) -> float:
        import random

        base_prices = {
            "BTCUSDT": 65000,
            "ETHUSDT": 3500,
            "SOLUSDT": 140,
            "BNBUSDT": 580,
            "ADAUSDT": 0.45,
            "DOTUSDT": 7.2,
        }
        base = base_prices.get(symbol, 100)
        return base * (1 + random.uniform(-0.02, 0.02))

    def _mock_ticker(self, symbol: str) -> Dict:
        price = self._mock_price(symbol)
        return {
            "symbol": symbol,
            "price": price,
            "high_24h": price * 1.03,
            "low_24h": price * 0.97,
            "volume_24h": 1000000,
            "quote_volume_24h": 50000000,
            "change_24h_percent": random.uniform(-3, 3),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _mock_klines(self, symbol: str, interval: str, limit: int) -> List[Dict]:
        import random

        base = self._mock_price(symbol)
        klines = []
        now = datetime.now(timezone.utc)
        for i in range(limit):
            change = random.uniform(-0.02, 0.02)
            close = base * (1 + change)
            klines.append(
                {
                    "timestamp": now,
                    "open": base,
                    "high": max(base, close) * 1.005,
                    "low": min(base, close) * 0.995,
                    "close": close,
                    "volume": random.uniform(100, 10000),
                    "close_time": now,
                    "quote_volume": random.uniform(10000, 500000),
                    "trades": random.randint(50, 500),
                }
            )
            base = close
        return klines

    def _mock_orderbook(self, symbol: str, depth: int) -> Dict:
        import random

        price = self._mock_price(symbol)
        return {
            "symbol": symbol,
            "bids": [
                [price * (1 - i * 0.001), random.uniform(1, 100)] for i in range(depth)
            ],
            "asks": [
                [price * (1 + i * 0.001), random.uniform(1, 100)] for i in range(depth)
            ],
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _mock_order(
        self, symbol: str, side: str, quantity: float, price: float = None
    ) -> Dict:
        import random

        fill_price = price or self._mock_price(symbol)
        return {
            "order_id": f"mock_{random.randint(10000, 99999)}",
            "symbol": symbol,
            "side": side,
            "type": "market" if price is None else "limit",
            "quantity": quantity,
            "price": fill_price,
            "status": "FILLED",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

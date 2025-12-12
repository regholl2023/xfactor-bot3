"""
Alpaca Broker Integration.

Alpaca provides:
- Commission-free trading
- Excellent REST and WebSocket APIs
- Paper trading environment
- Fractional shares
- Extended hours trading
- Crypto trading
"""

from datetime import datetime
from typing import Optional, List, Dict, Any

from loguru import logger

from src.brokers.base import (
    BaseBroker, BrokerType, Position, Order, AccountInfo,
    OrderStatus, OrderType, OrderSide
)


class AlpacaBroker(BaseBroker):
    """
    Alpaca Markets broker implementation.
    
    Free, commission-free trading with excellent API.
    Supports stocks, ETFs, and crypto.
    
    Environment variables needed:
    - ALPACA_API_KEY
    - ALPACA_SECRET_KEY
    - ALPACA_PAPER (true/false)
    """
    
    BASE_URL_PAPER = "https://paper-api.alpaca.markets"
    BASE_URL_LIVE = "https://api.alpaca.markets"
    DATA_URL = "https://data.alpaca.markets"
    
    def __init__(
        self,
        api_key: str = "",
        secret_key: str = "",
        paper: bool = True,
        **kwargs
    ):
        super().__init__(BrokerType.ALPACA)
        self.api_key = api_key
        self.secret_key = secret_key
        self.paper = paper
        self.base_url = self.BASE_URL_PAPER if paper else self.BASE_URL_LIVE
        self._client = None
        self._trading_client = None
        self._data_client = None
    
    async def connect(self) -> bool:
        """Connect to Alpaca API."""
        try:
            # Try to import alpaca-py
            from alpaca.trading.client import TradingClient
            from alpaca.data.historical import StockHistoricalDataClient
            
            self._trading_client = TradingClient(
                api_key=self.api_key,
                secret_key=self.secret_key,
                paper=self.paper
            )
            
            self._data_client = StockHistoricalDataClient(
                api_key=self.api_key,
                secret_key=self.secret_key
            )
            
            # Test connection by getting account
            account = self._trading_client.get_account()
            self._connected = True
            logger.info(f"Connected to Alpaca {'Paper' if self.paper else 'Live'} - Account: {account.account_number}")
            return True
            
        except ImportError:
            logger.error("alpaca-py not installed. Run: pip install alpaca-py")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to Alpaca: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from Alpaca."""
        self._trading_client = None
        self._data_client = None
        self._connected = False
        logger.info("Disconnected from Alpaca")
    
    async def health_check(self) -> bool:
        """Check Alpaca connection health."""
        if not self._trading_client:
            return False
        try:
            self._trading_client.get_account()
            return True
        except Exception:
            return False
    
    async def get_accounts(self) -> List[AccountInfo]:
        """Get Alpaca account (single account per API key)."""
        if not self._trading_client:
            return []
        
        try:
            account = self._trading_client.get_account()
            return [AccountInfo(
                account_id=account.account_number,
                broker=BrokerType.ALPACA,
                account_type="margin" if account.multiplier > 1 else "cash",
                buying_power=float(account.buying_power),
                cash=float(account.cash),
                portfolio_value=float(account.portfolio_value),
                equity=float(account.equity),
                margin_used=float(account.initial_margin or 0),
                margin_available=float(account.regt_buying_power or 0),
                day_trades_remaining=account.daytrade_count if hasattr(account, 'daytrade_count') else 3,
                is_pattern_day_trader=account.pattern_day_trader,
                currency=account.currency,
                last_updated=datetime.now()
            )]
        except Exception as e:
            logger.error(f"Error getting Alpaca account: {e}")
            return []
    
    async def get_account_info(self, account_id: str) -> AccountInfo:
        """Get Alpaca account info."""
        accounts = await self.get_accounts()
        if accounts:
            return accounts[0]
        raise ValueError("No account found")
    
    async def get_buying_power(self, account_id: str) -> float:
        """Get available buying power."""
        if not self._trading_client:
            return 0.0
        try:
            account = self._trading_client.get_account()
            return float(account.buying_power)
        except Exception as e:
            logger.error(f"Error getting buying power: {e}")
            return 0.0
    
    async def get_positions(self, account_id: str) -> List[Position]:
        """Get all open positions."""
        if not self._trading_client:
            return []
        
        try:
            positions = self._trading_client.get_all_positions()
            return [
                Position(
                    symbol=p.symbol,
                    quantity=float(p.qty),
                    avg_cost=float(p.avg_entry_price),
                    current_price=float(p.current_price),
                    market_value=float(p.market_value),
                    unrealized_pnl=float(p.unrealized_pl),
                    unrealized_pnl_pct=float(p.unrealized_plpc) * 100,
                    side="long" if float(p.qty) > 0 else "short",
                    broker=BrokerType.ALPACA,
                    account_id=account_id,
                    last_updated=datetime.now()
                )
                for p in positions
            ]
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []
    
    async def get_position(self, account_id: str, symbol: str) -> Optional[Position]:
        """Get position for a specific symbol."""
        if not self._trading_client:
            return None
        
        try:
            p = self._trading_client.get_open_position(symbol)
            return Position(
                symbol=p.symbol,
                quantity=float(p.qty),
                avg_cost=float(p.avg_entry_price),
                current_price=float(p.current_price),
                market_value=float(p.market_value),
                unrealized_pnl=float(p.unrealized_pl),
                unrealized_pnl_pct=float(p.unrealized_plpc) * 100,
                side="long" if float(p.qty) > 0 else "short",
                broker=BrokerType.ALPACA,
                account_id=account_id,
                last_updated=datetime.now()
            )
        except Exception:
            return None
    
    async def submit_order(
        self,
        account_id: str,
        symbol: str,
        side: OrderSide,
        quantity: float,
        order_type: OrderType = OrderType.MARKET,
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        time_in_force: str = "day",
        **kwargs
    ) -> Order:
        """Submit an order to Alpaca."""
        if not self._trading_client:
            raise ConnectionError("Not connected to Alpaca")
        
        from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, StopOrderRequest, StopLimitOrderRequest
        from alpaca.trading.enums import OrderSide as AlpacaSide, TimeInForce
        
        try:
            # Map order side
            alpaca_side = AlpacaSide.BUY if side == OrderSide.BUY else AlpacaSide.SELL
            
            # Map time in force
            tif_map = {
                "day": TimeInForce.DAY,
                "gtc": TimeInForce.GTC,
                "ioc": TimeInForce.IOC,
                "fok": TimeInForce.FOK,
            }
            alpaca_tif = tif_map.get(time_in_force.lower(), TimeInForce.DAY)
            
            # Create order request based on type
            if order_type == OrderType.MARKET:
                request = MarketOrderRequest(
                    symbol=symbol,
                    qty=quantity,
                    side=alpaca_side,
                    time_in_force=alpaca_tif
                )
            elif order_type == OrderType.LIMIT:
                request = LimitOrderRequest(
                    symbol=symbol,
                    qty=quantity,
                    side=alpaca_side,
                    time_in_force=alpaca_tif,
                    limit_price=limit_price
                )
            elif order_type == OrderType.STOP:
                request = StopOrderRequest(
                    symbol=symbol,
                    qty=quantity,
                    side=alpaca_side,
                    time_in_force=alpaca_tif,
                    stop_price=stop_price
                )
            elif order_type == OrderType.STOP_LIMIT:
                request = StopLimitOrderRequest(
                    symbol=symbol,
                    qty=quantity,
                    side=alpaca_side,
                    time_in_force=alpaca_tif,
                    limit_price=limit_price,
                    stop_price=stop_price
                )
            else:
                raise ValueError(f"Unsupported order type: {order_type}")
            
            # Submit order
            order = self._trading_client.submit_order(request)
            
            logger.info(f"Alpaca order submitted: {order.id} - {side.value} {quantity} {symbol}")
            
            return Order(
                order_id=str(order.id),
                symbol=order.symbol,
                side=side,
                order_type=order_type,
                quantity=float(order.qty),
                limit_price=float(order.limit_price) if order.limit_price else None,
                stop_price=float(order.stop_price) if order.stop_price else None,
                status=self._map_order_status(order.status.value),
                filled_quantity=float(order.filled_qty) if order.filled_qty else 0,
                avg_fill_price=float(order.filled_avg_price) if order.filled_avg_price else None,
                broker=BrokerType.ALPACA,
                account_id=account_id,
                created_at=order.created_at,
                updated_at=order.updated_at or datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error submitting Alpaca order: {e}")
            raise
    
    async def cancel_order(self, account_id: str, order_id: str) -> bool:
        """Cancel an open order."""
        if not self._trading_client:
            return False
        
        try:
            self._trading_client.cancel_order_by_id(order_id)
            logger.info(f"Alpaca order cancelled: {order_id}")
            return True
        except Exception as e:
            logger.error(f"Error cancelling Alpaca order: {e}")
            return False
    
    async def get_order(self, account_id: str, order_id: str) -> Optional[Order]:
        """Get order details."""
        if not self._trading_client:
            return None
        
        try:
            order = self._trading_client.get_order_by_id(order_id)
            return self._convert_order(order, account_id)
        except Exception:
            return None
    
    async def get_open_orders(self, account_id: str) -> List[Order]:
        """Get all open orders."""
        if not self._trading_client:
            return []
        
        try:
            from alpaca.trading.requests import GetOrdersRequest
            from alpaca.trading.enums import QueryOrderStatus
            
            request = GetOrdersRequest(status=QueryOrderStatus.OPEN)
            orders = self._trading_client.get_orders(request)
            return [self._convert_order(o, account_id) for o in orders]
        except Exception as e:
            logger.error(f"Error getting open orders: {e}")
            return []
    
    async def get_order_history(
        self,
        account_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Order]:
        """Get order history."""
        if not self._trading_client:
            return []
        
        try:
            from alpaca.trading.requests import GetOrdersRequest
            from alpaca.trading.enums import QueryOrderStatus
            
            request = GetOrdersRequest(
                status=QueryOrderStatus.ALL,
                limit=limit,
                after=start_date,
                until=end_date
            )
            orders = self._trading_client.get_orders(request)
            return [self._convert_order(o, account_id) for o in orders]
        except Exception as e:
            logger.error(f"Error getting order history: {e}")
            return []
    
    async def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current quote from Alpaca data."""
        if not self._data_client:
            return None
        
        try:
            from alpaca.data.requests import StockLatestQuoteRequest
            
            request = StockLatestQuoteRequest(symbol_or_symbols=symbol)
            quotes = self._data_client.get_stock_latest_quote(request)
            
            if symbol in quotes:
                q = quotes[symbol]
                return {
                    "symbol": symbol,
                    "bid": float(q.bid_price),
                    "ask": float(q.ask_price),
                    "bid_size": int(q.bid_size),
                    "ask_size": int(q.ask_size),
                    "timestamp": q.timestamp.isoformat()
                }
        except Exception as e:
            logger.error(f"Error getting quote: {e}")
        return None
    
    async def get_bars(
        self,
        symbol: str,
        timeframe: str = "1d",
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 100
    ) -> Optional[List[Dict[str, Any]]]:
        """Get historical bars from Alpaca."""
        if not self._data_client:
            return None
        
        try:
            from alpaca.data.requests import StockBarsRequest
            from alpaca.data.timeframe import TimeFrame
            
            # Map timeframe
            tf_map = {
                "1m": TimeFrame.Minute,
                "5m": TimeFrame.Minute,
                "15m": TimeFrame.Minute,
                "1h": TimeFrame.Hour,
                "1d": TimeFrame.Day,
                "1w": TimeFrame.Week,
            }
            tf = tf_map.get(timeframe, TimeFrame.Day)
            
            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=tf,
                start=start,
                end=end,
                limit=limit
            )
            bars = self._data_client.get_stock_bars(request)
            
            if symbol in bars:
                return [
                    {
                        "timestamp": b.timestamp.isoformat(),
                        "open": float(b.open),
                        "high": float(b.high),
                        "low": float(b.low),
                        "close": float(b.close),
                        "volume": int(b.volume),
                        "vwap": float(b.vwap) if b.vwap else None
                    }
                    for b in bars[symbol]
                ]
        except Exception as e:
            logger.error(f"Error getting bars: {e}")
        return None
    
    def _map_order_status(self, status: str) -> OrderStatus:
        """Map Alpaca order status to our OrderStatus."""
        status_map = {
            "new": OrderStatus.SUBMITTED,
            "accepted": OrderStatus.SUBMITTED,
            "pending_new": OrderStatus.PENDING,
            "accepted_for_bidding": OrderStatus.SUBMITTED,
            "filled": OrderStatus.FILLED,
            "partially_filled": OrderStatus.PARTIALLY_FILLED,
            "canceled": OrderStatus.CANCELLED,
            "expired": OrderStatus.EXPIRED,
            "rejected": OrderStatus.REJECTED,
            "pending_cancel": OrderStatus.SUBMITTED,
            "pending_replace": OrderStatus.SUBMITTED,
        }
        return status_map.get(status.lower(), OrderStatus.PENDING)
    
    def _convert_order(self, order, account_id: str) -> Order:
        """Convert Alpaca order to our Order type."""
        return Order(
            order_id=str(order.id),
            symbol=order.symbol,
            side=OrderSide.BUY if order.side.value == "buy" else OrderSide.SELL,
            order_type=OrderType.MARKET,  # Simplified
            quantity=float(order.qty),
            limit_price=float(order.limit_price) if order.limit_price else None,
            stop_price=float(order.stop_price) if order.stop_price else None,
            status=self._map_order_status(order.status.value),
            filled_quantity=float(order.filled_qty) if order.filled_qty else 0,
            avg_fill_price=float(order.filled_avg_price) if order.filled_avg_price else None,
            broker=BrokerType.ALPACA,
            account_id=account_id,
            created_at=order.created_at,
            updated_at=order.updated_at or datetime.now()
        )


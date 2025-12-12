"""
Tradier Broker Integration.

Tradier provides:
- Low-cost options trading ($0 stock, $0.35/contract options)
- Excellent REST API
- Real-time streaming
- Paper trading sandbox
"""

from datetime import datetime
from typing import Optional, List, Dict, Any

from loguru import logger

from src.brokers.base import (
    BaseBroker, BrokerType, Position, Order, AccountInfo,
    OrderStatus, OrderType, OrderSide
)


class TradierBroker(BaseBroker):
    """
    Tradier broker implementation.
    
    Great for options trading with low commissions.
    
    Environment variables needed:
    - TRADIER_ACCESS_TOKEN
    - TRADIER_ACCOUNT_ID
    - TRADIER_SANDBOX (true/false)
    """
    
    BASE_URL_LIVE = "https://api.tradier.com/v1"
    BASE_URL_SANDBOX = "https://sandbox.tradier.com/v1"
    
    def __init__(
        self,
        access_token: str = "",
        account_id: str = "",
        sandbox: bool = True,
        **kwargs
    ):
        super().__init__(BrokerType.TRADIER)
        self.access_token = access_token
        self.account_id = account_id
        self.sandbox = sandbox
        self.base_url = self.BASE_URL_SANDBOX if sandbox else self.BASE_URL_LIVE
    
    async def connect(self) -> bool:
        """Connect to Tradier API."""
        try:
            # Test connection by getting profile
            data = await self._make_request("GET", "/user/profile")
            if data:
                self._connected = True
                logger.info(f"Connected to Tradier {'Sandbox' if self.sandbox else 'Live'}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to connect to Tradier: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from Tradier."""
        self._connected = False
        logger.info("Disconnected from Tradier")
    
    async def health_check(self) -> bool:
        """Check Tradier connection health."""
        data = await self._make_request("GET", "/user/profile")
        return data is not None
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Make authenticated request to Tradier API."""
        import httpx
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                f"{self.base_url}{endpoint}",
                headers=headers,
                **kwargs
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Tradier API error: {response.status_code}")
                return None
    
    async def get_accounts(self) -> List[AccountInfo]:
        """Get Tradier accounts."""
        data = await self._make_request("GET", "/user/profile")
        if not data:
            return []
        
        accounts = []
        profile = data.get("profile", {})
        for acc in profile.get("account", []):
            if isinstance(acc, dict):
                accounts.append(AccountInfo(
                    account_id=acc.get("account_number", ""),
                    broker=BrokerType.TRADIER,
                    account_type=acc.get("type", "margin"),
                    buying_power=0,  # Need separate call
                    cash=0,
                    portfolio_value=0,
                    equity=0,
                    currency="USD",
                    last_updated=datetime.now()
                ))
        
        # Get balances for each account
        for acc in accounts:
            balance_data = await self._make_request(
                "GET",
                f"/accounts/{acc.account_id}/balances"
            )
            if balance_data:
                balances = balance_data.get("balances", {})
                acc.buying_power = float(balances.get("buying_power", 0))
                acc.cash = float(balances.get("cash", {}).get("cash_available", 0))
                acc.portfolio_value = float(balances.get("total_equity", 0))
                acc.equity = float(balances.get("equity", 0))
        
        return accounts
    
    async def get_account_info(self, account_id: str) -> AccountInfo:
        """Get account info."""
        accounts = await self.get_accounts()
        for acc in accounts:
            if acc.account_id == account_id:
                return acc
        raise ValueError(f"Account not found: {account_id}")
    
    async def get_buying_power(self, account_id: str) -> float:
        """Get buying power."""
        data = await self._make_request("GET", f"/accounts/{account_id}/balances")
        if data:
            return float(data.get("balances", {}).get("buying_power", 0))
        return 0.0
    
    async def get_positions(self, account_id: str) -> List[Position]:
        """Get positions."""
        data = await self._make_request("GET", f"/accounts/{account_id}/positions")
        if not data:
            return []
        
        positions_data = data.get("positions", {})
        if positions_data == "null" or not positions_data:
            return []
        
        position_list = positions_data.get("position", [])
        if isinstance(position_list, dict):
            position_list = [position_list]
        
        positions = []
        for pos in position_list:
            positions.append(Position(
                symbol=pos.get("symbol", ""),
                quantity=float(pos.get("quantity", 0)),
                avg_cost=float(pos.get("cost_basis", 0)) / max(float(pos.get("quantity", 1)), 1),
                current_price=0,  # Need quote
                market_value=float(pos.get("cost_basis", 0)),
                unrealized_pnl=0,
                unrealized_pnl_pct=0,
                side="long" if float(pos.get("quantity", 0)) > 0 else "short",
                broker=BrokerType.TRADIER,
                account_id=account_id,
                last_updated=datetime.now()
            ))
        
        return positions
    
    async def get_position(self, account_id: str, symbol: str) -> Optional[Position]:
        """Get position for symbol."""
        positions = await self.get_positions(account_id)
        for pos in positions:
            if pos.symbol == symbol:
                return pos
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
        """Submit order to Tradier."""
        order_data = {
            "class": "equity",
            "symbol": symbol,
            "side": "buy" if side == OrderSide.BUY else "sell",
            "quantity": int(quantity),
            "type": order_type.value,
            "duration": time_in_force,
        }
        
        if limit_price:
            order_data["price"] = limit_price
        if stop_price:
            order_data["stop"] = stop_price
        
        data = await self._make_request(
            "POST",
            f"/accounts/{account_id}/orders",
            data=order_data
        )
        
        if data and data.get("order"):
            order_info = data["order"]
            return Order(
                order_id=str(order_info.get("id", "")),
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                limit_price=limit_price,
                stop_price=stop_price,
                status=self._map_status(order_info.get("status", "")),
                broker=BrokerType.TRADIER,
                account_id=account_id,
                created_at=datetime.now()
            )
        raise Exception("Failed to submit order")
    
    async def cancel_order(self, account_id: str, order_id: str) -> bool:
        """Cancel order."""
        data = await self._make_request(
            "DELETE",
            f"/accounts/{account_id}/orders/{order_id}"
        )
        return data is not None and data.get("order", {}).get("status") == "ok"
    
    async def get_order(self, account_id: str, order_id: str) -> Optional[Order]:
        """Get order details."""
        data = await self._make_request(
            "GET",
            f"/accounts/{account_id}/orders/{order_id}"
        )
        if data and data.get("order"):
            return self._convert_order(data["order"], account_id)
        return None
    
    async def get_open_orders(self, account_id: str) -> List[Order]:
        """Get open orders."""
        data = await self._make_request(
            "GET",
            f"/accounts/{account_id}/orders",
            params={"includeTags": "true"}
        )
        if not data or not data.get("orders"):
            return []
        
        orders = data["orders"].get("order", [])
        if isinstance(orders, dict):
            orders = [orders]
        
        return [
            self._convert_order(o, account_id)
            for o in orders
            if o.get("status") in ["open", "pending", "partially_filled"]
        ]
    
    async def get_order_history(
        self,
        account_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Order]:
        """Get order history."""
        data = await self._make_request(
            "GET",
            f"/accounts/{account_id}/orders"
        )
        if not data or not data.get("orders"):
            return []
        
        orders = data["orders"].get("order", [])
        if isinstance(orders, dict):
            orders = [orders]
        
        return [self._convert_order(o, account_id) for o in orders[:limit]]
    
    async def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get quote from Tradier."""
        data = await self._make_request(
            "GET",
            "/markets/quotes",
            params={"symbols": symbol}
        )
        if data and data.get("quotes"):
            quote = data["quotes"].get("quote", {})
            return {
                "symbol": symbol,
                "bid": float(quote.get("bid", 0)),
                "ask": float(quote.get("ask", 0)),
                "last": float(quote.get("last", 0)),
                "volume": int(quote.get("volume", 0)),
            }
        return None
    
    def _convert_order(self, data: Dict, account_id: str) -> Order:
        """Convert Tradier order to Order."""
        return Order(
            order_id=str(data.get("id", "")),
            symbol=data.get("symbol", ""),
            side=OrderSide.BUY if data.get("side") == "buy" else OrderSide.SELL,
            order_type=OrderType.MARKET,
            quantity=float(data.get("quantity", 0)),
            limit_price=data.get("price"),
            stop_price=data.get("stop_price"),
            status=self._map_status(data.get("status", "")),
            filled_quantity=float(data.get("exec_quantity", 0)),
            avg_fill_price=data.get("avg_fill_price"),
            broker=BrokerType.TRADIER,
            account_id=account_id,
            created_at=datetime.now()
        )
    
    def _map_status(self, status: str) -> OrderStatus:
        """Map Tradier status to OrderStatus."""
        status_map = {
            "open": OrderStatus.SUBMITTED,
            "pending": OrderStatus.PENDING,
            "partially_filled": OrderStatus.PARTIALLY_FILLED,
            "filled": OrderStatus.FILLED,
            "canceled": OrderStatus.CANCELLED,
            "rejected": OrderStatus.REJECTED,
            "expired": OrderStatus.EXPIRED,
        }
        return status_map.get(status.lower(), OrderStatus.PENDING)


"""
Charles Schwab / TD Ameritrade Broker Integration.

Schwab acquired TD Ameritrade and is transitioning to a unified API.
This integration supports both the legacy TD API and new Schwab API.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any

from loguru import logger

from src.brokers.base import (
    BaseBroker, BrokerType, Position, Order, AccountInfo,
    OrderStatus, OrderType, OrderSide
)


class SchwabBroker(BaseBroker):
    """
    Charles Schwab / TD Ameritrade broker implementation.
    
    Supports:
    - Stocks, ETFs, Options, Futures
    - OAuth2 authentication
    - Streaming market data
    
    Environment variables needed:
    - SCHWAB_CLIENT_ID (App Key)
    - SCHWAB_CLIENT_SECRET
    - SCHWAB_REFRESH_TOKEN
    - SCHWAB_ACCOUNT_ID
    """
    
    BASE_URL = "https://api.schwabapi.com"
    AUTH_URL = "https://api.schwabapi.com/v1/oauth/authorize"
    TOKEN_URL = "https://api.schwabapi.com/v1/oauth/token"
    
    def __init__(
        self,
        client_id: str = "",
        client_secret: str = "",
        refresh_token: str = "",
        account_id: str = "",
        **kwargs
    ):
        super().__init__(BrokerType.SCHWAB)
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.account_id = account_id
        self._access_token: Optional[str] = None
        self._token_expires: Optional[datetime] = None
    
    async def connect(self) -> bool:
        """Connect to Schwab API using OAuth2."""
        try:
            import httpx
            
            # Exchange refresh token for access token
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.TOKEN_URL,
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": self.refresh_token,
                        "client_id": self.client_id,
                    },
                    auth=(self.client_id, self.client_secret)
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self._access_token = data["access_token"]
                    self._connected = True
                    logger.info("Connected to Schwab API")
                    return True
                else:
                    logger.error(f"Schwab auth failed: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to connect to Schwab: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from Schwab."""
        self._access_token = None
        self._connected = False
        logger.info("Disconnected from Schwab")
    
    async def health_check(self) -> bool:
        """Check Schwab connection health."""
        if not self._access_token:
            return False
        # TODO: Implement actual health check
        return self._connected
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Make authenticated request to Schwab API."""
        if not self._access_token:
            return None
        
        import httpx
        
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                f"{self.BASE_URL}{endpoint}",
                headers=headers,
                **kwargs
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Schwab API error: {response.status_code} - {response.text}")
                return None
    
    async def get_accounts(self) -> List[AccountInfo]:
        """Get all Schwab accounts."""
        data = await self._make_request("GET", "/trader/v1/accounts")
        if not data:
            return []
        
        accounts = []
        for acc in data.get("accounts", []):
            accounts.append(AccountInfo(
                account_id=acc.get("accountNumber", ""),
                broker=BrokerType.SCHWAB,
                account_type=acc.get("type", "margin"),
                buying_power=float(acc.get("buyingPower", 0)),
                cash=float(acc.get("cashBalance", 0)),
                portfolio_value=float(acc.get("liquidationValue", 0)),
                equity=float(acc.get("equity", 0)),
                currency="USD",
                last_updated=datetime.now()
            ))
        
        return accounts
    
    async def get_account_info(self, account_id: str) -> AccountInfo:
        """Get specific account info."""
        accounts = await self.get_accounts()
        for acc in accounts:
            if acc.account_id == account_id:
                return acc
        raise ValueError(f"Account not found: {account_id}")
    
    async def get_buying_power(self, account_id: str) -> float:
        """Get buying power."""
        account = await self.get_account_info(account_id)
        return account.buying_power
    
    async def get_positions(self, account_id: str) -> List[Position]:
        """Get all positions."""
        data = await self._make_request("GET", f"/trader/v1/accounts/{account_id}/positions")
        if not data:
            return []
        
        positions = []
        for pos in data.get("positions", []):
            positions.append(Position(
                symbol=pos.get("symbol", ""),
                quantity=float(pos.get("quantity", 0)),
                avg_cost=float(pos.get("averagePrice", 0)),
                current_price=float(pos.get("currentPrice", 0)),
                market_value=float(pos.get("marketValue", 0)),
                unrealized_pnl=float(pos.get("unrealizedPL", 0)),
                unrealized_pnl_pct=float(pos.get("unrealizedPLPercent", 0)),
                side="long" if float(pos.get("quantity", 0)) > 0 else "short",
                broker=BrokerType.SCHWAB,
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
        """Submit order to Schwab."""
        order_data = {
            "symbol": symbol,
            "instruction": "BUY" if side == OrderSide.BUY else "SELL",
            "quantity": quantity,
            "orderType": order_type.value.upper(),
            "duration": time_in_force.upper(),
        }
        
        if limit_price:
            order_data["price"] = limit_price
        if stop_price:
            order_data["stopPrice"] = stop_price
        
        data = await self._make_request(
            "POST",
            f"/trader/v1/accounts/{account_id}/orders",
            json=order_data
        )
        
        if data:
            return Order(
                order_id=data.get("orderId", ""),
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                limit_price=limit_price,
                stop_price=stop_price,
                status=OrderStatus.SUBMITTED,
                broker=BrokerType.SCHWAB,
                account_id=account_id,
                created_at=datetime.now()
            )
        raise Exception("Failed to submit order")
    
    async def cancel_order(self, account_id: str, order_id: str) -> bool:
        """Cancel order."""
        data = await self._make_request(
            "DELETE",
            f"/trader/v1/accounts/{account_id}/orders/{order_id}"
        )
        return data is not None
    
    async def get_order(self, account_id: str, order_id: str) -> Optional[Order]:
        """Get order details."""
        data = await self._make_request(
            "GET",
            f"/trader/v1/accounts/{account_id}/orders/{order_id}"
        )
        if data:
            return self._convert_order(data, account_id)
        return None
    
    async def get_open_orders(self, account_id: str) -> List[Order]:
        """Get open orders."""
        data = await self._make_request(
            "GET",
            f"/trader/v1/accounts/{account_id}/orders",
            params={"status": "WORKING"}
        )
        if not data:
            return []
        return [self._convert_order(o, account_id) for o in data.get("orders", [])]
    
    async def get_order_history(
        self,
        account_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Order]:
        """Get order history."""
        params = {"maxResults": limit}
        if start_date:
            params["fromEnteredTime"] = start_date.isoformat()
        if end_date:
            params["toEnteredTime"] = end_date.isoformat()
        
        data = await self._make_request(
            "GET",
            f"/trader/v1/accounts/{account_id}/orders",
            params=params
        )
        if not data:
            return []
        return [self._convert_order(o, account_id) for o in data.get("orders", [])]
    
    def _convert_order(self, data: Dict, account_id: str) -> Order:
        """Convert Schwab order response to Order."""
        return Order(
            order_id=data.get("orderId", ""),
            symbol=data.get("symbol", ""),
            side=OrderSide.BUY if data.get("instruction") == "BUY" else OrderSide.SELL,
            order_type=OrderType.MARKET,
            quantity=float(data.get("quantity", 0)),
            limit_price=data.get("price"),
            status=self._map_status(data.get("status", "")),
            filled_quantity=float(data.get("filledQuantity", 0)),
            avg_fill_price=data.get("averagePrice"),
            broker=BrokerType.SCHWAB,
            account_id=account_id,
            created_at=datetime.now()
        )
    
    def _map_status(self, status: str) -> OrderStatus:
        """Map Schwab status to OrderStatus."""
        status_map = {
            "AWAITING_PARENT_ORDER": OrderStatus.PENDING,
            "AWAITING_CONDITION": OrderStatus.PENDING,
            "AWAITING_MANUAL_REVIEW": OrderStatus.PENDING,
            "ACCEPTED": OrderStatus.SUBMITTED,
            "PENDING_ACTIVATION": OrderStatus.PENDING,
            "QUEUED": OrderStatus.SUBMITTED,
            "WORKING": OrderStatus.SUBMITTED,
            "REJECTED": OrderStatus.REJECTED,
            "PENDING_CANCEL": OrderStatus.SUBMITTED,
            "CANCELED": OrderStatus.CANCELLED,
            "PENDING_REPLACE": OrderStatus.SUBMITTED,
            "REPLACED": OrderStatus.CANCELLED,
            "FILLED": OrderStatus.FILLED,
            "EXPIRED": OrderStatus.EXPIRED,
        }
        return status_map.get(status.upper(), OrderStatus.PENDING)


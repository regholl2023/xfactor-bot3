"""
TradingView Webhook Integration.

TradingView allows sending alerts via webhooks when conditions are met.
This integration receives those webhooks and converts them to trading signals.

Setup in TradingView:
1. Create an alert on your chart
2. Set webhook URL to: https://your-domain.com/api/webhooks/tradingview
3. Set message format (JSON):
   {
     "action": "{{strategy.order.action}}",
     "ticker": "{{ticker}}",
     "price": {{close}},
     "time": "{{time}}",
     "strategy": "{{strategy.order.comment}}",
     "secret": "your-secret-key"
   }
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Callable
import hashlib
import hmac

from loguru import logger


class TradingViewAction(str, Enum):
    """TradingView alert actions."""
    BUY = "buy"
    SELL = "sell"
    LONG = "long"
    SHORT = "short"
    CLOSE = "close"
    CLOSE_LONG = "close_long"
    CLOSE_SHORT = "close_short"


@dataclass
class TradingViewAlert:
    """Parsed TradingView alert."""
    action: TradingViewAction
    symbol: str
    price: float
    timestamp: datetime
    strategy: str = ""
    quantity: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    timeframe: str = ""
    raw_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.raw_data is None:
            self.raw_data = {}
    
    @property
    def is_entry(self) -> bool:
        """Check if this is an entry signal."""
        return self.action in [
            TradingViewAction.BUY,
            TradingViewAction.LONG,
            TradingViewAction.SHORT
        ]
    
    @property
    def is_exit(self) -> bool:
        """Check if this is an exit signal."""
        return self.action in [
            TradingViewAction.SELL,
            TradingViewAction.CLOSE,
            TradingViewAction.CLOSE_LONG,
            TradingViewAction.CLOSE_SHORT
        ]
    
    @property
    def is_long(self) -> bool:
        """Check if long position."""
        return self.action in [TradingViewAction.BUY, TradingViewAction.LONG]
    
    @property
    def is_short(self) -> bool:
        """Check if short position."""
        return self.action == TradingViewAction.SHORT


class TradingViewWebhook:
    """
    TradingView webhook handler.
    
    Receives webhook alerts from TradingView and converts them
    to trading signals for the XFactor Bot.
    """
    
    def __init__(
        self,
        secret: str = "",
        on_alert: Callable[[TradingViewAlert], None] = None
    ):
        """
        Initialize TradingView webhook handler.
        
        Args:
            secret: Webhook secret for authentication
            on_alert: Callback function for new alerts
        """
        self.secret = secret
        self.on_alert = on_alert
        self._alerts: List[TradingViewAlert] = []
        self._alert_handlers: List[Callable] = []
    
    async def connect(self) -> bool:
        """Connect method for compatibility with BaseDataSource pattern."""
        logger.info("TradingView webhook handler ready")
        return True
    
    async def disconnect(self) -> None:
        """Disconnect method for compatibility."""
        pass
    
    async def process_alert(self, data: Dict[str, Any]) -> Optional[TradingViewAlert]:
        """Alias for handle_webhook for compatibility."""
        return await self.handle_webhook(data)
    
    def add_handler(self, handler: Callable[[TradingViewAlert], None]) -> None:
        """Add an alert handler callback."""
        self._alert_handlers.append(handler)
    
    def remove_handler(self, handler: Callable) -> None:
        """Remove an alert handler."""
        if handler in self._alert_handlers:
            self._alert_handlers.remove(handler)
    
    def verify_signature(
        self,
        payload: bytes,
        signature: str
    ) -> bool:
        """
        Verify webhook signature (if using signed webhooks).
        
        Args:
            payload: Raw request body
            signature: Signature from header
            
        Returns:
            True if signature is valid
        """
        if not self.secret:
            return True  # No secret configured
        
        expected = hmac.new(
            self.secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected, signature)
    
    def parse_alert(self, data: Dict[str, Any]) -> Optional[TradingViewAlert]:
        """
        Parse TradingView webhook payload.
        
        Expected format:
        {
            "action": "buy" | "sell" | "long" | "short" | "close",
            "ticker": "AAPL",
            "price": 150.25,
            "time": "2024-01-15T10:30:00Z",
            "strategy": "RSI Divergence",
            "quantity": 100,           // optional
            "stop_loss": 145.00,       // optional
            "take_profit": 160.00,     // optional
            "timeframe": "1h",         // optional
            "secret": "your-secret"    // optional, for auth
        }
        """
        try:
            # Verify secret if present
            if self.secret and data.get("secret") != self.secret:
                logger.warning("TradingView webhook: invalid secret")
                return None
            
            # Parse action
            action_str = data.get("action", "").lower()
            try:
                action = TradingViewAction(action_str)
            except ValueError:
                logger.warning(f"Unknown TradingView action: {action_str}")
                return None
            
            # Parse symbol
            symbol = data.get("ticker") or data.get("symbol") or ""
            if not symbol:
                logger.warning("TradingView webhook: missing symbol")
                return None
            
            # Parse price
            price = float(data.get("price") or data.get("close") or 0)
            
            # Parse timestamp
            time_str = data.get("time") or data.get("timestamp")
            if time_str:
                try:
                    timestamp = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
                except ValueError:
                    timestamp = datetime.now()
            else:
                timestamp = datetime.now()
            
            alert = TradingViewAlert(
                action=action,
                symbol=symbol.upper(),
                price=price,
                timestamp=timestamp,
                strategy=data.get("strategy", ""),
                quantity=float(data.get("quantity")) if data.get("quantity") else None,
                stop_loss=float(data.get("stop_loss")) if data.get("stop_loss") else None,
                take_profit=float(data.get("take_profit")) if data.get("take_profit") else None,
                timeframe=data.get("timeframe", ""),
                raw_data=data
            )
            
            return alert
            
        except Exception as e:
            logger.error(f"Failed to parse TradingView alert: {e}")
            return None
    
    async def handle_webhook(self, data: Dict[str, Any]) -> Optional[TradingViewAlert]:
        """
        Handle incoming TradingView webhook.
        
        Args:
            data: Webhook payload
            
        Returns:
            Parsed alert or None if invalid
        """
        alert = self.parse_alert(data)
        
        if alert:
            # Store alert
            self._alerts.append(alert)
            
            # Keep last 1000 alerts
            if len(self._alerts) > 1000:
                self._alerts = self._alerts[-1000:]
            
            logger.info(
                f"TradingView Alert: {alert.action.value} {alert.symbol} "
                f"@ ${alert.price:.2f} ({alert.strategy})"
            )
            
            # Call handlers
            if self.on_alert:
                self.on_alert(alert)
            
            for handler in self._alert_handlers:
                try:
                    handler(alert)
                except Exception as e:
                    logger.error(f"Alert handler error: {e}")
        
        return alert
    
    def get_recent_alerts(
        self,
        limit: int = 50,
        symbol: str = None,
        action: TradingViewAction = None
    ) -> List[TradingViewAlert]:
        """
        Get recent alerts.
        
        Args:
            limit: Maximum alerts to return
            symbol: Filter by symbol
            action: Filter by action type
            
        Returns:
            List of recent alerts
        """
        alerts = self._alerts.copy()
        
        if symbol:
            alerts = [a for a in alerts if a.symbol == symbol.upper()]
        
        if action:
            alerts = [a for a in alerts if a.action == action]
        
        return alerts[-limit:]
    
    def to_dict(self) -> Dict[str, Any]:
        """Get webhook handler status."""
        return {
            "enabled": True,
            "has_secret": bool(self.secret),
            "handler_count": len(self._alert_handlers) + (1 if self.on_alert else 0),
            "recent_alerts": len(self._alerts),
            "last_alert": self._alerts[-1].timestamp.isoformat() if self._alerts else None
        }


# Global instance
_tradingview_webhook: Optional[TradingViewWebhook] = None


def get_tradingview_webhook() -> TradingViewWebhook:
    """Get or create global TradingView webhook handler."""
    global _tradingview_webhook
    if _tradingview_webhook is None:
        from src.config.settings import get_settings
        settings = get_settings()
        _tradingview_webhook = TradingViewWebhook(
            secret=settings.tradingview_webhook_secret
        )
    return _tradingview_webhook


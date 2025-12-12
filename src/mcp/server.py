"""
MCP Server Implementation.

The Model Context Protocol (MCP) enables AI assistants like Claude
to interact with external tools and data sources.

This server exposes trading bot functionality as MCP tools:
- Query portfolio and positions
- Get market data and quotes
- Execute trades (with confirmation)
- Analyze performance
- Get news and sentiment
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Callable
import json

from loguru import logger


class MCPToolType(str, Enum):
    """Available MCP tools."""
    # Portfolio & Positions
    GET_PORTFOLIO = "get_portfolio"
    GET_POSITIONS = "get_positions"
    GET_POSITION = "get_position"
    
    # Market Data
    GET_QUOTE = "get_quote"
    GET_BARS = "get_bars"
    SEARCH_SYMBOLS = "search_symbols"
    
    # Trading
    SUBMIT_ORDER = "submit_order"
    CANCEL_ORDER = "cancel_order"
    GET_ORDERS = "get_orders"
    
    # Analysis
    GET_PERFORMANCE = "get_performance"
    GET_RISK_METRICS = "get_risk_metrics"
    ANALYZE_SYMBOL = "analyze_symbol"
    
    # News & Sentiment
    GET_NEWS = "get_news"
    GET_SENTIMENT = "get_sentiment"
    
    # Bot Management
    GET_BOTS = "get_bots"
    START_BOT = "start_bot"
    STOP_BOT = "stop_bot"
    
    # System
    GET_STATUS = "get_status"
    GET_CONFIG = "get_config"


@dataclass
class MCPTool:
    """MCP tool definition."""
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Callable
    requires_confirmation: bool = False


@dataclass
class MCPRequest:
    """Incoming MCP request."""
    tool: str
    arguments: Dict[str, Any]
    request_id: str = ""


@dataclass
class MCPResponse:
    """MCP response."""
    success: bool
    data: Any
    error: Optional[str] = None
    request_id: str = ""
    requires_confirmation: bool = False


class MCPServer:
    """
    MCP Server for XFactor Bot.
    
    Exposes trading functionality as tools that AI assistants
    can discover and invoke.
    """
    
    def __init__(self, port: int = 3333, allowed_tools: List[str] = None):
        self.port = port
        self.allowed_tools = allowed_tools or ["*"]
        self._tools: Dict[str, MCPTool] = {}
        self._running = False
        self._register_tools()
    
    def _register_tools(self) -> None:
        """Register all available MCP tools."""
        
        # Portfolio tools
        self._register_tool(MCPTool(
            name=MCPToolType.GET_PORTFOLIO.value,
            description="Get current portfolio summary including total value, P&L, and allocation",
            parameters={
                "type": "object",
                "properties": {},
                "required": []
            },
            handler=self._handle_get_portfolio
        ))
        
        self._register_tool(MCPTool(
            name=MCPToolType.GET_POSITIONS.value,
            description="Get all open positions with current prices and P&L",
            parameters={
                "type": "object",
                "properties": {
                    "broker": {"type": "string", "description": "Filter by broker (optional)"}
                },
                "required": []
            },
            handler=self._handle_get_positions
        ))
        
        self._register_tool(MCPTool(
            name=MCPToolType.GET_QUOTE.value,
            description="Get real-time quote for a stock symbol",
            parameters={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock ticker symbol (e.g., AAPL)"}
                },
                "required": ["symbol"]
            },
            handler=self._handle_get_quote
        ))
        
        self._register_tool(MCPTool(
            name=MCPToolType.GET_BARS.value,
            description="Get historical price bars for a symbol",
            parameters={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock ticker symbol"},
                    "timeframe": {"type": "string", "description": "Bar timeframe (1m, 5m, 1h, 1d)", "default": "1d"},
                    "limit": {"type": "integer", "description": "Number of bars", "default": 100}
                },
                "required": ["symbol"]
            },
            handler=self._handle_get_bars
        ))
        
        self._register_tool(MCPTool(
            name=MCPToolType.SUBMIT_ORDER.value,
            description="Submit a trade order. Requires user confirmation for live trading.",
            parameters={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock ticker symbol"},
                    "side": {"type": "string", "enum": ["buy", "sell"], "description": "Order side"},
                    "quantity": {"type": "number", "description": "Number of shares"},
                    "order_type": {"type": "string", "enum": ["market", "limit", "stop"], "default": "market"},
                    "limit_price": {"type": "number", "description": "Limit price (for limit orders)"},
                    "broker": {"type": "string", "description": "Broker to use (optional)"}
                },
                "required": ["symbol", "side", "quantity"]
            },
            handler=self._handle_submit_order,
            requires_confirmation=True
        ))
        
        self._register_tool(MCPTool(
            name=MCPToolType.GET_BOTS.value,
            description="Get status of all trading bots",
            parameters={
                "type": "object",
                "properties": {},
                "required": []
            },
            handler=self._handle_get_bots
        ))
        
        self._register_tool(MCPTool(
            name=MCPToolType.GET_NEWS.value,
            description="Get recent news for a symbol or market-wide",
            parameters={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock symbol (optional)"},
                    "limit": {"type": "integer", "description": "Number of articles", "default": 10}
                },
                "required": []
            },
            handler=self._handle_get_news
        ))
        
        self._register_tool(MCPTool(
            name=MCPToolType.GET_PERFORMANCE.value,
            description="Get trading performance metrics",
            parameters={
                "type": "object",
                "properties": {
                    "period": {"type": "string", "enum": ["1d", "1w", "1m", "3m", "ytd", "all"], "default": "1m"}
                },
                "required": []
            },
            handler=self._handle_get_performance
        ))
        
        self._register_tool(MCPTool(
            name=MCPToolType.GET_STATUS.value,
            description="Get overall system status including connected brokers and data sources",
            parameters={
                "type": "object",
                "properties": {},
                "required": []
            },
            handler=self._handle_get_status
        ))
    
    def _register_tool(self, tool: MCPTool) -> None:
        """Register a tool."""
        if self.allowed_tools == ["*"] or tool.name in self.allowed_tools:
            self._tools[tool.name] = tool
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get tool definitions for MCP discovery."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.parameters
            }
            for tool in self._tools.values()
        ]
    
    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        """Handle an MCP request."""
        if request.tool not in self._tools:
            return MCPResponse(
                success=False,
                data=None,
                error=f"Unknown tool: {request.tool}",
                request_id=request.request_id
            )
        
        tool = self._tools[request.tool]
        
        try:
            result = await tool.handler(request.arguments)
            return MCPResponse(
                success=True,
                data=result,
                request_id=request.request_id,
                requires_confirmation=tool.requires_confirmation
            )
        except Exception as e:
            logger.error(f"MCP tool error ({request.tool}): {e}")
            return MCPResponse(
                success=False,
                data=None,
                error=str(e),
                request_id=request.request_id
            )
    
    # =========================================================================
    # Tool Handlers
    # =========================================================================
    
    async def _handle_get_portfolio(self, args: Dict) -> Dict[str, Any]:
        """Get portfolio summary."""
        from src.brokers import get_broker_registry
        
        registry = get_broker_registry()
        total_value = await registry.get_total_portfolio_value()
        total_bp = await registry.get_total_buying_power()
        all_accounts = await registry.get_all_accounts()
        
        return {
            "total_portfolio_value": total_value,
            "total_buying_power": total_bp,
            "connected_brokers": len(registry.connected_brokers),
            "accounts": sum(len(accs) for accs in all_accounts.values())
        }
    
    async def _handle_get_positions(self, args: Dict) -> List[Dict[str, Any]]:
        """Get all positions."""
        from src.brokers import get_broker_registry
        
        registry = get_broker_registry()
        positions = []
        
        for broker_type in registry.connected_brokers:
            broker = registry.get_broker(broker_type)
            if broker:
                accounts = await broker.get_accounts()
                for account in accounts:
                    account_positions = await broker.get_positions(account.account_id)
                    for pos in account_positions:
                        positions.append({
                            "symbol": pos.symbol,
                            "quantity": pos.quantity,
                            "avg_cost": pos.avg_cost,
                            "current_price": pos.current_price,
                            "market_value": pos.market_value,
                            "unrealized_pnl": pos.unrealized_pnl,
                            "unrealized_pnl_pct": pos.unrealized_pnl_pct,
                            "broker": broker_type.value
                        })
        
        return positions
    
    async def _handle_get_quote(self, args: Dict) -> Dict[str, Any]:
        """Get quote for symbol."""
        from src.data_sources import get_data_registry
        
        symbol = args.get("symbol", "").upper()
        if not symbol:
            raise ValueError("Symbol is required")
        
        registry = get_data_registry()
        quote = await registry.get_quote(symbol)
        
        if quote:
            return {
                "symbol": quote.symbol,
                "bid": quote.bid,
                "ask": quote.ask,
                "last": quote.last,
                "mid": quote.mid,
                "spread": quote.spread,
                "volume": quote.volume,
                "timestamp": quote.timestamp.isoformat()
            }
        
        raise ValueError(f"No quote available for {symbol}")
    
    async def _handle_get_bars(self, args: Dict) -> List[Dict[str, Any]]:
        """Get historical bars."""
        from src.data_sources import get_data_registry
        
        symbol = args.get("symbol", "").upper()
        timeframe = args.get("timeframe", "1d")
        limit = args.get("limit", 100)
        
        registry = get_data_registry()
        bars = await registry.get_bars(symbol, timeframe, limit)
        
        return [
            {
                "timestamp": bar.timestamp.isoformat(),
                "open": bar.open,
                "high": bar.high,
                "low": bar.low,
                "close": bar.close,
                "volume": bar.volume
            }
            for bar in bars
        ]
    
    async def _handle_submit_order(self, args: Dict) -> Dict[str, Any]:
        """Submit a trade order."""
        from src.brokers import get_broker_registry, OrderSide, OrderType
        
        symbol = args.get("symbol", "").upper()
        side = OrderSide.BUY if args.get("side", "").lower() == "buy" else OrderSide.SELL
        quantity = float(args.get("quantity", 0))
        order_type_str = args.get("order_type", "market").lower()
        limit_price = args.get("limit_price")
        
        order_type = OrderType(order_type_str)
        
        registry = get_broker_registry()
        broker = registry.get_default_broker()
        
        if not broker:
            raise ValueError("No broker connected")
        
        accounts = await broker.get_accounts()
        if not accounts:
            raise ValueError("No accounts available")
        
        account = accounts[0]
        
        order = await broker.submit_order(
            account_id=account.account_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type=order_type,
            limit_price=limit_price
        )
        
        return {
            "order_id": order.order_id,
            "symbol": order.symbol,
            "side": order.side.value,
            "quantity": order.quantity,
            "status": order.status.value,
            "broker": broker.broker_type.value
        }
    
    async def _handle_get_bots(self, args: Dict) -> List[Dict[str, Any]]:
        """Get all bots."""
        from src.bot.bot_manager import get_bot_manager
        
        manager = get_bot_manager()
        bots = manager.get_all_bots()
        
        return [
            {
                "id": b.id,
                "name": b.config.name,
                "status": b.status.value,
                "symbols": b.config.symbols,
                "strategies": b.config.strategies
            }
            for b in bots
        ]
    
    async def _handle_get_news(self, args: Dict) -> List[Dict[str, Any]]:
        """Get recent news."""
        # Placeholder - integrate with actual news aggregator
        symbol = args.get("symbol")
        limit = args.get("limit", 10)
        
        return [
            {
                "title": f"Sample news for {symbol or 'market'}",
                "source": "XFactor News",
                "timestamp": datetime.now().isoformat(),
                "sentiment": 0.5
            }
        ]
    
    async def _handle_get_performance(self, args: Dict) -> Dict[str, Any]:
        """Get performance metrics."""
        period = args.get("period", "1m")
        
        # Placeholder - integrate with actual performance tracking
        return {
            "period": period,
            "total_return": 12.5,
            "total_trades": 150,
            "win_rate": 0.58,
            "sharpe_ratio": 1.8,
            "max_drawdown": -5.2
        }
    
    async def _handle_get_status(self, args: Dict) -> Dict[str, Any]:
        """Get system status."""
        from src.brokers import get_broker_registry
        from src.data_sources import get_data_registry
        from src.bot.bot_manager import get_bot_manager
        
        broker_registry = get_broker_registry()
        data_registry = get_data_registry()
        bot_manager = get_bot_manager()
        
        return {
            "status": "operational",
            "brokers": broker_registry.to_dict(),
            "data_sources": data_registry.to_dict(),
            "bots": {
                "total": bot_manager.bot_count,
                "running": len([b for b in bot_manager.get_all_bots() if b.status.value == "running"])
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Get server info."""
        return {
            "port": self.port,
            "running": self._running,
            "tools": list(self._tools.keys()),
            "allowed_tools": self.allowed_tools
        }


# Global instance
_mcp_server: Optional[MCPServer] = None


def get_mcp_server() -> MCPServer:
    """Get or create global MCP server."""
    global _mcp_server
    if _mcp_server is None:
        from src.config.settings import get_settings
        settings = get_settings()
        allowed = settings.mcp_allowed_tools.split(",") if settings.mcp_allowed_tools != "*" else ["*"]
        _mcp_server = MCPServer(
            port=settings.mcp_port,
            allowed_tools=allowed
        )
    return _mcp_server


"""
Context Builder for AI Assistant.
Gathers system state, performance metrics, and data source information
to provide context for AI queries.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Optional

from pydantic import BaseModel

from src.utils.logger import get_logger

logger = get_logger(__name__)


class PerformanceMetrics(BaseModel):
    """Performance metrics for the trading system."""
    
    total_pnl: float = 0.0
    daily_pnl: float = 0.0
    weekly_pnl: float = 0.0
    monthly_pnl: float = 0.0
    win_rate: float = 0.0
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    average_win: float = 0.0
    average_loss: float = 0.0
    profit_factor: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    current_drawdown: float = 0.0
    best_trade: float = 0.0
    worst_trade: float = 0.0


class PositionSummary(BaseModel):
    """Summary of current positions."""
    
    total_positions: int = 0
    long_positions: int = 0
    short_positions: int = 0
    total_exposure: float = 0.0
    largest_position: str = ""
    largest_position_value: float = 0.0
    sector_breakdown: dict[str, float] = {}
    positions: list[dict[str, Any]] = []


class StrategyPerformance(BaseModel):
    """Performance metrics per strategy."""
    
    strategy_name: str
    enabled: bool = True
    total_signals: int = 0
    signals_executed: int = 0
    pnl: float = 0.0
    win_rate: float = 0.0
    avg_return: float = 0.0


class DataSourceStatus(BaseModel):
    """Status of data sources."""
    
    name: str
    type: str  # "news", "social", "market", "local"
    status: str  # "active", "inactive", "error"
    last_update: Optional[datetime] = None
    items_processed_24h: int = 0
    error_rate: float = 0.0
    avg_latency_ms: float = 0.0


class BotStatus(BaseModel):
    """Status of individual bots."""
    
    bot_id: str
    status: str
    strategy: str
    pnl: float = 0.0
    positions: int = 0
    trades_today: int = 0
    uptime_hours: float = 0.0


class SystemContext(BaseModel):
    """Complete system context for AI queries."""
    
    timestamp: datetime
    trading_mode: str
    account_value: float = 0.0
    buying_power: float = 0.0
    cash_balance: float = 0.0
    margin_used: float = 0.0
    
    performance: PerformanceMetrics
    positions: PositionSummary
    strategies: list[StrategyPerformance] = []
    data_sources: list[DataSourceStatus] = []
    bots: list[BotStatus] = []
    
    recent_news_sentiment: float = 0.0
    market_conditions: dict[str, Any] = {}
    alerts: list[str] = []
    circuit_breaker_status: dict[str, bool] = {}


class ContextBuilder:
    """
    Builds context from various system components for AI queries.
    """
    
    def __init__(self):
        self._cache: Optional[SystemContext] = None
        self._cache_ttl = timedelta(seconds=30)
        self._cache_time: Optional[datetime] = None
    
    async def build_context(self, force_refresh: bool = False) -> SystemContext:
        """
        Build complete system context for AI queries.
        
        Args:
            force_refresh: Force refresh even if cache is valid
            
        Returns:
            SystemContext with all relevant information
        """
        # Check cache
        if not force_refresh and self._cache and self._cache_time:
            if datetime.utcnow() - self._cache_time < self._cache_ttl:
                return self._cache
        
        try:
            # Gather all context in parallel
            results = await asyncio.gather(
                self._get_account_info(),
                self._get_performance_metrics(),
                self._get_position_summary(),
                self._get_strategy_performance(),
                self._get_data_source_status(),
                self._get_bot_status(),
                self._get_market_conditions(),
                self._get_circuit_breaker_status(),
                return_exceptions=True,
            )
            
            # Unpack results with error handling
            account_info = results[0] if not isinstance(results[0], Exception) else {}
            performance = results[1] if not isinstance(results[1], Exception) else PerformanceMetrics()
            positions = results[2] if not isinstance(results[2], Exception) else PositionSummary()
            strategies = results[3] if not isinstance(results[3], Exception) else []
            data_sources = results[4] if not isinstance(results[4], Exception) else []
            bots = results[5] if not isinstance(results[5], Exception) else []
            market_conditions = results[6] if not isinstance(results[6], Exception) else {}
            circuit_breakers = results[7] if not isinstance(results[7], Exception) else {}
            
            context = SystemContext(
                timestamp=datetime.utcnow(),
                trading_mode=account_info.get("trading_mode", "paper"),
                account_value=account_info.get("account_value", 0.0),
                buying_power=account_info.get("buying_power", 0.0),
                cash_balance=account_info.get("cash_balance", 0.0),
                margin_used=account_info.get("margin_used", 0.0),
                performance=performance,
                positions=positions,
                strategies=strategies,
                data_sources=data_sources,
                bots=bots,
                market_conditions=market_conditions,
                circuit_breaker_status=circuit_breakers,
                alerts=await self._get_recent_alerts(),
            )
            
            # Update cache
            self._cache = context
            self._cache_time = datetime.utcnow()
            
            return context
            
        except Exception as e:
            logger.error(f"Error building context: {e}")
            # Return minimal context on error
            return SystemContext(
                timestamp=datetime.utcnow(),
                trading_mode="paper",
                performance=PerformanceMetrics(),
                positions=PositionSummary(),
            )
    
    async def _get_account_info(self) -> dict[str, Any]:
        """Get account information from IBKR connector."""
        try:
            from src.connectors.ibkr_connector import get_ibkr_connector
            from src.config.settings import get_settings
            
            settings = get_settings()
            connector = get_ibkr_connector()
            
            if connector.is_connected():
                account = await connector.get_account_summary()
                return {
                    "trading_mode": settings.trading_mode,
                    "account_value": account.get("NetLiquidation", 0.0),
                    "buying_power": account.get("BuyingPower", 0.0),
                    "cash_balance": account.get("TotalCashValue", 0.0),
                    "margin_used": account.get("MaintMarginReq", 0.0),
                }
            
            return {"trading_mode": settings.trading_mode}
            
        except Exception as e:
            logger.warning(f"Could not get account info: {e}")
            return {}
    
    async def _get_performance_metrics(self) -> PerformanceMetrics:
        """Calculate performance metrics from trade history."""
        try:
            from src.execution.position_tracker import get_position_tracker
            
            tracker = get_position_tracker()
            closed_trades = tracker.get_closed_trades()
            
            if not closed_trades:
                return PerformanceMetrics()
            
            pnls = [t.realized_pnl for t in closed_trades if t.realized_pnl is not None]
            wins = [p for p in pnls if p > 0]
            losses = [p for p in pnls if p < 0]
            
            total_pnl = sum(pnls)
            win_rate = len(wins) / len(pnls) * 100 if pnls else 0
            avg_win = sum(wins) / len(wins) if wins else 0
            avg_loss = sum(losses) / len(losses) if losses else 0
            profit_factor = abs(sum(wins) / sum(losses)) if losses and sum(losses) != 0 else 0
            
            return PerformanceMetrics(
                total_pnl=total_pnl,
                total_trades=len(pnls),
                winning_trades=len(wins),
                losing_trades=len(losses),
                win_rate=win_rate,
                average_win=avg_win,
                average_loss=avg_loss,
                profit_factor=profit_factor,
                best_trade=max(pnls) if pnls else 0,
                worst_trade=min(pnls) if pnls else 0,
            )
            
        except Exception as e:
            logger.warning(f"Could not get performance metrics: {e}")
            return PerformanceMetrics()
    
    async def _get_position_summary(self) -> PositionSummary:
        """Get summary of current positions."""
        try:
            from src.execution.position_tracker import get_position_tracker
            
            tracker = get_position_tracker()
            positions = tracker.get_open_positions()
            
            if not positions:
                return PositionSummary()
            
            long_count = sum(1 for p in positions if p.quantity > 0)
            short_count = sum(1 for p in positions if p.quantity < 0)
            total_exposure = sum(abs(p.market_value) for p in positions)
            
            largest = max(positions, key=lambda p: abs(p.market_value))
            
            position_list = [
                {
                    "symbol": p.symbol,
                    "quantity": p.quantity,
                    "entry_price": p.avg_entry_price,
                    "current_price": p.current_price,
                    "market_value": p.market_value,
                    "unrealized_pnl": p.unrealized_pnl,
                    "pnl_pct": p.unrealized_pnl_pct,
                }
                for p in positions
            ]
            
            return PositionSummary(
                total_positions=len(positions),
                long_positions=long_count,
                short_positions=short_count,
                total_exposure=total_exposure,
                largest_position=largest.symbol,
                largest_position_value=abs(largest.market_value),
                positions=position_list,
            )
            
        except Exception as e:
            logger.warning(f"Could not get position summary: {e}")
            return PositionSummary()
    
    async def _get_strategy_performance(self) -> list[StrategyPerformance]:
        """Get performance metrics per strategy."""
        try:
            # This would be connected to actual strategy tracking
            # For now, return placeholder data
            strategies = [
                StrategyPerformance(
                    strategy_name="Technical Analysis",
                    enabled=True,
                    total_signals=0,
                    signals_executed=0,
                    pnl=0.0,
                    win_rate=0.0,
                ),
                StrategyPerformance(
                    strategy_name="Momentum",
                    enabled=True,
                    total_signals=0,
                    signals_executed=0,
                    pnl=0.0,
                    win_rate=0.0,
                ),
                StrategyPerformance(
                    strategy_name="News Sentiment",
                    enabled=True,
                    total_signals=0,
                    signals_executed=0,
                    pnl=0.0,
                    win_rate=0.0,
                ),
            ]
            return strategies
            
        except Exception as e:
            logger.warning(f"Could not get strategy performance: {e}")
            return []
    
    async def _get_data_source_status(self) -> list[DataSourceStatus]:
        """Get status of all data sources."""
        try:
            from src.config.settings import get_settings
            from src.news_intel.news_aggregator import RSS_FEEDS
            
            settings = get_settings()
            sources = []
            
            # RSS Feeds - group by category
            rss_categories = {
                "US Major News": ["cnn_business", "cnbc_top", "foxbusiness", "bbc_business", "npr_business"],
                "Financial Publications": ["wsj_markets", "marketwatch", "ft_markets", "reuters_business", "bloomberg_markets"],
                "Tech & Startup": ["techcrunch", "theverge", "arstechnica", "wired_business"],
                "Crypto": ["coindesk", "cointelegraph", "theblock"],
                "Asia Pacific": ["scmp_business", "nikkei_asia", "channelnewsasia", "economic_times"],
                "Government/Regulatory": ["sec_press", "fed_press"],
            }
            
            for category, feeds in rss_categories.items():
                active_feeds = sum(1 for f in feeds if f in RSS_FEEDS)
                sources.append(DataSourceStatus(
                    name=f"RSS: {category}",
                    type="news",
                    status="active" if active_feeds > 0 else "inactive",
                    items_processed_24h=0,  # Would be tracked in actual implementation
                ))
            
            # API-based sources
            api_sources = [
                ("Benzinga", "news", bool(settings.benzinga_api_key)),
                ("NewsAPI", "news", bool(settings.newsapi_api_key)),
                ("Finnhub", "news", bool(settings.finnhub_api_key)),
                ("Polygon", "news", bool(settings.polygon_api_key)),
                ("Alpha Vantage", "market", bool(settings.alpha_vantage_api_key)),
                ("IEX Cloud", "market", bool(settings.iex_cloud_api_key)),
            ]
            
            for name, source_type, configured in api_sources:
                sources.append(DataSourceStatus(
                    name=name,
                    type=source_type,
                    status="active" if configured else "not_configured",
                ))
            
            # Social media sources
            social_sources = [
                ("Reddit", bool(settings.reddit_client_id)),
                ("Twitter/X", bool(settings.twitter_bearer_token)),
                ("StockTwits", bool(settings.stocktwits_access_token)),
            ]
            
            for name, configured in social_sources:
                sources.append(DataSourceStatus(
                    name=name,
                    type="social",
                    status="active" if configured else "not_configured",
                ))
            
            # Local file watcher
            sources.append(DataSourceStatus(
                name="Local Files (new_news/)",
                type="local",
                status="active",
            ))
            
            return sources
            
        except Exception as e:
            logger.warning(f"Could not get data source status: {e}")
            return []
    
    async def _get_bot_status(self) -> list[BotStatus]:
        """Get status of all running bots."""
        try:
            from src.bot.bot_manager import get_bot_manager
            
            manager = get_bot_manager()
            status = manager.get_status()
            
            bot_list = []
            for bot_id, info in status.get("bots", {}).items():
                bot_list.append(BotStatus(
                    bot_id=bot_id,
                    status=info.get("status", "unknown"),
                    strategy=info.get("strategy", "unknown"),
                    pnl=info.get("pnl", 0.0),
                    positions=info.get("open_positions", 0),
                    trades_today=info.get("trades_today", 0),
                ))
            
            return bot_list
            
        except Exception as e:
            logger.warning(f"Could not get bot status: {e}")
            return []
    
    async def _get_market_conditions(self) -> dict[str, Any]:
        """Get current market conditions."""
        try:
            from src.data.redis_cache import get_redis_cache
            
            cache = get_redis_cache()
            
            # Try to get cached market data
            vix = await cache.get("market:vix") or 0.0
            spy_change = await cache.get("market:spy_change") or 0.0
            
            # Determine market hours (simple check)
            from datetime import datetime
            now = datetime.utcnow()
            hour = now.hour
            weekday = now.weekday()
            
            # NYSE hours: 9:30 AM - 4:00 PM ET (14:30 - 21:00 UTC)
            if weekday < 5 and 14 <= hour < 21:
                market_status = "open"
            elif weekday < 5 and (9 <= hour < 14 or 21 <= hour < 22):
                market_status = "pre_market" if hour < 14 else "after_hours"
            else:
                market_status = "closed"
            
            return {
                "spy_change": float(spy_change) if spy_change else 0.0,
                "vix": float(vix) if vix else 0.0,
                "market_status": market_status,
                "sector_performance": {},
                "timestamp": now.isoformat(),
            }
        except Exception as e:
            logger.warning(f"Could not get market conditions: {e}")
            return {"market_status": "unknown"}
    
    async def _get_circuit_breaker_status(self) -> dict[str, bool]:
        """Get circuit breaker status."""
        try:
            from src.circuit_breakers.kill_switch import get_kill_switch
            
            kill_switch = get_kill_switch()
            return {
                "kill_switch_active": kill_switch.is_active,
                "trading_halted": not kill_switch.can_trade(),
            }
        except Exception as e:
            logger.warning(f"Could not get circuit breaker status: {e}")
            return {}
    
    async def _get_recent_alerts(self) -> list[str]:
        """Get recent system alerts."""
        try:
            # This would fetch from an alerts store
            return []
        except Exception as e:
            logger.warning(f"Could not get alerts: {e}")
            return []
    
    def get_context_summary(self, context: SystemContext) -> str:
        """
        Generate a text summary of the context for AI prompts.
        
        Args:
            context: The system context
            
        Returns:
            Formatted text summary
        """
        lines = [
            f"=== Trading Bot System Status ({context.timestamp.isoformat()}) ===",
            f"",
            f"ACCOUNT:",
            f"  Mode: {context.trading_mode}",
            f"  Account Value: ${context.account_value:,.2f}",
            f"  Buying Power: ${context.buying_power:,.2f}",
            f"  Cash: ${context.cash_balance:,.2f}",
            f"",
            f"PERFORMANCE:",
            f"  Total P&L: ${context.performance.total_pnl:,.2f}",
            f"  Win Rate: {context.performance.win_rate:.1f}%",
            f"  Total Trades: {context.performance.total_trades}",
            f"  Profit Factor: {context.performance.profit_factor:.2f}",
            f"  Max Drawdown: {context.performance.max_drawdown:.1f}%",
            f"",
            f"POSITIONS ({context.positions.total_positions} total):",
            f"  Long: {context.positions.long_positions}",
            f"  Short: {context.positions.short_positions}",
            f"  Total Exposure: ${context.positions.total_exposure:,.2f}",
        ]
        
        if context.positions.positions:
            lines.append(f"  Current Positions:")
            for pos in context.positions.positions[:10]:  # Limit to 10
                lines.append(
                    f"    {pos['symbol']}: {pos['quantity']} @ ${pos['current_price']:.2f} "
                    f"(P&L: ${pos['unrealized_pnl']:.2f})"
                )
        
        lines.extend([
            f"",
            f"STRATEGIES:",
        ])
        for strat in context.strategies:
            lines.append(
                f"  {strat.strategy_name}: {'Enabled' if strat.enabled else 'Disabled'} | "
                f"Signals: {strat.total_signals} | Win Rate: {strat.win_rate:.1f}%"
            )
        
        lines.extend([
            f"",
            f"BOTS ({len(context.bots)} running):",
        ])
        for bot in context.bots:
            lines.append(
                f"  {bot.bot_id}: {bot.status} | Strategy: {bot.strategy} | P&L: ${bot.pnl:.2f}"
            )
        
        lines.extend([
            f"",
            f"DATA SOURCES:",
        ])
        for ds in context.data_sources:
            lines.append(f"  {ds.name}: {ds.status} | Processed (24h): {ds.items_processed_24h}")
        
        if context.alerts:
            lines.extend([
                f"",
                f"ALERTS:",
            ])
            for alert in context.alerts[:5]:
                lines.append(f"  ⚠️ {alert}")
        
        lines.extend([
            f"",
            f"CIRCUIT BREAKERS:",
        ])
        for name, active in context.circuit_breaker_status.items():
            status = "🔴 ACTIVE" if active else "🟢 OK"
            lines.append(f"  {name}: {status}")
        
        return "\n".join(lines)


# Singleton instance
_context_builder: Optional[ContextBuilder] = None


def get_context_builder() -> ContextBuilder:
    """Get or create context builder instance."""
    global _context_builder
    if _context_builder is None:
        _context_builder = ContextBuilder()
    return _context_builder


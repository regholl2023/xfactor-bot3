"""
Individual bot instance that runs in its own thread.
"""

import asyncio
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Any, Callable
import uuid

from loguru import logger


class BotStatus(str, Enum):
    """Bot status states."""
    CREATED = "created"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class BotConfig:
    """Configuration for a bot instance."""
    name: str
    description: str = ""
    
    # Trading configuration
    symbols: list[str] = field(default_factory=list)
    strategies: list[str] = field(default_factory=lambda: ["Technical", "Momentum"])
    
    # Strategy weights
    strategy_weights: dict[str, float] = field(default_factory=lambda: {
        "Technical": 0.6,
        "Momentum": 0.5,
        "MeanReversion": 0.4,
        "NewsSentiment": 0.4,
    })
    
    # Risk parameters (per bot)
    max_position_size: float = 25000.0
    max_positions: int = 10
    max_daily_loss_pct: float = 2.0
    
    # Execution settings
    trade_frequency_seconds: int = 60
    use_paper_trading: bool = True
    
    # News settings
    enable_news_trading: bool = True
    news_sentiment_threshold: float = 0.5
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "symbols": self.symbols,
            "strategies": self.strategies,
            "strategy_weights": self.strategy_weights,
            "max_position_size": self.max_position_size,
            "max_positions": self.max_positions,
            "max_daily_loss_pct": self.max_daily_loss_pct,
            "trade_frequency_seconds": self.trade_frequency_seconds,
            "use_paper_trading": self.use_paper_trading,
            "enable_news_trading": self.enable_news_trading,
            "news_sentiment_threshold": self.news_sentiment_threshold,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "BotConfig":
        return cls(**data)


@dataclass
class BotStats:
    """Runtime statistics for a bot."""
    trades_today: int = 0
    signals_generated: int = 0
    daily_pnl: float = 0.0
    total_pnl: float = 0.0
    win_rate: float = 0.0
    open_positions: int = 0
    last_trade_time: Optional[datetime] = None
    errors_count: int = 0
    uptime_seconds: float = 0.0


class BotInstance:
    """
    Individual trading bot instance that runs in its own thread.
    
    Each bot can:
    - Trade a specific set of symbols
    - Use different strategy combinations
    - Have its own risk limits
    - Run independently of other bots
    """
    
    MAX_BOTS = 10  # Maximum number of bots allowed
    
    def __init__(self, config: BotConfig, bot_id: str = None):
        """
        Initialize a bot instance.
        
        Args:
            config: Bot configuration
            bot_id: Optional bot ID (auto-generated if not provided)
        """
        self.id = bot_id or str(uuid.uuid4())[:8]
        self.config = config
        self.status = BotStatus.CREATED
        self.stats = BotStats()
        
        self._thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        
        self._created_at = datetime.utcnow()
        self._started_at: Optional[datetime] = None
        self._stopped_at: Optional[datetime] = None
        
        self._callbacks: dict[str, list[Callable]] = {
            "on_start": [],
            "on_stop": [],
            "on_trade": [],
            "on_signal": [],
            "on_error": [],
        }
        
        logger.info(f"Bot {self.id} created: {config.name}")
    
    @property
    def is_running(self) -> bool:
        return self.status == BotStatus.RUNNING
    
    @property
    def is_paused(self) -> bool:
        return self.status == BotStatus.PAUSED
    
    @property
    def uptime(self) -> float:
        """Get uptime in seconds."""
        if self._started_at:
            end_time = self._stopped_at or datetime.utcnow()
            return (end_time - self._started_at).total_seconds()
        return 0.0
    
    def register_callback(self, event: str, callback: Callable) -> None:
        """Register a callback for an event."""
        if event in self._callbacks:
            self._callbacks[event].append(callback)
    
    def _emit(self, event: str, *args, **kwargs) -> None:
        """Emit an event to callbacks."""
        for callback in self._callbacks.get(event, []):
            try:
                callback(self, *args, **kwargs)
            except Exception as e:
                logger.error(f"Bot {self.id} callback error: {e}")
    
    def start(self) -> bool:
        """Start the bot in a new thread."""
        if self.status in (BotStatus.RUNNING, BotStatus.STARTING):
            logger.warning(f"Bot {self.id} is already running")
            return False
        
        self.status = BotStatus.STARTING
        self._stop_event.clear()
        self._pause_event.clear()
        
        self._thread = threading.Thread(
            target=self._run_thread,
            name=f"Bot-{self.id}",
            daemon=True,
        )
        self._thread.start()
        
        return True
    
    def stop(self) -> bool:
        """Stop the bot."""
        if self.status not in (BotStatus.RUNNING, BotStatus.PAUSED):
            return False
        
        self.status = BotStatus.STOPPING
        self._stop_event.set()
        self._pause_event.set()  # Unpause if paused
        
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=10)
        
        self.status = BotStatus.STOPPED
        self._stopped_at = datetime.utcnow()
        self._emit("on_stop")
        
        logger.info(f"Bot {self.id} stopped")
        return True
    
    def pause(self) -> bool:
        """Pause the bot (keeps thread alive but stops trading)."""
        if self.status != BotStatus.RUNNING:
            return False
        
        self._pause_event.set()
        self.status = BotStatus.PAUSED
        logger.info(f"Bot {self.id} paused")
        return True
    
    def resume(self) -> bool:
        """Resume the bot from paused state."""
        if self.status != BotStatus.PAUSED:
            return False
        
        self._pause_event.clear()
        self.status = BotStatus.RUNNING
        logger.info(f"Bot {self.id} resumed")
        return True
    
    def _run_thread(self) -> None:
        """Main thread entry point."""
        try:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._loop.run_until_complete(self._run_async())
        except Exception as e:
            self.status = BotStatus.ERROR
            self.stats.errors_count += 1
            logger.error(f"Bot {self.id} error: {e}")
            self._emit("on_error", e)
        finally:
            if self._loop:
                self._loop.close()
    
    async def _run_async(self) -> None:
        """Main async trading loop."""
        self.status = BotStatus.RUNNING
        self._started_at = datetime.utcnow()
        self._emit("on_start")
        
        logger.info(f"Bot {self.id} ({self.config.name}) started trading")
        logger.info(f"  Symbols: {self.config.symbols}")
        logger.info(f"  Strategies: {self.config.strategies}")
        
        while not self._stop_event.is_set():
            try:
                # Check if paused
                if self._pause_event.is_set():
                    await asyncio.sleep(1)
                    continue
                
                # Run trading cycle
                await self._trading_cycle()
                
                # Update stats
                self.stats.uptime_seconds = self.uptime
                
                # Wait for next cycle
                await asyncio.sleep(self.config.trade_frequency_seconds)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.stats.errors_count += 1
                logger.error(f"Bot {self.id} cycle error: {e}")
                await asyncio.sleep(5)  # Brief pause on error
    
    async def _trading_cycle(self) -> None:
        """Execute one trading cycle."""
        # This is where the actual trading logic would run
        # For now, it's a placeholder that would integrate with:
        # - Market data
        # - Strategy analysis
        # - Signal generation
        # - Order execution
        
        for symbol in self.config.symbols:
            # Simulate signal generation
            # In production, this would call the actual strategies
            pass
    
    def update_config(self, updates: dict) -> None:
        """Update bot configuration (while running or stopped)."""
        for key, value in updates.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        logger.info(f"Bot {self.id} config updated: {list(updates.keys())}")
    
    def get_status(self) -> dict:
        """Get bot status and stats."""
        return {
            "id": self.id,
            "name": self.config.name,
            "description": self.config.description,
            "status": self.status.value,
            "created_at": self._created_at.isoformat(),
            "started_at": self._started_at.isoformat() if self._started_at else None,
            "stopped_at": self._stopped_at.isoformat() if self._stopped_at else None,
            "uptime_seconds": self.uptime,
            "config": self.config.to_dict(),
            "stats": {
                "trades_today": self.stats.trades_today,
                "signals_generated": self.stats.signals_generated,
                "daily_pnl": self.stats.daily_pnl,
                "total_pnl": self.stats.total_pnl,
                "win_rate": self.stats.win_rate,
                "open_positions": self.stats.open_positions,
                "errors_count": self.stats.errors_count,
            },
        }


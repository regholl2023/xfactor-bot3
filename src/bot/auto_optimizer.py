"""
Auto-Optimizer for Trading Bots.

Automatically analyzes bot performance and adjusts strategy parameters
for maximum profit. Uses adaptive algorithms to learn from trading outcomes.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Any, Callable
from collections import deque
import statistics
import json

from loguru import logger


class OptimizationMode(Enum):
    """Optimization modes for different risk profiles."""
    CONSERVATIVE = "conservative"    # Small, careful adjustments
    MODERATE = "moderate"            # Balanced adjustments
    AGGRESSIVE = "aggressive"        # Larger, faster adjustments
    CUSTOM = "custom"                # User-defined parameters


class AdjustmentType(Enum):
    """Types of parameter adjustments."""
    INCREASE = "increase"
    DECREASE = "decrease"
    NO_CHANGE = "no_change"
    RESET = "reset"


@dataclass
class PerformanceMetrics:
    """Performance metrics for a trading bot."""
    bot_id: str
    timestamp: datetime
    
    # Core metrics
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_pnl: float = 0.0
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    
    # Calculated metrics
    win_rate: float = 0.0
    profit_factor: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    
    # Recent performance (last N trades)
    recent_win_rate: float = 0.0
    recent_pnl: float = 0.0
    trend: str = "neutral"  # improving, declining, neutral
    
    def to_dict(self) -> dict:
        return {
            "bot_id": self.bot_id,
            "timestamp": self.timestamp.isoformat(),
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "total_pnl": self.total_pnl,
            "win_rate": self.win_rate,
            "profit_factor": self.profit_factor,
            "max_drawdown": self.max_drawdown,
            "sharpe_ratio": self.sharpe_ratio,
            "recent_win_rate": self.recent_win_rate,
            "recent_pnl": self.recent_pnl,
            "trend": self.trend,
        }


@dataclass
class ParameterAdjustment:
    """Record of a parameter adjustment."""
    parameter_name: str
    old_value: Any
    new_value: Any
    adjustment_type: AdjustmentType
    reason: str
    timestamp: datetime = field(default_factory=datetime.now)
    performance_before: Optional[float] = None
    performance_after: Optional[float] = None
    
    def to_dict(self) -> dict:
        return {
            "parameter": self.parameter_name,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "adjustment": self.adjustment_type.value,
            "reason": self.reason,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class OptimizationConfig:
    """Configuration for auto-optimization."""
    enabled: bool = False
    mode: OptimizationMode = OptimizationMode.MODERATE
    
    # Analysis settings
    min_trades_for_analysis: int = 10      # Minimum trades before making adjustments
    analysis_window_hours: int = 24        # Time window for recent performance
    evaluation_interval_minutes: int = 60  # How often to evaluate and adjust
    
    # Adjustment limits
    max_adjustment_pct: float = 0.20       # Maximum 20% change per adjustment
    min_adjustment_pct: float = 0.05       # Minimum 5% change to be meaningful
    cooldown_minutes: int = 30             # Wait time between adjustments
    
    # Performance thresholds
    min_win_rate: float = 0.40             # Below this, reduce position sizes
    target_win_rate: float = 0.55          # Target win rate
    max_drawdown_pct: float = 0.15         # Maximum allowed drawdown
    min_profit_factor: float = 1.2         # Minimum profit factor target
    
    # Safety limits
    max_adjustments_per_day: int = 5       # Limit adjustments per day
    revert_on_worse_performance: bool = True
    
    def to_dict(self) -> dict:
        return {
            "enabled": self.enabled,
            "mode": self.mode.value,
            "min_trades_for_analysis": self.min_trades_for_analysis,
            "analysis_window_hours": self.analysis_window_hours,
            "evaluation_interval_minutes": self.evaluation_interval_minutes,
            "max_adjustment_pct": self.max_adjustment_pct,
            "min_win_rate": self.min_win_rate,
            "target_win_rate": self.target_win_rate,
            "max_drawdown_pct": self.max_drawdown_pct,
            "max_adjustments_per_day": self.max_adjustments_per_day,
        }


class BotAutoOptimizer:
    """
    Auto-optimizer for a single trading bot.
    
    Monitors performance and dynamically adjusts strategy parameters
    to improve profitability.
    """
    
    # Parameters that can be auto-adjusted
    ADJUSTABLE_PARAMETERS = {
        # Risk management
        "stop_loss_pct": {"min": 0.01, "max": 0.10, "direction": "minimize_loss"},
        "take_profit_pct": {"min": 0.02, "max": 0.20, "direction": "maximize_profit"},
        "position_size_pct": {"min": 0.01, "max": 0.10, "direction": "optimize"},
        "max_positions": {"min": 1, "max": 10, "direction": "optimize"},
        
        # Technical indicators
        "rsi_oversold": {"min": 20, "max": 40, "direction": "optimize"},
        "rsi_overbought": {"min": 60, "max": 80, "direction": "optimize"},
        "ma_fast_period": {"min": 5, "max": 20, "direction": "optimize"},
        "ma_slow_period": {"min": 20, "max": 100, "direction": "optimize"},
        
        # Momentum
        "momentum_threshold": {"min": 0.02, "max": 0.15, "direction": "optimize"},
        "volume_threshold": {"min": 1.0, "max": 3.0, "direction": "optimize"},
        
        # Signal thresholds
        "min_confidence": {"min": 0.5, "max": 0.9, "direction": "optimize"},
        "signal_strength_threshold": {"min": 0.3, "max": 0.8, "direction": "optimize"},
    }
    
    def __init__(
        self,
        bot_id: str,
        get_bot_params: Callable[[], dict],
        set_bot_params: Callable[[dict], None],
        config: Optional[OptimizationConfig] = None,
    ):
        """
        Initialize the auto-optimizer.
        
        Args:
            bot_id: Unique identifier for the bot
            get_bot_params: Callback to get current bot parameters
            set_bot_params: Callback to set bot parameters
            config: Optimization configuration
        """
        self.bot_id = bot_id
        self._get_params = get_bot_params
        self._set_params = set_bot_params
        self.config = config or OptimizationConfig()
        
        # Performance tracking
        self._metrics_history: deque[PerformanceMetrics] = deque(maxlen=1000)
        self._trade_results: deque[dict] = deque(maxlen=500)
        self._pnl_history: deque[float] = deque(maxlen=1000)
        
        # Adjustment tracking
        self._adjustments: list[ParameterAdjustment] = []
        self._last_adjustment_time: Optional[datetime] = None
        self._adjustments_today: int = 0
        self._last_reset_date: Optional[datetime] = None
        
        # Baseline tracking
        self._baseline_params: dict = {}
        self._best_params: dict = {}
        self._best_performance: float = 0.0
        
        # State
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    @property
    def is_enabled(self) -> bool:
        return self.config.enabled
    
    @property
    def is_running(self) -> bool:
        return self._running
    
    def enable(self) -> None:
        """Enable auto-optimization."""
        self.config.enabled = True
        # Save current params as baseline
        self._baseline_params = self._get_params().copy()
        logger.info(f"Auto-optimizer enabled for bot {self.bot_id}")
    
    def disable(self) -> None:
        """Disable auto-optimization."""
        self.config.enabled = False
        logger.info(f"Auto-optimizer disabled for bot {self.bot_id}")
    
    def set_mode(self, mode: OptimizationMode) -> None:
        """Set optimization mode."""
        self.config.mode = mode
        
        # Adjust config based on mode
        if mode == OptimizationMode.CONSERVATIVE:
            self.config.max_adjustment_pct = 0.10
            self.config.min_trades_for_analysis = 20
            self.config.cooldown_minutes = 60
            self.config.max_adjustments_per_day = 3
        elif mode == OptimizationMode.MODERATE:
            self.config.max_adjustment_pct = 0.20
            self.config.min_trades_for_analysis = 10
            self.config.cooldown_minutes = 30
            self.config.max_adjustments_per_day = 5
        elif mode == OptimizationMode.AGGRESSIVE:
            self.config.max_adjustment_pct = 0.35
            self.config.min_trades_for_analysis = 5
            self.config.cooldown_minutes = 15
            self.config.max_adjustments_per_day = 10
        
        logger.info(f"Auto-optimizer mode set to {mode.value} for bot {self.bot_id}")
    
    def record_trade(self, trade: dict) -> None:
        """
        Record a completed trade for analysis.
        
        Args:
            trade: Trade data including pnl, side, entry_price, exit_price, etc.
        """
        self._trade_results.append({
            **trade,
            "timestamp": datetime.now(),
        })
        
        # Track P&L
        pnl = trade.get("pnl", 0)
        self._pnl_history.append(pnl)
    
    def record_metrics(self, metrics: PerformanceMetrics) -> None:
        """Record current performance metrics."""
        self._metrics_history.append(metrics)
    
    async def start(self) -> None:
        """Start the auto-optimization loop."""
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(self._optimization_loop())
        logger.info(f"Auto-optimizer started for bot {self.bot_id}")
    
    async def stop(self) -> None:
        """Stop the auto-optimization loop."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info(f"Auto-optimizer stopped for bot {self.bot_id}")
    
    async def _optimization_loop(self) -> None:
        """Main optimization loop."""
        while self._running:
            try:
                if self.config.enabled:
                    await self._evaluate_and_adjust()
                
                # Wait for next evaluation interval
                await asyncio.sleep(self.config.evaluation_interval_minutes * 60)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in optimization loop for {self.bot_id}: {e}")
                await asyncio.sleep(60)  # Wait a minute on error
    
    def _calculate_metrics(self) -> Optional[PerformanceMetrics]:
        """Calculate current performance metrics."""
        if len(self._trade_results) < self.config.min_trades_for_analysis:
            return None
        
        # Filter to analysis window
        cutoff = datetime.now() - timedelta(hours=self.config.analysis_window_hours)
        recent_trades = [
            t for t in self._trade_results
            if t.get("timestamp", datetime.now()) >= cutoff
        ]
        
        if not recent_trades:
            recent_trades = list(self._trade_results)
        
        # Calculate metrics
        total = len(recent_trades)
        winners = [t for t in recent_trades if t.get("pnl", 0) > 0]
        losers = [t for t in recent_trades if t.get("pnl", 0) < 0]
        
        total_pnl = sum(t.get("pnl", 0) for t in recent_trades)
        total_wins = sum(t.get("pnl", 0) for t in winners)
        total_losses = abs(sum(t.get("pnl", 0) for t in losers))
        
        win_rate = len(winners) / total if total > 0 else 0
        avg_win = total_wins / len(winners) if winners else 0
        avg_loss = total_losses / len(losers) if losers else 0
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
        
        # Calculate drawdown
        peak = 0
        max_dd = 0
        cumulative = 0
        for t in recent_trades:
            cumulative += t.get("pnl", 0)
            peak = max(peak, cumulative)
            dd = (peak - cumulative) / peak if peak > 0 else 0
            max_dd = max(max_dd, dd)
        
        # Calculate Sharpe ratio (simplified)
        if len(self._pnl_history) > 1:
            pnl_list = list(self._pnl_history)
            mean_return = statistics.mean(pnl_list)
            std_return = statistics.stdev(pnl_list) if len(pnl_list) > 1 else 1
            sharpe = (mean_return / std_return) * (252 ** 0.5) if std_return > 0 else 0
        else:
            sharpe = 0
        
        # Determine trend
        if len(self._metrics_history) >= 3:
            recent_pnls = [m.total_pnl for m in list(self._metrics_history)[-3:]]
            if all(recent_pnls[i] < recent_pnls[i+1] for i in range(len(recent_pnls)-1)):
                trend = "improving"
            elif all(recent_pnls[i] > recent_pnls[i+1] for i in range(len(recent_pnls)-1)):
                trend = "declining"
            else:
                trend = "neutral"
        else:
            trend = "neutral"
        
        return PerformanceMetrics(
            bot_id=self.bot_id,
            timestamp=datetime.now(),
            total_trades=total,
            winning_trades=len(winners),
            losing_trades=len(losers),
            total_pnl=total_pnl,
            win_rate=win_rate,
            profit_factor=profit_factor,
            avg_win=avg_win,
            avg_loss=avg_loss,
            max_drawdown=max_dd,
            sharpe_ratio=sharpe,
            recent_win_rate=win_rate,
            recent_pnl=total_pnl,
            trend=trend,
        )
    
    async def _evaluate_and_adjust(self) -> None:
        """Evaluate performance and make adjustments if needed."""
        # Reset daily counter
        today = datetime.now().date()
        if self._last_reset_date != today:
            self._adjustments_today = 0
            self._last_reset_date = today
        
        # Check if we've hit daily limit
        if self._adjustments_today >= self.config.max_adjustments_per_day:
            logger.debug(f"Bot {self.bot_id}: Daily adjustment limit reached")
            return
        
        # Check cooldown
        if self._last_adjustment_time:
            cooldown = timedelta(minutes=self.config.cooldown_minutes)
            if datetime.now() - self._last_adjustment_time < cooldown:
                return
        
        # Calculate current metrics
        metrics = self._calculate_metrics()
        if not metrics:
            return
        
        self.record_metrics(metrics)
        
        # Analyze and determine adjustments
        adjustments = self._analyze_performance(metrics)
        
        if adjustments:
            await self._apply_adjustments(adjustments, metrics)
    
    def _analyze_performance(self, metrics: PerformanceMetrics) -> list[ParameterAdjustment]:
        """Analyze performance and determine needed adjustments."""
        adjustments = []
        current_params = self._get_params()
        
        # Check if performance is below thresholds
        if metrics.win_rate < self.config.min_win_rate:
            # Low win rate - tighten entry criteria
            adjustments.extend(self._suggest_entry_improvements(current_params, metrics))
        
        if metrics.max_drawdown > self.config.max_drawdown_pct:
            # High drawdown - reduce risk
            adjustments.extend(self._suggest_risk_reduction(current_params, metrics))
        
        if metrics.profit_factor < self.config.min_profit_factor:
            # Poor profit factor - improve risk/reward
            adjustments.extend(self._suggest_risk_reward_improvements(current_params, metrics))
        
        # If declining, try to reverse the trend
        if metrics.trend == "declining":
            adjustments.extend(self._suggest_trend_reversal(current_params, metrics))
        
        # If improving and performing well, consider relaxing constraints
        if metrics.trend == "improving" and metrics.win_rate > self.config.target_win_rate:
            adjustments.extend(self._suggest_optimization(current_params, metrics))
        
        return adjustments
    
    def _suggest_entry_improvements(
        self,
        params: dict,
        metrics: PerformanceMetrics
    ) -> list[ParameterAdjustment]:
        """Suggest improvements to entry criteria for better win rate."""
        suggestions = []
        
        # Increase minimum confidence required
        if "min_confidence" in params:
            current = params["min_confidence"]
            limits = self.ADJUSTABLE_PARAMETERS.get("min_confidence", {})
            new_val = min(current * (1 + self.config.max_adjustment_pct), limits.get("max", 0.9))
            if new_val != current:
                suggestions.append(ParameterAdjustment(
                    parameter_name="min_confidence",
                    old_value=current,
                    new_value=round(new_val, 2),
                    adjustment_type=AdjustmentType.INCREASE,
                    reason=f"Low win rate ({metrics.win_rate:.1%}): increasing entry threshold",
                ))
        
        # Tighten signal strength threshold
        if "signal_strength_threshold" in params:
            current = params["signal_strength_threshold"]
            limits = self.ADJUSTABLE_PARAMETERS.get("signal_strength_threshold", {})
            new_val = min(current * 1.1, limits.get("max", 0.8))
            if new_val != current:
                suggestions.append(ParameterAdjustment(
                    parameter_name="signal_strength_threshold",
                    old_value=current,
                    new_value=round(new_val, 2),
                    adjustment_type=AdjustmentType.INCREASE,
                    reason="Requiring stronger signals for entry",
                ))
        
        return suggestions[:2]  # Limit adjustments per cycle
    
    def _suggest_risk_reduction(
        self,
        params: dict,
        metrics: PerformanceMetrics
    ) -> list[ParameterAdjustment]:
        """Suggest risk reduction when drawdown is high."""
        suggestions = []
        
        # Reduce position size
        if "position_size_pct" in params:
            current = params["position_size_pct"]
            limits = self.ADJUSTABLE_PARAMETERS.get("position_size_pct", {})
            new_val = max(current * (1 - self.config.max_adjustment_pct), limits.get("min", 0.01))
            suggestions.append(ParameterAdjustment(
                parameter_name="position_size_pct",
                old_value=current,
                new_value=round(new_val, 3),
                adjustment_type=AdjustmentType.DECREASE,
                reason=f"High drawdown ({metrics.max_drawdown:.1%}): reducing position size",
            ))
        
        # Tighten stop loss
        if "stop_loss_pct" in params:
            current = params["stop_loss_pct"]
            limits = self.ADJUSTABLE_PARAMETERS.get("stop_loss_pct", {})
            new_val = max(current * 0.85, limits.get("min", 0.01))
            suggestions.append(ParameterAdjustment(
                parameter_name="stop_loss_pct",
                old_value=current,
                new_value=round(new_val, 3),
                adjustment_type=AdjustmentType.DECREASE,
                reason="Tightening stop loss to limit losses",
            ))
        
        return suggestions[:2]
    
    def _suggest_risk_reward_improvements(
        self,
        params: dict,
        metrics: PerformanceMetrics
    ) -> list[ParameterAdjustment]:
        """Suggest improvements to risk/reward ratio."""
        suggestions = []
        
        # Increase take profit target
        if "take_profit_pct" in params:
            current = params["take_profit_pct"]
            limits = self.ADJUSTABLE_PARAMETERS.get("take_profit_pct", {})
            new_val = min(current * 1.15, limits.get("max", 0.20))
            suggestions.append(ParameterAdjustment(
                parameter_name="take_profit_pct",
                old_value=current,
                new_value=round(new_val, 3),
                adjustment_type=AdjustmentType.INCREASE,
                reason=f"Low profit factor ({metrics.profit_factor:.2f}): increasing profit targets",
            ))
        
        return suggestions
    
    def _suggest_trend_reversal(
        self,
        params: dict,
        metrics: PerformanceMetrics
    ) -> list[ParameterAdjustment]:
        """Suggest changes to reverse declining performance."""
        suggestions = []
        
        # If we have previous best parameters, consider reverting
        if self._best_params and self.config.revert_on_worse_performance:
            current_perf = metrics.total_pnl
            if current_perf < self._best_performance * 0.9:  # 10% worse than best
                # Suggest reverting key parameters
                for param, best_val in self._best_params.items():
                    if param in params and params[param] != best_val:
                        suggestions.append(ParameterAdjustment(
                            parameter_name=param,
                            old_value=params[param],
                            new_value=best_val,
                            adjustment_type=AdjustmentType.RESET,
                            reason="Reverting to best-performing configuration",
                        ))
        
        return suggestions[:3]
    
    def _suggest_optimization(
        self,
        params: dict,
        metrics: PerformanceMetrics
    ) -> list[ParameterAdjustment]:
        """Suggest optimizations when performance is good."""
        suggestions = []
        
        # If doing well, can consider slightly increasing position sizes
        if "position_size_pct" in params and metrics.win_rate > 0.60:
            current = params["position_size_pct"]
            limits = self.ADJUSTABLE_PARAMETERS.get("position_size_pct", {})
            new_val = min(current * 1.05, limits.get("max", 0.10))
            if new_val != current:
                suggestions.append(ParameterAdjustment(
                    parameter_name="position_size_pct",
                    old_value=current,
                    new_value=round(new_val, 3),
                    adjustment_type=AdjustmentType.INCREASE,
                    reason=f"Strong performance ({metrics.win_rate:.1%} win rate): slight position increase",
                ))
        
        return suggestions[:1]  # Conservative optimization
    
    async def _apply_adjustments(
        self,
        adjustments: list[ParameterAdjustment],
        metrics: PerformanceMetrics
    ) -> None:
        """Apply parameter adjustments to the bot."""
        if not adjustments:
            return
        
        current_params = self._get_params()
        new_params = current_params.copy()
        
        for adj in adjustments:
            new_params[adj.parameter_name] = adj.new_value
            adj.performance_before = metrics.total_pnl
            self._adjustments.append(adj)
            
            logger.info(
                f"Bot {self.bot_id} auto-adjustment: {adj.parameter_name} "
                f"{adj.old_value} -> {adj.new_value} ({adj.reason})"
            )
        
        # Apply the changes
        self._set_params(new_params)
        
        # Update tracking
        self._last_adjustment_time = datetime.now()
        self._adjustments_today += 1
        
        # Update best params if current performance is best
        if metrics.total_pnl > self._best_performance:
            self._best_performance = metrics.total_pnl
            self._best_params = current_params.copy()
    
    def get_status(self) -> dict:
        """Get current optimizer status."""
        metrics = self._calculate_metrics()
        
        return {
            "bot_id": self.bot_id,
            "enabled": self.config.enabled,
            "running": self._running,
            "mode": self.config.mode.value,
            "config": self.config.to_dict(),
            "current_metrics": metrics.to_dict() if metrics else None,
            "total_adjustments": len(self._adjustments),
            "adjustments_today": self._adjustments_today,
            "last_adjustment": self._last_adjustment_time.isoformat() if self._last_adjustment_time else None,
            "recent_adjustments": [
                adj.to_dict() for adj in self._adjustments[-10:]
            ],
            "baseline_params": self._baseline_params,
            "best_params": self._best_params,
            "best_performance": self._best_performance,
        }
    
    def reset(self) -> None:
        """Reset optimizer to baseline."""
        if self._baseline_params:
            self._set_params(self._baseline_params.copy())
        
        self._adjustments.clear()
        self._adjustments_today = 0
        self._last_adjustment_time = None
        self._best_params = {}
        self._best_performance = 0.0
        
        logger.info(f"Auto-optimizer reset for bot {self.bot_id}")


class AutoOptimizerManager:
    """
    Manages auto-optimizers for multiple bots.
    """
    
    def __init__(self):
        self._optimizers: dict[str, BotAutoOptimizer] = {}
        self._global_config = OptimizationConfig()
    
    def register_bot(
        self,
        bot_id: str,
        get_params: Callable[[], dict],
        set_params: Callable[[dict], None],
        config: Optional[OptimizationConfig] = None,
    ) -> BotAutoOptimizer:
        """Register a bot for auto-optimization."""
        optimizer = BotAutoOptimizer(
            bot_id=bot_id,
            get_bot_params=get_params,
            set_bot_params=set_params,
            config=config or OptimizationConfig(),
        )
        self._optimizers[bot_id] = optimizer
        return optimizer
    
    def get_optimizer(self, bot_id: str) -> Optional[BotAutoOptimizer]:
        """Get optimizer for a specific bot."""
        return self._optimizers.get(bot_id)
    
    def unregister_bot(self, bot_id: str) -> None:
        """Remove a bot from auto-optimization."""
        if bot_id in self._optimizers:
            optimizer = self._optimizers.pop(bot_id)
            # Stop the optimizer - handle both sync and async contexts
            try:
                loop = asyncio.get_running_loop()
                # We're in an async context, schedule the stop
                loop.create_task(optimizer.stop())
            except RuntimeError:
                # No running loop - just disable, cleanup will happen on next start
                optimizer.disable()
    
    async def enable_bot(self, bot_id: str, mode: OptimizationMode = OptimizationMode.MODERATE) -> bool:
        """Enable auto-optimization for a specific bot."""
        optimizer = self._optimizers.get(bot_id)
        if optimizer:
            optimizer.set_mode(mode)
            optimizer.enable()
            await optimizer.start()
            return True
        return False
    
    async def disable_bot(self, bot_id: str) -> bool:
        """Disable auto-optimization for a specific bot."""
        optimizer = self._optimizers.get(bot_id)
        if optimizer:
            optimizer.disable()
            await optimizer.stop()
            return True
        return False
    
    async def enable_all(self, mode: OptimizationMode = OptimizationMode.MODERATE) -> int:
        """Enable auto-optimization for all registered bots."""
        count = 0
        for bot_id, optimizer in self._optimizers.items():
            optimizer.set_mode(mode)
            optimizer.enable()
            await optimizer.start()
            count += 1
        return count
    
    async def disable_all(self) -> int:
        """Disable auto-optimization for all bots."""
        count = 0
        for optimizer in self._optimizers.values():
            optimizer.disable()
            await optimizer.stop()
            count += 1
        return count
    
    def record_trade(self, bot_id: str, trade: dict) -> None:
        """Record a trade for a specific bot."""
        optimizer = self._optimizers.get(bot_id)
        if optimizer:
            optimizer.record_trade(trade)
    
    def get_all_status(self) -> dict:
        """Get status of all optimizers."""
        return {
            "total_bots": len(self._optimizers),
            "enabled_count": sum(1 for o in self._optimizers.values() if o.is_enabled),
            "running_count": sum(1 for o in self._optimizers.values() if o.is_running),
            "bots": {
                bot_id: optimizer.get_status()
                for bot_id, optimizer in self._optimizers.items()
            }
        }
    
    def get_recommendations(self) -> list[dict]:
        """Get optimization recommendations for all bots."""
        recommendations = []
        
        for bot_id, optimizer in self._optimizers.items():
            status = optimizer.get_status()
            metrics = status.get("current_metrics")
            
            if not metrics:
                continue
            
            # Generate recommendations based on metrics
            if metrics.get("win_rate", 0) < 0.4:
                recommendations.append({
                    "bot_id": bot_id,
                    "priority": "high",
                    "issue": "Low win rate",
                    "value": f"{metrics['win_rate']:.1%}",
                    "suggestion": "Enable auto-optimization in conservative mode",
                })
            
            if metrics.get("max_drawdown", 0) > 0.15:
                recommendations.append({
                    "bot_id": bot_id,
                    "priority": "high",
                    "issue": "High drawdown",
                    "value": f"{metrics['max_drawdown']:.1%}",
                    "suggestion": "Reduce position sizes and tighten stops",
                })
            
            if metrics.get("profit_factor", 1) < 1.2:
                recommendations.append({
                    "bot_id": bot_id,
                    "priority": "medium",
                    "issue": "Poor risk/reward",
                    "value": f"{metrics['profit_factor']:.2f}",
                    "suggestion": "Adjust take profit and stop loss ratios",
                })
        
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 99))
        
        return recommendations


# Global instance
_manager: Optional[AutoOptimizerManager] = None


def get_auto_optimizer_manager() -> AutoOptimizerManager:
    """Get or create the global auto-optimizer manager."""
    global _manager
    if _manager is None:
        _manager = AutoOptimizerManager()
    return _manager


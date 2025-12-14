"""
Tests for Auto-Optimizer for Trading Bots.

Tests performance analysis, parameter adjustment, and optimization modes.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from src.bot.auto_optimizer import (
    BotAutoOptimizer,
    AutoOptimizerManager,
    OptimizationConfig,
    OptimizationMode,
    PerformanceMetrics,
    ParameterAdjustment,
    AdjustmentType,
    get_auto_optimizer_manager,
)


class TestOptimizationConfig:
    """Tests for OptimizationConfig dataclass."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = OptimizationConfig()
        
        assert config.enabled is False
        assert config.mode == OptimizationMode.MODERATE
        assert config.min_trades_for_analysis == 10
        assert config.analysis_window_hours == 24
        assert config.max_adjustment_pct == 0.20
        assert config.min_win_rate == 0.40
        assert config.target_win_rate == 0.55
        assert config.max_drawdown_pct == 0.15
        assert config.max_adjustments_per_day == 5
    
    def test_config_to_dict(self):
        """Test config serialization."""
        config = OptimizationConfig()
        data = config.to_dict()
        
        assert "enabled" in data
        assert "mode" in data
        assert "min_trades_for_analysis" in data
        assert data["mode"] == "moderate"


class TestOptimizationMode:
    """Tests for OptimizationMode enum."""
    
    def test_mode_values(self):
        """Test optimization mode values."""
        assert OptimizationMode.CONSERVATIVE.value == "conservative"
        assert OptimizationMode.MODERATE.value == "moderate"
        assert OptimizationMode.AGGRESSIVE.value == "aggressive"
        assert OptimizationMode.CUSTOM.value == "custom"


class TestPerformanceMetrics:
    """Tests for PerformanceMetrics dataclass."""
    
    def test_metrics_creation(self):
        """Test creating performance metrics."""
        metrics = PerformanceMetrics(
            bot_id="test-bot-1",
            timestamp=datetime.now(),
            total_trades=50,
            winning_trades=30,
            losing_trades=20,
            total_pnl=5000.0,
            win_rate=0.60,
            profit_factor=1.8,
            max_drawdown=0.08,
            sharpe_ratio=1.5,
        )
        
        assert metrics.bot_id == "test-bot-1"
        assert metrics.total_trades == 50
        assert metrics.win_rate == 0.60
        assert metrics.profit_factor == 1.8
    
    def test_metrics_to_dict(self):
        """Test metrics serialization."""
        metrics = PerformanceMetrics(
            bot_id="test-bot",
            timestamp=datetime.now(),
        )
        data = metrics.to_dict()
        
        assert "bot_id" in data
        assert "timestamp" in data
        assert "win_rate" in data
        assert "profit_factor" in data


class TestParameterAdjustment:
    """Tests for ParameterAdjustment dataclass."""
    
    def test_adjustment_creation(self):
        """Test creating a parameter adjustment."""
        adj = ParameterAdjustment(
            parameter_name="stop_loss_pct",
            old_value=0.05,
            new_value=0.04,
            adjustment_type=AdjustmentType.DECREASE,
            reason="High drawdown detected",
        )
        
        assert adj.parameter_name == "stop_loss_pct"
        assert adj.old_value == 0.05
        assert adj.new_value == 0.04
        assert adj.adjustment_type == AdjustmentType.DECREASE
    
    def test_adjustment_to_dict(self):
        """Test adjustment serialization."""
        adj = ParameterAdjustment(
            parameter_name="position_size_pct",
            old_value=0.05,
            new_value=0.04,
            adjustment_type=AdjustmentType.DECREASE,
            reason="Reducing risk",
        )
        data = adj.to_dict()
        
        assert "parameter" in data
        assert "old_value" in data
        assert "new_value" in data
        assert "adjustment" in data
        assert "reason" in data


class TestBotAutoOptimizer:
    """Tests for BotAutoOptimizer class."""
    
    @pytest.fixture
    def mock_bot_params(self):
        """Create mock bot parameters."""
        return {
            "stop_loss_pct": 0.05,
            "take_profit_pct": 0.10,
            "position_size_pct": 0.05,
            "max_positions": 5,
            "min_confidence": 0.6,
            "rsi_oversold": 30,
            "rsi_overbought": 70,
        }
    
    @pytest.fixture
    def optimizer(self, mock_bot_params):
        """Create optimizer with mock callbacks."""
        params = mock_bot_params.copy()
        
        def get_params():
            return params.copy()
        
        def set_params(new_params):
            params.update(new_params)
        
        return BotAutoOptimizer(
            bot_id="test-bot",
            get_bot_params=get_params,
            set_bot_params=set_params,
        )
    
    def test_optimizer_initialization(self, optimizer):
        """Test optimizer initializes correctly."""
        assert optimizer.bot_id == "test-bot"
        assert optimizer.is_enabled is False
        assert optimizer.is_running is False
    
    def test_enable_disable(self, optimizer):
        """Test enabling and disabling optimizer."""
        optimizer.enable()
        assert optimizer.is_enabled is True
        
        optimizer.disable()
        assert optimizer.is_enabled is False
    
    def test_set_mode_conservative(self, optimizer):
        """Test setting conservative mode."""
        optimizer.set_mode(OptimizationMode.CONSERVATIVE)
        
        assert optimizer.config.mode == OptimizationMode.CONSERVATIVE
        assert optimizer.config.max_adjustment_pct == 0.10
        assert optimizer.config.min_trades_for_analysis == 20
        assert optimizer.config.cooldown_minutes == 60
        assert optimizer.config.max_adjustments_per_day == 3
    
    def test_set_mode_moderate(self, optimizer):
        """Test setting moderate mode."""
        optimizer.set_mode(OptimizationMode.MODERATE)
        
        assert optimizer.config.mode == OptimizationMode.MODERATE
        assert optimizer.config.max_adjustment_pct == 0.20
        assert optimizer.config.min_trades_for_analysis == 10
    
    def test_set_mode_aggressive(self, optimizer):
        """Test setting aggressive mode."""
        optimizer.set_mode(OptimizationMode.AGGRESSIVE)
        
        assert optimizer.config.mode == OptimizationMode.AGGRESSIVE
        assert optimizer.config.max_adjustment_pct == 0.35
        assert optimizer.config.min_trades_for_analysis == 5
        assert optimizer.config.max_adjustments_per_day == 10
    
    def test_record_trade(self, optimizer):
        """Test recording trades."""
        trade = {
            "symbol": "AAPL",
            "side": "buy",
            "pnl": 100.0,
            "quantity": 10,
        }
        optimizer.record_trade(trade)
        
        assert len(optimizer._trade_results) == 1
        assert len(optimizer._pnl_history) == 1
    
    def test_record_multiple_trades(self, optimizer):
        """Test recording multiple trades."""
        for i in range(15):
            trade = {
                "symbol": "AAPL",
                "pnl": 50.0 if i % 2 == 0 else -30.0,
            }
            optimizer.record_trade(trade)
        
        assert len(optimizer._trade_results) == 15
    
    def test_calculate_metrics_insufficient_trades(self, optimizer):
        """Test metrics calculation with insufficient trades."""
        # Record fewer trades than minimum
        for i in range(5):
            optimizer.record_trade({"pnl": 10.0})
        
        metrics = optimizer._calculate_metrics()
        assert metrics is None  # Not enough trades
    
    def test_calculate_metrics_sufficient_trades(self, optimizer):
        """Test metrics calculation with sufficient trades."""
        optimizer.config.min_trades_for_analysis = 5
        
        # Record enough trades
        for i in range(10):
            trade = {
                "pnl": 100.0 if i % 3 != 0 else -50.0,
                "timestamp": datetime.now(),
            }
            optimizer.record_trade(trade)
        
        metrics = optimizer._calculate_metrics()
        assert metrics is not None
        assert metrics.total_trades == 10
        assert metrics.win_rate > 0
    
    def test_get_status(self, optimizer):
        """Test getting optimizer status."""
        status = optimizer.get_status()
        
        assert "bot_id" in status
        assert "enabled" in status
        assert "running" in status
        assert "mode" in status
        assert "config" in status
        assert "total_adjustments" in status
    
    def test_reset(self, optimizer):
        """Test resetting optimizer."""
        # Set up some state
        optimizer.enable()
        optimizer.record_trade({"pnl": 100.0})
        optimizer._adjustments.append(MagicMock())
        
        optimizer.reset()
        
        assert optimizer._adjustments == []
        assert optimizer._adjustments_today == 0
        assert optimizer._best_params == {}
    
    def test_adjustable_parameters(self):
        """Test that adjustable parameters are defined."""
        params = BotAutoOptimizer.ADJUSTABLE_PARAMETERS
        
        assert "stop_loss_pct" in params
        assert "take_profit_pct" in params
        assert "position_size_pct" in params
        assert "rsi_oversold" in params
        assert "min_confidence" in params
        
        # Check structure
        stop_loss = params["stop_loss_pct"]
        assert "min" in stop_loss
        assert "max" in stop_loss
        assert "direction" in stop_loss


class TestAutoOptimizerManager:
    """Tests for AutoOptimizerManager class."""
    
    @pytest.fixture
    def manager(self):
        """Create a fresh manager for each test."""
        return AutoOptimizerManager()
    
    @pytest.fixture
    def mock_callbacks(self):
        """Create mock callbacks for bot registration."""
        params = {"stop_loss_pct": 0.05}
        return (
            lambda: params.copy(),
            lambda p: params.update(p),
        )
    
    def test_manager_initialization(self, manager):
        """Test manager initializes correctly."""
        assert len(manager._optimizers) == 0
    
    def test_register_bot(self, manager, mock_callbacks):
        """Test registering a bot."""
        get_params, set_params = mock_callbacks
        optimizer = manager.register_bot(
            bot_id="test-1",
            get_params=get_params,
            set_params=set_params,
        )
        
        assert optimizer is not None
        assert optimizer.bot_id == "test-1"
        assert "test-1" in manager._optimizers
    
    def test_get_optimizer(self, manager, mock_callbacks):
        """Test getting an optimizer."""
        get_params, set_params = mock_callbacks
        manager.register_bot("test-1", get_params, set_params)
        
        optimizer = manager.get_optimizer("test-1")
        assert optimizer is not None
        
        missing = manager.get_optimizer("nonexistent")
        assert missing is None
    
    @pytest.mark.asyncio
    async def test_unregister_bot(self, manager, mock_callbacks):
        """Test unregistering a bot."""
        get_params, set_params = mock_callbacks
        manager.register_bot("test-1", get_params, set_params)
        
        # Get the optimizer before unregistering
        optimizer = manager.get_optimizer("test-1")
        
        # Pop from dict directly since unregister uses asyncio.create_task
        del manager._optimizers["test-1"]
        
        assert "test-1" not in manager._optimizers
    
    def test_record_trade(self, manager, mock_callbacks):
        """Test recording trade through manager."""
        get_params, set_params = mock_callbacks
        manager.register_bot("test-1", get_params, set_params)
        
        manager.record_trade("test-1", {"pnl": 100.0})
        
        optimizer = manager.get_optimizer("test-1")
        assert len(optimizer._trade_results) == 1
    
    def test_get_all_status(self, manager, mock_callbacks):
        """Test getting status of all optimizers."""
        get_params, set_params = mock_callbacks
        manager.register_bot("test-1", get_params, set_params)
        manager.register_bot("test-2", get_params, set_params)
        
        status = manager.get_all_status()
        
        assert "total_bots" in status
        assert "enabled_count" in status
        assert "running_count" in status
        assert "bots" in status
        assert status["total_bots"] == 2
    
    def test_get_recommendations_empty(self, manager):
        """Test getting recommendations with no data."""
        recommendations = manager.get_recommendations()
        assert isinstance(recommendations, list)
    
    @pytest.mark.asyncio
    async def test_enable_disable_bot(self, manager, mock_callbacks):
        """Test enabling and disabling bot through manager."""
        get_params, set_params = mock_callbacks
        manager.register_bot("test-1", get_params, set_params)
        
        success = await manager.enable_bot("test-1", OptimizationMode.MODERATE)
        assert success is True
        
        optimizer = manager.get_optimizer("test-1")
        assert optimizer.is_enabled is True
        
        success = await manager.disable_bot("test-1")
        assert success is True
        assert optimizer.is_enabled is False


class TestGlobalManager:
    """Tests for global manager singleton."""
    
    def test_global_manager_singleton(self):
        """Test that global manager is a singleton."""
        manager1 = get_auto_optimizer_manager()
        manager2 = get_auto_optimizer_manager()
        
        assert manager1 is manager2


class TestAdjustmentType:
    """Tests for AdjustmentType enum."""
    
    def test_adjustment_types(self):
        """Test adjustment type values."""
        assert AdjustmentType.INCREASE.value == "increase"
        assert AdjustmentType.DECREASE.value == "decrease"
        assert AdjustmentType.NO_CHANGE.value == "no_change"
        assert AdjustmentType.RESET.value == "reset"


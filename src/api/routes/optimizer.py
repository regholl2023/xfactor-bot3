"""
Auto-Optimizer API Routes.

Provides endpoints for managing bot auto-optimization,
viewing performance metrics, and controlling adjustments.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.bot.auto_optimizer import (
    get_auto_optimizer_manager,
    OptimizationMode,
    OptimizationConfig,
)


router = APIRouter(prefix="/api/optimizer", tags=["optimizer"])


class EnableOptimizerRequest(BaseModel):
    """Request to enable auto-optimizer for a bot."""
    mode: str = "moderate"  # conservative, moderate, aggressive


class OptimizerConfigRequest(BaseModel):
    """Request to update optimizer configuration."""
    min_trades_for_analysis: Optional[int] = None
    analysis_window_hours: Optional[int] = None
    evaluation_interval_minutes: Optional[int] = None
    max_adjustment_pct: Optional[float] = None
    min_win_rate: Optional[float] = None
    target_win_rate: Optional[float] = None
    max_drawdown_pct: Optional[float] = None
    max_adjustments_per_day: Optional[int] = None


@router.get("/status")
async def get_optimizer_status() -> dict:
    """
    Get status of all auto-optimizers.
    
    Returns overview of all registered bots and their optimization status.
    """
    manager = get_auto_optimizer_manager()
    return manager.get_all_status()


@router.get("/bot/{bot_id}/status")
async def get_bot_optimizer_status(bot_id: str) -> dict:
    """
    Get detailed optimizer status for a specific bot.
    
    Returns current metrics, recent adjustments, and configuration.
    """
    manager = get_auto_optimizer_manager()
    optimizer = manager.get_optimizer(bot_id)
    
    if not optimizer:
        raise HTTPException(
            status_code=404,
            detail=f"Bot {bot_id} not found or not registered for optimization"
        )
    
    return optimizer.get_status()


@router.post("/bot/{bot_id}/enable")
async def enable_bot_optimizer(bot_id: str, request: EnableOptimizerRequest) -> dict:
    """
    Enable auto-optimization for a specific bot.
    
    When enabled, the optimizer will:
    - Monitor trading performance
    - Analyze win rate, drawdown, and profit factor
    - Automatically adjust strategy parameters
    - Log all adjustments for transparency
    """
    manager = get_auto_optimizer_manager()
    
    # Parse mode
    try:
        mode = OptimizationMode(request.mode.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mode: {request.mode}. Use: conservative, moderate, aggressive"
        )
    
    success = await manager.enable_bot(bot_id, mode)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Bot {bot_id} not found. Register the bot first."
        )
    
    return {
        "success": True,
        "message": f"Auto-optimization enabled for bot {bot_id}",
        "mode": mode.value,
    }


@router.post("/bot/{bot_id}/disable")
async def disable_bot_optimizer(bot_id: str) -> dict:
    """
    Disable auto-optimization for a specific bot.
    
    The bot will keep its current parameters but stop making
    automatic adjustments.
    """
    manager = get_auto_optimizer_manager()
    success = await manager.disable_bot(bot_id)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Bot {bot_id} not found"
        )
    
    return {
        "success": True,
        "message": f"Auto-optimization disabled for bot {bot_id}",
    }


@router.post("/bot/{bot_id}/reset")
async def reset_bot_optimizer(bot_id: str) -> dict:
    """
    Reset bot to baseline parameters.
    
    Reverts all auto-adjustments and clears history.
    """
    manager = get_auto_optimizer_manager()
    optimizer = manager.get_optimizer(bot_id)
    
    if not optimizer:
        raise HTTPException(status_code=404, detail=f"Bot {bot_id} not found")
    
    optimizer.reset()
    
    return {
        "success": True,
        "message": f"Bot {bot_id} reset to baseline parameters",
    }


@router.put("/bot/{bot_id}/config")
async def update_bot_optimizer_config(
    bot_id: str,
    config: OptimizerConfigRequest
) -> dict:
    """
    Update optimizer configuration for a specific bot.
    
    Allows fine-tuning of optimization parameters.
    """
    manager = get_auto_optimizer_manager()
    optimizer = manager.get_optimizer(bot_id)
    
    if not optimizer:
        raise HTTPException(status_code=404, detail=f"Bot {bot_id} not found")
    
    # Update only provided fields
    if config.min_trades_for_analysis is not None:
        optimizer.config.min_trades_for_analysis = config.min_trades_for_analysis
    if config.analysis_window_hours is not None:
        optimizer.config.analysis_window_hours = config.analysis_window_hours
    if config.evaluation_interval_minutes is not None:
        optimizer.config.evaluation_interval_minutes = config.evaluation_interval_minutes
    if config.max_adjustment_pct is not None:
        optimizer.config.max_adjustment_pct = config.max_adjustment_pct
    if config.min_win_rate is not None:
        optimizer.config.min_win_rate = config.min_win_rate
    if config.target_win_rate is not None:
        optimizer.config.target_win_rate = config.target_win_rate
    if config.max_drawdown_pct is not None:
        optimizer.config.max_drawdown_pct = config.max_drawdown_pct
    if config.max_adjustments_per_day is not None:
        optimizer.config.max_adjustments_per_day = config.max_adjustments_per_day
    
    return {
        "success": True,
        "config": optimizer.config.to_dict(),
    }


@router.get("/bot/{bot_id}/adjustments")
async def get_bot_adjustments(
    bot_id: str,
    limit: int = Query(50, ge=1, le=500)
) -> dict:
    """
    Get history of parameter adjustments for a bot.
    
    Returns all auto-adjustments made, with reasons and timing.
    """
    manager = get_auto_optimizer_manager()
    optimizer = manager.get_optimizer(bot_id)
    
    if not optimizer:
        raise HTTPException(status_code=404, detail=f"Bot {bot_id} not found")
    
    adjustments = [adj.to_dict() for adj in optimizer._adjustments[-limit:]]
    
    return {
        "bot_id": bot_id,
        "total_adjustments": len(optimizer._adjustments),
        "adjustments": adjustments,
    }


@router.get("/bot/{bot_id}/metrics")
async def get_bot_metrics(bot_id: str) -> dict:
    """
    Get current performance metrics for a bot.
    
    Returns win rate, profit factor, drawdown, and trend.
    """
    manager = get_auto_optimizer_manager()
    optimizer = manager.get_optimizer(bot_id)
    
    if not optimizer:
        raise HTTPException(status_code=404, detail=f"Bot {bot_id} not found")
    
    metrics = optimizer._calculate_metrics()
    
    if not metrics:
        return {
            "bot_id": bot_id,
            "message": "Insufficient trades for analysis",
            "min_trades_required": optimizer.config.min_trades_for_analysis,
        }
    
    return metrics.to_dict()


@router.post("/enable-all")
async def enable_all_optimizers(request: EnableOptimizerRequest) -> dict:
    """
    Enable auto-optimization for all registered bots.
    
    Use with caution - affects all trading bots.
    """
    manager = get_auto_optimizer_manager()
    
    try:
        mode = OptimizationMode(request.mode.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid mode: {request.mode}")
    
    count = await manager.enable_all(mode)
    
    return {
        "success": True,
        "message": f"Enabled auto-optimization for {count} bots",
        "mode": mode.value,
    }


@router.post("/disable-all")
async def disable_all_optimizers() -> dict:
    """
    Disable auto-optimization for all bots.
    """
    manager = get_auto_optimizer_manager()
    count = await manager.disable_all()
    
    return {
        "success": True,
        "message": f"Disabled auto-optimization for {count} bots",
    }


@router.get("/recommendations")
async def get_optimization_recommendations() -> dict:
    """
    Get optimization recommendations for all bots.
    
    Analyzes performance and suggests improvements.
    """
    manager = get_auto_optimizer_manager()
    recommendations = manager.get_recommendations()
    
    return {
        "recommendations": recommendations,
        "total": len(recommendations),
        "high_priority": sum(1 for r in recommendations if r["priority"] == "high"),
    }


@router.post("/bot/{bot_id}/record-trade")
async def record_trade(bot_id: str, trade: dict) -> dict:
    """
    Record a completed trade for analysis.
    
    The optimizer uses this data to evaluate performance.
    
    Trade should include:
    - pnl: Profit/loss amount
    - side: 'buy' or 'sell'
    - symbol: Trading symbol
    - entry_price: Entry price
    - exit_price: Exit price (optional)
    - quantity: Position size
    """
    manager = get_auto_optimizer_manager()
    manager.record_trade(bot_id, trade)
    
    return {
        "success": True,
        "message": f"Trade recorded for bot {bot_id}",
    }


@router.get("/modes")
async def get_optimization_modes() -> dict:
    """
    Get available optimization modes with descriptions.
    """
    return {
        "modes": [
            {
                "name": "conservative",
                "description": "Small, careful adjustments. Best for stable strategies.",
                "max_adjustment": "10%",
                "min_trades": 20,
                "cooldown": "60 min",
                "daily_limit": 3,
            },
            {
                "name": "moderate",
                "description": "Balanced adjustments. Good for most use cases.",
                "max_adjustment": "20%",
                "min_trades": 10,
                "cooldown": "30 min",
                "daily_limit": 5,
            },
            {
                "name": "aggressive",
                "description": "Larger, faster adjustments. For active optimization.",
                "max_adjustment": "35%",
                "min_trades": 5,
                "cooldown": "15 min",
                "daily_limit": 10,
            },
        ]
    }


@router.get("/adjustable-parameters")
async def get_adjustable_parameters() -> dict:
    """
    Get list of parameters that can be auto-adjusted.
    
    Returns parameter names, min/max values, and optimization direction.
    """
    from src.bot.auto_optimizer import BotAutoOptimizer
    
    return {
        "parameters": BotAutoOptimizer.ADJUSTABLE_PARAMETERS,
        "categories": {
            "risk_management": [
                "stop_loss_pct", "take_profit_pct", 
                "position_size_pct", "max_positions"
            ],
            "technical_indicators": [
                "rsi_oversold", "rsi_overbought",
                "ma_fast_period", "ma_slow_period"
            ],
            "momentum": [
                "momentum_threshold", "volume_threshold"
            ],
            "signals": [
                "min_confidence", "signal_strength_threshold"
            ],
        }
    }


"""
Compliance API Routes.

Provides endpoints for trading compliance status, pre-trade checks,
and violation history.
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.compliance import (
    get_compliance_manager,
    ComplianceAction,
)


router = APIRouter(prefix="/compliance", tags=["Compliance"])


# =========================================================================
# Request/Response Models
# =========================================================================

class PreTradeCheckRequest(BaseModel):
    """Request for pre-trade compliance check."""
    symbol: str
    side: str  # 'buy' or 'sell'
    quantity: float
    estimated_price: float
    is_closing: bool = False


class AccountUpdateRequest(BaseModel):
    """Request to update account information."""
    equity: Optional[float] = None
    buying_power: Optional[float] = None
    day_trading_buying_power: Optional[float] = None
    is_pattern_day_trader: Optional[bool] = None
    account_type: Optional[str] = None


class RecordTradeRequest(BaseModel):
    """Request to record a completed trade."""
    symbol: str
    side: str  # 'buy' or 'sell'
    quantity: float
    price: float


class ComplianceSettingsRequest(BaseModel):
    """Request to update compliance settings."""
    pdt_warning_enabled: bool = True
    good_faith_warning_enabled: bool = True
    freeriding_warning_enabled: bool = True
    wash_sale_warning_enabled: bool = True
    auto_stop_on_pdt: bool = True


# =========================================================================
# Status Endpoints
# =========================================================================

@router.get("/status")
async def get_compliance_status() -> Dict[str, Any]:
    """
    Get current compliance status.
    
    Returns:
        Current PDT status, restrictions, and trading status.
    """
    compliance = get_compliance_manager()
    return compliance.get_status()


@router.get("/day-trades")
async def get_day_trades() -> Dict[str, Any]:
    """
    Get recent day trades.
    
    Returns:
        List of day trades in the last 5 business days.
    """
    compliance = get_compliance_manager()
    trades = compliance.get_day_trades()
    count = len([t for t in trades if t])
    
    return {
        "day_trades": trades,
        "count": count,
        "threshold": compliance.PDT_THRESHOLD,
        "remaining": max(0, compliance.PDT_THRESHOLD - count - 1),
    }


@router.get("/pdt-status")
async def get_pdt_status() -> Dict[str, Any]:
    """
    Get Pattern Day Trader status.
    
    Returns:
        PDT-specific status including day trade count and equity.
    """
    compliance = get_compliance_manager()
    status = compliance.get_status()
    return status["pdt_status"]


@router.get("/violations")
async def get_violations(limit: int = 20) -> Dict[str, Any]:
    """
    Get recent compliance violations.
    
    Args:
        limit: Maximum number of violations to return.
        
    Returns:
        List of recent violations and warnings.
    """
    compliance = get_compliance_manager()
    violations = compliance._violations[-limit:]
    
    return {
        "violations": [v.to_dict() for v in violations],
        "total_count": len(compliance._violations),
    }


# =========================================================================
# Pre-Trade Check Endpoints
# =========================================================================

@router.post("/check")
async def pre_trade_check(request: PreTradeCheckRequest) -> Dict[str, Any]:
    """
    Perform pre-trade compliance check.
    
    This should be called before placing any order to check for:
    - Pattern Day Trader violations
    - Good Faith violations
    - Freeriding violations
    - Day Trading Buying Power limits
    - Wash Sale warnings
    
    Args:
        request: Trade details to check.
        
    Returns:
        ComplianceCheckResult with allowed status and any violations.
    """
    compliance = get_compliance_manager()
    
    result = compliance.check_order(
        symbol=request.symbol.upper(),
        side=request.side.lower(),
        quantity=request.quantity,
        estimated_price=request.estimated_price,
        is_closing=request.is_closing,
    )
    
    response = result.to_dict()
    response["symbol"] = request.symbol.upper()
    response["side"] = request.side.lower()
    response["quantity"] = request.quantity
    
    return response


@router.post("/check-bulk")
async def bulk_pre_trade_check(orders: List[PreTradeCheckRequest]) -> Dict[str, Any]:
    """
    Check multiple orders for compliance.
    
    Args:
        orders: List of orders to check.
        
    Returns:
        Results for each order.
    """
    compliance = get_compliance_manager()
    results = []
    
    for order in orders:
        result = compliance.check_order(
            symbol=order.symbol.upper(),
            side=order.side.lower(),
            quantity=order.quantity,
            estimated_price=order.estimated_price,
            is_closing=order.is_closing,
        )
        
        order_result = result.to_dict()
        order_result["symbol"] = order.symbol.upper()
        order_result["side"] = order.side.lower()
        results.append(order_result)
    
    # Aggregate results
    all_allowed = all(r["allowed"] for r in results)
    any_requires_confirmation = any(r["requires_confirmation"] for r in results)
    any_stop_trading = any(r["stop_trading"] for r in results)
    
    return {
        "results": results,
        "summary": {
            "all_allowed": all_allowed,
            "any_requires_confirmation": any_requires_confirmation,
            "any_stop_trading": any_stop_trading,
            "total_orders": len(orders),
            "blocked_orders": len([r for r in results if not r["allowed"]]),
        }
    }


# =========================================================================
# Trade Recording Endpoints
# =========================================================================

@router.post("/record-trade")
async def record_trade(request: RecordTradeRequest) -> Dict[str, Any]:
    """
    Record a completed trade for compliance tracking.
    
    This should be called after a trade is executed to track:
    - Day trades
    - Unsettled positions
    - Trade history for wash sale detection
    
    Args:
        request: Executed trade details.
        
    Returns:
        Any violations triggered by this trade.
    """
    compliance = get_compliance_manager()
    
    violations = compliance.record_trade(
        symbol=request.symbol.upper(),
        side=request.side.lower(),
        quantity=request.quantity,
        price=request.price,
    )
    
    return {
        "recorded": True,
        "violations": [v.to_dict() for v in violations],
        "status": compliance.get_status(),
    }


# =========================================================================
# Account Management Endpoints
# =========================================================================

@router.post("/account/update")
async def update_account(request: AccountUpdateRequest) -> Dict[str, Any]:
    """
    Update account information for compliance tracking.
    
    This should be called periodically to update:
    - Account equity
    - Buying power
    - Day trading buying power
    - PDT status
    
    Args:
        request: Updated account values.
        
    Returns:
        Updated compliance status.
    """
    compliance = get_compliance_manager()
    
    # Update account type if provided
    if request.account_type:
        from src.compliance import AccountType
        try:
            compliance.account_type = AccountType(request.account_type.lower())
        except ValueError:
            raise HTTPException(400, f"Invalid account type: {request.account_type}")
    
    compliance.update_account(
        equity=request.equity,
        buying_power=request.buying_power,
        day_trading_buying_power=request.day_trading_buying_power,
        is_pattern_day_trader=request.is_pattern_day_trader,
    )
    
    return compliance.get_status()


@router.post("/account/sync")
async def sync_account_from_broker() -> Dict[str, Any]:
    """
    Sync account information from connected broker.
    
    Fetches current account data from the broker and updates
    the compliance manager.
    
    Returns:
        Synced account status.
    """
    from src.brokers.registry import get_broker_registry
    
    registry = get_broker_registry()
    broker = registry.get_default_broker()
    
    if not broker:
        raise HTTPException(400, "No broker connected")
    
    try:
        accounts = await broker.get_accounts()
        if not accounts:
            raise HTTPException(400, "No accounts found")
        
        account = accounts[0]
        compliance = get_compliance_manager()
        
        # Determine account type
        from src.compliance import AccountType
        account_type_map = {
            "cash": AccountType.CASH,
            "margin": AccountType.MARGIN,
            "ira": AccountType.IRA,
        }
        compliance.account_type = account_type_map.get(
            account.account_type.lower(), 
            AccountType.MARGIN
        )
        
        compliance.update_account(
            equity=account.equity,
            buying_power=account.buying_power,
            day_trading_buying_power=account.margin_available * 4 if account.account_type == "margin" else 0,
            is_pattern_day_trader=account.is_pattern_day_trader,
        )
        
        return {
            "synced": True,
            "account_id": account.account_id,
            "broker": account.broker.value,
            "status": compliance.get_status(),
        }
        
    except Exception as e:
        raise HTTPException(500, f"Failed to sync account: {e}")


# =========================================================================
# Control Endpoints
# =========================================================================

@router.post("/reset-daily")
async def reset_daily() -> Dict[str, Any]:
    """
    Reset daily compliance counters.
    
    Call this at market open to reset:
    - Today's day trade count
    - Trading stopped status
    - Intraday positions
    
    Returns:
        Reset status.
    """
    compliance = get_compliance_manager()
    compliance.reset_daily()
    
    return {
        "reset": True,
        "status": compliance.get_status(),
    }


@router.post("/resume-trading")
async def resume_trading() -> Dict[str, Any]:
    """
    Resume trading after it was stopped.
    
    Note: This does not override PDT restrictions or account locks.
    It only resumes trading that was stopped by compliance rules.
    
    Returns:
        Trading status.
    """
    compliance = get_compliance_manager()
    compliance._trading_stopped = False
    compliance._stop_reason = None
    
    return {
        "resumed": True,
        "status": compliance.get_status(),
    }


@router.post("/confirm-proceed")
async def confirm_proceed(symbol: str, side: str) -> Dict[str, Any]:
    """
    Confirm proceeding with a trade despite warnings.
    
    Use this when the user has acknowledged a compliance warning
    and wishes to proceed with the trade.
    
    Args:
        symbol: Stock symbol
        side: 'buy' or 'sell'
        
    Returns:
        Confirmation status.
    """
    # Log the user's acknowledgment
    from loguru import logger
    logger.info(f"User confirmed proceeding with {side} {symbol} despite compliance warnings")
    
    return {
        "confirmed": True,
        "message": f"You have acknowledged the compliance warnings for {side} {symbol}.",
    }


# =========================================================================
# Info Endpoints
# =========================================================================

@router.get("/rules")
async def get_compliance_rules() -> Dict[str, Any]:
    """
    Get information about trading compliance rules.
    
    Returns:
        Description of all compliance rules enforced.
    """
    return {
        "rules": [
            {
                "id": "pdt",
                "name": "Pattern Day Trader (PDT) Rule",
                "regulation": "FINRA Rule 4210",
                "description": (
                    "If you execute 4 or more day trades within 5 business days in a margin account, "
                    "you are classified as a Pattern Day Trader. PDT accounts must maintain $25,000 "
                    "minimum equity at all times."
                ),
                "threshold": 4,
                "lookback_days": 5,
                "equity_requirement": 25000,
                "applies_to": ["margin"],
            },
            {
                "id": "good_faith",
                "name": "Good Faith Violation",
                "regulation": "Regulation T / FINRA",
                "description": (
                    "In a cash account, selling a security before the purchase has settled (T+1) "
                    "is a Good Faith Violation. Three violations in 12 months results in a "
                    "90-day cash-upfront restriction."
                ),
                "settlement_days": 1,
                "applies_to": ["cash"],
            },
            {
                "id": "freeriding",
                "name": "Freeriding Violation",
                "regulation": "Regulation T",
                "description": (
                    "In a cash account, buying securities with unsettled proceeds and selling "
                    "before the original sale settles is a Freeriding Violation. This results "
                    "in a 90-day cash-upfront restriction."
                ),
                "restriction_days": 90,
                "applies_to": ["cash"],
            },
            {
                "id": "dtbp",
                "name": "Day Trading Buying Power",
                "regulation": "FINRA Margin Rules",
                "description": (
                    "Pattern Day Traders have access to 4x their maintenance margin excess for "
                    "day trading. Exceeding this limit results in a margin call requiring "
                    "immediate deposit."
                ),
                "multiplier": 4,
                "applies_to": ["margin", "pdt"],
            },
            {
                "id": "wash_sale",
                "name": "Wash Sale Rule",
                "regulation": "IRS Section 1091",
                "description": (
                    "If you sell a security at a loss and repurchase the same or substantially "
                    "identical security within 30 days (before or after), the loss is disallowed "
                    "for tax purposes."
                ),
                "window_days": 30,
                "applies_to": ["all"],
            },
            {
                "id": "settlement",
                "name": "Settlement Rules (T+1)",
                "regulation": "SEC Rule 15c6-1",
                "description": (
                    "Stock trades settle T+1 (one business day after trade date). As of May 2024, "
                    "settlement was reduced from T+2 to T+1. The SEC is considering T+0 for "
                    "2025/2026."
                ),
                "settlement_days": 1,
                "proposed_changes": "T+0 being considered for 2025/2026",
                "applies_to": ["all"],
            },
        ],
        "upcoming_changes": [
            {
                "title": "T+0 Settlement (Proposed)",
                "description": (
                    "The SEC is considering moving to same-day settlement (T+0) for stocks. "
                    "This would significantly reduce settlement risk but may require system changes."
                ),
                "expected": "2025-2026",
                "status": "Under consideration",
            },
            {
                "title": "Enhanced PDT Monitoring",
                "description": (
                    "FINRA may enhance PDT monitoring requirements with more real-time tracking "
                    "and automated enforcement."
                ),
                "expected": "2025",
                "status": "Proposed",
            },
        ],
    }


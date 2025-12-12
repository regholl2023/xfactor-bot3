"""API routes for fee tracking and expense reporting."""

from datetime import date, datetime
from typing import Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel

from src.fees.fee_tracker import get_fee_tracker, FeeType

router = APIRouter()


class FeeCalculationRequest(BaseModel):
    symbol: str
    quantity: float
    price: float
    broker: Optional[str] = None
    instrument_type: str = "stock"  # stock, options, futures, crypto
    is_sell: bool = False
    contracts: Optional[int] = None


@router.get("/summary")
async def get_fee_summary(
    start_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date YYYY-MM-DD"),
):
    """Get fee summary for a period."""
    tracker = get_fee_tracker()
    
    start = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
    end = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None
    
    report = tracker.generate_report(start, end)
    
    return {
        "period": {
            "start": report.period_start.isoformat(),
            "end": report.period_end.isoformat(),
        },
        "totals": {
            "total_fees": round(report.total_fees, 2),
            "fees_pct_of_portfolio": round(report.fees_as_pct_of_portfolio, 4),
            "fees_pct_of_volume": round(report.fees_as_pct_of_volume, 4),
            "trade_count": report.trade_count,
            "avg_fee_per_trade": round(report.avg_fee_per_trade, 2),
            "total_trade_volume": round(report.total_trade_volume, 2),
            "portfolio_value": round(report.portfolio_value, 2),
        },
        "breakdown_by_type": {
            k.value: round(v, 2) for k, v in report.fee_breakdown.items()
        },
        "breakdown_by_broker": {
            k: round(v, 2) for k, v in report.fees_by_broker.items()
        },
        "breakdown_by_bot": {
            k: round(v, 2) for k, v in report.fees_by_bot.items()
        },
    }


@router.get("/breakdown")
async def get_fee_breakdown():
    """Get breakdown of fees by type."""
    tracker = get_fee_tracker()
    breakdown = tracker.get_fee_breakdown()
    
    return {
        "breakdown": {k.value: round(v, 2) for k, v in breakdown.items()},
        "total": round(sum(breakdown.values()), 2),
    }


@router.get("/by-broker")
async def get_fees_by_broker():
    """Get fees grouped by broker."""
    tracker = get_fee_tracker()
    by_broker = tracker.get_fees_by_broker()
    
    return {
        "by_broker": {k: round(v, 2) for k, v in by_broker.items()},
        "total": round(sum(by_broker.values()), 2),
    }


@router.get("/by-bot")
async def get_fees_by_bot():
    """Get fees grouped by bot."""
    tracker = get_fee_tracker()
    by_bot = tracker.get_fees_by_bot()
    
    return {
        "by_bot": {k: round(v, 2) for k, v in by_bot.items()},
        "total": round(sum(by_bot.values()), 2),
    }


@router.post("/calculate")
async def calculate_fees(request: FeeCalculationRequest):
    """Calculate estimated fees for a trade."""
    tracker = get_fee_tracker()
    
    if request.instrument_type == "stock":
        fees = tracker.calculate_stock_fee(
            symbol=request.symbol,
            quantity=request.quantity,
            price=request.price,
            broker=request.broker,
            is_sell=request.is_sell,
        )
    elif request.instrument_type == "options":
        contracts = request.contracts or int(abs(request.quantity))
        fees = tracker.calculate_options_fee(
            contracts=contracts,
            price_per_contract=request.price,
            broker=request.broker,
        )
    elif request.instrument_type == "futures":
        contracts = request.contracts or int(abs(request.quantity))
        fees = tracker.calculate_futures_fee(
            contracts=contracts,
            broker=request.broker,
        )
    elif request.instrument_type == "crypto":
        fees = tracker.calculate_crypto_fee(
            symbol=request.symbol,
            quantity=request.quantity,
            price=request.price,
            broker=request.broker,
        )
    else:
        fees = {}
    
    total = sum(fees.values())
    trade_value = abs(request.quantity * request.price)
    
    return {
        "trade": {
            "symbol": request.symbol,
            "quantity": request.quantity,
            "price": request.price,
            "value": round(trade_value, 2),
        },
        "fees": {k.value: round(v, 4) for k, v in fees.items()},
        "total_fees": round(total, 4),
        "fee_pct": round((total / trade_value * 100) if trade_value > 0 else 0, 4),
    }


@router.get("/brokers")
async def get_broker_fee_structures():
    """Get available broker fee structures."""
    tracker = get_fee_tracker()
    return {"brokers": tracker.get_available_brokers()}


@router.get("/estimate")
async def estimate_monthly_fees(
    trades_per_day: int = Query(10, description="Average trades per day"),
    avg_trade_value: float = Query(5000, description="Average trade value"),
    broker: str = Query("ibkr_pro", description="Broker ID"),
):
    """Estimate monthly fees based on trading activity."""
    tracker = get_fee_tracker()
    
    # Calculate per-trade fees
    stock_fees = tracker.calculate_stock_fee(
        symbol="SPY",
        quantity=avg_trade_value / 500,  # Assuming ~$500 per share avg
        price=500,
        broker=broker,
        is_sell=False,
    )
    
    per_trade_fee = sum(stock_fees.values())
    trading_days = 21  # Avg trading days per month
    
    monthly_trades = trades_per_day * trading_days
    monthly_volume = monthly_trades * avg_trade_value
    monthly_fees = monthly_trades * per_trade_fee
    
    return {
        "estimate": {
            "monthly_trades": monthly_trades,
            "monthly_volume": round(monthly_volume, 2),
            "monthly_fees": round(monthly_fees, 2),
            "yearly_fees": round(monthly_fees * 12, 2),
            "fee_per_trade": round(per_trade_fee, 4),
            "fee_pct_of_volume": round((monthly_fees / monthly_volume * 100) if monthly_volume > 0 else 0, 4),
        },
        "assumptions": {
            "trades_per_day": trades_per_day,
            "avg_trade_value": avg_trade_value,
            "trading_days_per_month": trading_days,
            "broker": broker,
        },
    }


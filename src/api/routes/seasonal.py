"""
Seasonal Events API Routes.

Provides endpoints for seasonal calendar information,
active events, and trading adjustments.
"""

from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

from src.strategies.seasonal_events import get_seasonal_calendar


router = APIRouter(prefix="/api/seasonal", tags=["seasonal"])


class SeasonalContextResponse(BaseModel):
    """Full seasonal context response."""
    date: str
    season: str
    is_holiday_period: bool
    is_earnings_season: bool
    overall_adjustment: float
    market_impact: str
    market_impact_description: str
    active_events: list[dict]
    upcoming_events: list[dict]


class SeasonalAdjustmentResponse(BaseModel):
    """Seasonal adjustment for a sector."""
    sector: Optional[str]
    adjustment: float
    active_events: list[str]


class ActiveEventResponse(BaseModel):
    """Active event details."""
    name: str
    impact: str
    adjustment: float
    sectors: list[str]
    description: str
    start_date: str
    end_date: str


@router.get("/context", response_model=SeasonalContextResponse)
async def get_seasonal_context(
    target_date: Optional[str] = Query(
        None,
        description="Date to check in YYYY-MM-DD format (defaults to today)"
    )
) -> SeasonalContextResponse:
    """
    Get the current seasonal context.
    
    Returns information about:
    - Current season (spring, summer, fall, winter)
    - Active seasonal events (Black Friday, Santa Rally, etc.)
    - Upcoming events in the next 14 days
    - Overall market adjustment factor
    - Holiday and earnings season indicators
    """
    calendar = get_seasonal_calendar()
    
    # Parse target date if provided
    check_date = None
    if target_date:
        try:
            check_date = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            pass
    
    context = calendar.get_seasonal_context(check_date)
    
    return SeasonalContextResponse(
        date=context["date"],
        season=context["season"],
        is_holiday_period=context["is_holiday_period"],
        is_earnings_season=context["is_earnings_season"],
        overall_adjustment=context["overall_adjustment"],
        market_impact=context["market_impact"],
        market_impact_description=context["market_impact_description"],
        active_events=context["active_events"],
        upcoming_events=context["upcoming_events"],
    )


@router.get("/adjustment", response_model=SeasonalAdjustmentResponse)
async def get_seasonal_adjustment(
    sector: Optional[str] = Query(
        None,
        description="Sector to get adjustment for (e.g., retail, technology, energy)"
    ),
    target_date: Optional[str] = Query(
        None,
        description="Date to check in YYYY-MM-DD format (defaults to today)"
    )
) -> SeasonalAdjustmentResponse:
    """
    Get the seasonal adjustment multiplier for trading signals.
    
    The adjustment is a multiplier applied to signal strength:
    - > 1.0: Favorable seasonal period (boost signals)
    - < 1.0: Unfavorable seasonal period (reduce signals)
    - = 1.0: No significant seasonal impact
    
    Optionally filter by sector for more targeted adjustments.
    """
    calendar = get_seasonal_calendar()
    
    # Parse target date if provided
    check_date = None
    if target_date:
        try:
            check_date = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            pass
    
    adjustment, events = calendar.get_seasonal_adjustment(sector, check_date)
    
    return SeasonalAdjustmentResponse(
        sector=sector,
        adjustment=adjustment,
        active_events=events,
    )


@router.get("/events/active", response_model=list[ActiveEventResponse])
async def get_active_events(
    target_date: Optional[str] = Query(
        None,
        description="Date to check in YYYY-MM-DD format (defaults to today)"
    )
) -> list[ActiveEventResponse]:
    """
    Get all currently active seasonal events.
    
    Returns detailed information about each active event including
    market impact, affected sectors, and trading adjustment.
    """
    calendar = get_seasonal_calendar()
    
    # Parse target date if provided
    check_date = None
    if target_date:
        try:
            check_date = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            pass
    
    events = calendar.get_active_events(check_date)
    
    return [
        ActiveEventResponse(
            name=e.name,
            impact=e.impact.name,
            adjustment=e.trading_adjustment,
            sectors=e.sectors_affected,
            description=e.description,
            start_date=e.start_date.isoformat(),
            end_date=e.end_date.isoformat(),
        )
        for e in events
    ]


@router.get("/events/upcoming", response_model=list[dict])
async def get_upcoming_events(
    days_ahead: int = Query(
        14,
        ge=1,
        le=90,
        description="Number of days to look ahead (1-90)"
    ),
    target_date: Optional[str] = Query(
        None,
        description="Starting date in YYYY-MM-DD format (defaults to today)"
    )
) -> list[dict]:
    """
    Get upcoming seasonal events within the specified number of days.
    
    Useful for planning trading strategies around upcoming
    holidays, earnings seasons, and market patterns.
    """
    calendar = get_seasonal_calendar()
    
    # Parse target date if provided
    check_date = None
    if target_date:
        try:
            check_date = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            pass
    
    events = calendar.get_upcoming_events(days_ahead, check_date)
    
    return [
        {
            "name": e.name,
            "starts": e.start_date.isoformat(),
            "ends": e.end_date.isoformat(),
            "impact": e.impact.name,
            "adjustment": e.trading_adjustment,
            "sectors": e.sectors_affected,
            "description": e.description,
        }
        for e in events
    ]


@router.get("/season")
async def get_current_season() -> dict:
    """
    Get the current calendar season.
    
    Returns:
    - season: spring, summer, fall, or winter
    - date: Current date
    """
    calendar = get_seasonal_calendar()
    
    return {
        "season": calendar.get_current_season().value,
        "date": calendar.current_date.isoformat(),
    }


@router.get("/holiday-check")
async def check_holiday_period(
    target_date: Optional[str] = Query(
        None,
        description="Date to check in YYYY-MM-DD format (defaults to today)"
    )
) -> dict:
    """
    Check if a date falls within a major holiday shopping period.
    
    Holiday periods include:
    - Black Friday / Cyber Monday
    - Christmas Shopping Season
    - Valentine's Day
    - Mother's Day
    """
    calendar = get_seasonal_calendar()
    
    # Parse target date if provided
    check_date = None
    if target_date:
        try:
            check_date = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            pass
    
    is_holiday = calendar.is_holiday_period(check_date)
    active_events = calendar.get_active_events(check_date)
    
    holiday_events = [
        e.name for e in active_events
        if e.name in ["Black Friday", "Cyber Monday", "Christmas Shopping Season",
                      "Valentine's Day", "Mother's Day"]
    ]
    
    return {
        "is_holiday_period": is_holiday,
        "date": (check_date or calendar.current_date).isoformat(),
        "active_holiday_events": holiday_events,
    }


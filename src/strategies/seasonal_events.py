"""
Seasonal Events and Holiday Calendar for Trading Strategies.

Provides awareness of market-moving seasonal events, holidays, and patterns
that affect stock momentum and trends.
"""

from dataclasses import dataclass
from datetime import datetime, date, timedelta
from enum import Enum
from typing import Optional
import calendar


class Season(Enum):
    """Calendar seasons."""
    SPRING = "spring"
    SUMMER = "summer"
    FALL = "fall"
    WINTER = "winter"


class MarketImpact(Enum):
    """Expected market impact of an event."""
    VERY_BULLISH = 2.0      # Strong positive momentum expected
    BULLISH = 1.5           # Moderate positive momentum
    SLIGHTLY_BULLISH = 1.2  # Slight positive bias
    NEUTRAL = 1.0           # No significant impact
    SLIGHTLY_BEARISH = 0.8  # Slight negative bias
    BEARISH = 0.6           # Moderate negative momentum
    VERY_BEARISH = 0.4      # Strong negative momentum expected


@dataclass
class SeasonalEvent:
    """Represents a seasonal or holiday event."""
    name: str
    start_date: date
    end_date: date
    impact: MarketImpact
    sectors_affected: list[str]  # Affected sectors (empty = all)
    description: str
    trading_adjustment: float  # Multiplier for signal strength


class SeasonalEventsCalendar:
    """
    Calendar of seasonal events that affect market behavior.
    
    Provides real-time detection of:
    - Major holidays (Christmas, Black Friday, etc.)
    - Seasonal patterns (Summer doldrums, Santa Rally)
    - Earnings seasons
    - Tax-related periods
    - Market-specific events
    """
    
    def __init__(self, reference_date: Optional[datetime] = None):
        """
        Initialize the seasonal calendar.
        
        Args:
            reference_date: Date to use for calculations (defaults to now)
        """
        self._reference_date = reference_date or datetime.now()
        self._events_cache: dict[int, list[SeasonalEvent]] = {}
    
    @property
    def current_date(self) -> date:
        """Get the current date being used."""
        return self._reference_date.date()
    
    def refresh_date(self) -> None:
        """Update to current date/time."""
        self._reference_date = datetime.now()
    
    def get_current_season(self) -> Season:
        """
        Get the current calendar season.
        
        Based on meteorological seasons:
        - Spring: March - May
        - Summer: June - August
        - Fall: September - November
        - Winter: December - February
        """
        month = self.current_date.month
        
        if month in (3, 4, 5):
            return Season.SPRING
        elif month in (6, 7, 8):
            return Season.SUMMER
        elif month in (9, 10, 11):
            return Season.FALL
        else:
            return Season.WINTER
    
    def get_events_for_year(self, year: int) -> list[SeasonalEvent]:
        """Get all seasonal events for a given year."""
        if year in self._events_cache:
            return self._events_cache[year]
        
        events = self._build_events_for_year(year)
        self._events_cache[year] = events
        return events
    
    def _build_events_for_year(self, year: int) -> list[SeasonalEvent]:
        """Build the list of seasonal events for a year."""
        events = []
        
        # === MAJOR SHOPPING HOLIDAYS ===
        
        # Black Friday (Day after Thanksgiving - 4th Thursday of November)
        thanksgiving = self._get_nth_weekday_of_month(year, 11, 3, 4)  # 4th Thursday
        black_friday = thanksgiving + timedelta(days=1)
        events.append(SeasonalEvent(
            name="Black Friday",
            start_date=black_friday - timedelta(days=7),  # Pre-Black Friday buildup
            end_date=black_friday + timedelta(days=3),    # Cyber Monday included
            impact=MarketImpact.VERY_BULLISH,
            sectors_affected=["retail", "e-commerce", "consumer_discretionary", "technology"],
            description="Biggest shopping day - retail stocks surge",
            trading_adjustment=1.3,
        ))
        
        # Cyber Monday
        cyber_monday = black_friday + timedelta(days=3)
        events.append(SeasonalEvent(
            name="Cyber Monday",
            start_date=cyber_monday,
            end_date=cyber_monday,
            impact=MarketImpact.BULLISH,
            sectors_affected=["e-commerce", "technology", "payments"],
            description="Online shopping surge",
            trading_adjustment=1.2,
        ))
        
        # Christmas Shopping Season
        events.append(SeasonalEvent(
            name="Christmas Shopping Season",
            start_date=date(year, 11, 15),
            end_date=date(year, 12, 24),
            impact=MarketImpact.BULLISH,
            sectors_affected=["retail", "consumer_discretionary", "logistics", "e-commerce"],
            description="Holiday shopping drives retail momentum",
            trading_adjustment=1.15,
        ))
        
        # === MARKET PATTERNS ===
        
        # Santa Claus Rally (Last 5 trading days of year + first 2 of new year)
        events.append(SeasonalEvent(
            name="Santa Claus Rally",
            start_date=date(year, 12, 24),
            end_date=date(year + 1, 1, 3),
            impact=MarketImpact.BULLISH,
            sectors_affected=[],  # All sectors
            description="Historical pattern of year-end market rally",
            trading_adjustment=1.2,
        ))
        
        # January Effect (Small caps outperform)
        events.append(SeasonalEvent(
            name="January Effect",
            start_date=date(year, 1, 2),
            end_date=date(year, 1, 31),
            impact=MarketImpact.SLIGHTLY_BULLISH,
            sectors_affected=["small_cap"],
            description="Small cap stocks historically outperform in January",
            trading_adjustment=1.1,
        ))
        
        # Summer Doldrums (Low volume, sideways trading)
        events.append(SeasonalEvent(
            name="Summer Doldrums",
            start_date=date(year, 7, 1),
            end_date=date(year, 8, 31),
            impact=MarketImpact.SLIGHTLY_BEARISH,
            sectors_affected=[],
            description="Low volume period - 'Sell in May and go away'",
            trading_adjustment=0.85,
        ))
        
        # September Effect (Historically weak month)
        events.append(SeasonalEvent(
            name="September Effect",
            start_date=date(year, 9, 1),
            end_date=date(year, 9, 30),
            impact=MarketImpact.SLIGHTLY_BEARISH,
            sectors_affected=[],
            description="September historically weakest month for stocks",
            trading_adjustment=0.9,
        ))
        
        # Q4 Rally (October - December bullish trend)
        events.append(SeasonalEvent(
            name="Q4 Rally Season",
            start_date=date(year, 10, 15),
            end_date=date(year, 12, 31),
            impact=MarketImpact.BULLISH,
            sectors_affected=[],
            description="Historically strong end-of-year performance",
            trading_adjustment=1.15,
        ))
        
        # === EARNINGS SEASONS ===
        
        # Q1 Earnings (April-May)
        events.append(SeasonalEvent(
            name="Q1 Earnings Season",
            start_date=date(year, 4, 10),
            end_date=date(year, 5, 15),
            impact=MarketImpact.NEUTRAL,
            sectors_affected=[],
            description="Q1 earnings reports - increased volatility",
            trading_adjustment=1.0,
        ))
        
        # Q2 Earnings (July-August)
        events.append(SeasonalEvent(
            name="Q2 Earnings Season",
            start_date=date(year, 7, 10),
            end_date=date(year, 8, 15),
            impact=MarketImpact.NEUTRAL,
            sectors_affected=[],
            description="Q2 earnings reports - increased volatility",
            trading_adjustment=1.0,
        ))
        
        # Q3 Earnings (October-November)
        events.append(SeasonalEvent(
            name="Q3 Earnings Season",
            start_date=date(year, 10, 10),
            end_date=date(year, 11, 15),
            impact=MarketImpact.NEUTRAL,
            sectors_affected=[],
            description="Q3 earnings reports - increased volatility",
            trading_adjustment=1.0,
        ))
        
        # Q4 Earnings (January-February next year)
        events.append(SeasonalEvent(
            name="Q4 Earnings Season",
            start_date=date(year, 1, 10),
            end_date=date(year, 2, 28),
            impact=MarketImpact.NEUTRAL,
            sectors_affected=[],
            description="Q4 earnings reports - increased volatility",
            trading_adjustment=1.0,
        ))
        
        # === TAX-RELATED EVENTS ===
        
        # Tax Loss Harvesting Season
        events.append(SeasonalEvent(
            name="Tax Loss Harvesting",
            start_date=date(year, 10, 1),
            end_date=date(year, 12, 31),
            impact=MarketImpact.SLIGHTLY_BEARISH,
            sectors_affected=["losers_ytd"],  # Stocks down for the year
            description="Investors sell losing positions for tax benefits",
            trading_adjustment=0.9,
        ))
        
        # Tax Deadline Rally
        events.append(SeasonalEvent(
            name="Post-Tax Deadline Rally",
            start_date=date(year, 4, 16),
            end_date=date(year, 4, 30),
            impact=MarketImpact.SLIGHTLY_BULLISH,
            sectors_affected=[],
            description="Market often rallies after tax selling pressure ends",
            trading_adjustment=1.1,
        ))
        
        # === SECTOR-SPECIFIC SEASONAL EVENTS ===
        
        # Back to School (Retail)
        events.append(SeasonalEvent(
            name="Back to School Season",
            start_date=date(year, 7, 15),
            end_date=date(year, 9, 15),
            impact=MarketImpact.BULLISH,
            sectors_affected=["retail", "technology", "apparel"],
            description="Second largest shopping season after holidays",
            trading_adjustment=1.15,
        ))
        
        # Valentine's Day
        events.append(SeasonalEvent(
            name="Valentine's Day",
            start_date=date(year, 2, 1),
            end_date=date(year, 2, 14),
            impact=MarketImpact.SLIGHTLY_BULLISH,
            sectors_affected=["retail", "restaurants", "luxury", "flowers"],
            description="Consumer spending on gifts and dining",
            trading_adjustment=1.1,
        ))
        
        # Mother's Day
        mothers_day = self._get_nth_weekday_of_month(year, 5, 6, 2)  # 2nd Sunday of May
        events.append(SeasonalEvent(
            name="Mother's Day",
            start_date=mothers_day - timedelta(days=14),
            end_date=mothers_day,
            impact=MarketImpact.SLIGHTLY_BULLISH,
            sectors_affected=["retail", "restaurants", "flowers", "jewelry"],
            description="Gift and dining spending surge",
            trading_adjustment=1.1,
        ))
        
        # Prime Day (Amazon) - Usually mid-July
        events.append(SeasonalEvent(
            name="Amazon Prime Day",
            start_date=date(year, 7, 10),
            end_date=date(year, 7, 17),
            impact=MarketImpact.BULLISH,
            sectors_affected=["e-commerce", "technology", "logistics"],
            description="Major e-commerce sales event",
            trading_adjustment=1.2,
        ))
        
        # Travel Season (Summer)
        events.append(SeasonalEvent(
            name="Summer Travel Season",
            start_date=date(year, 5, 25),  # Memorial Day weekend
            end_date=date(year, 9, 5),      # Labor Day
            impact=MarketImpact.BULLISH,
            sectors_affected=["airlines", "hotels", "cruise", "travel", "energy"],
            description="Peak travel and tourism season",
            trading_adjustment=1.15,
        ))
        
        # Winter/Heating Season
        events.append(SeasonalEvent(
            name="Heating Season",
            start_date=date(year, 11, 1),
            end_date=date(year + 1, 3, 31) if year else date(year, 3, 31),
            impact=MarketImpact.BULLISH,
            sectors_affected=["natural_gas", "utilities", "energy"],
            description="Increased demand for heating fuels",
            trading_adjustment=1.15,
        ))
        
        # Hurricane Season
        events.append(SeasonalEvent(
            name="Hurricane Season",
            start_date=date(year, 6, 1),
            end_date=date(year, 11, 30),
            impact=MarketImpact.NEUTRAL,  # Variable based on actual storms
            sectors_affected=["insurance", "energy", "construction", "home_improvement"],
            description="Atlantic hurricane season - volatility in affected sectors",
            trading_adjustment=1.0,
        ))
        
        # Super Bowl
        # First Sunday in February
        super_bowl = self._get_nth_weekday_of_month(year, 2, 6, 1)  # 1st Sunday of Feb
        events.append(SeasonalEvent(
            name="Super Bowl",
            start_date=super_bowl - timedelta(days=14),
            end_date=super_bowl,
            impact=MarketImpact.SLIGHTLY_BULLISH,
            sectors_affected=["media", "advertising", "food_beverage", "retail"],
            description="Major advertising and consumer spending event",
            trading_adjustment=1.1,
        ))
        
        return events
    
    def _get_nth_weekday_of_month(
        self, 
        year: int, 
        month: int, 
        weekday: int,  # 0=Monday, 6=Sunday
        n: int
    ) -> date:
        """Get the nth occurrence of a weekday in a month."""
        first_day = date(year, month, 1)
        first_weekday = first_day.weekday()
        
        # Days until first occurrence of target weekday
        days_until = (weekday - first_weekday) % 7
        first_occurrence = first_day + timedelta(days=days_until)
        
        # Add weeks to get to nth occurrence
        return first_occurrence + timedelta(weeks=n-1)
    
    def get_active_events(self, target_date: Optional[date] = None) -> list[SeasonalEvent]:
        """
        Get all events active on a given date.
        
        Args:
            target_date: Date to check (defaults to current date)
            
        Returns:
            List of active events
        """
        check_date = target_date or self.current_date
        year = check_date.year
        
        # Get events for current and adjacent years (for events spanning year boundaries)
        all_events = []
        for y in [year - 1, year, year + 1]:
            all_events.extend(self.get_events_for_year(y))
        
        # Filter to active events
        active = [
            event for event in all_events
            if event.start_date <= check_date <= event.end_date
        ]
        
        return active
    
    def get_upcoming_events(
        self, 
        days_ahead: int = 14,
        target_date: Optional[date] = None
    ) -> list[SeasonalEvent]:
        """
        Get events starting within the next N days.
        
        Args:
            days_ahead: Number of days to look ahead
            target_date: Starting date (defaults to current)
            
        Returns:
            List of upcoming events
        """
        start_date = target_date or self.current_date
        end_date = start_date + timedelta(days=days_ahead)
        year = start_date.year
        
        all_events = self.get_events_for_year(year)
        if start_date.month >= 11:  # Include next year events if near year end
            all_events.extend(self.get_events_for_year(year + 1))
        
        upcoming = [
            event for event in all_events
            if start_date <= event.start_date <= end_date
        ]
        
        # Sort by start date
        upcoming.sort(key=lambda e: e.start_date)
        return upcoming
    
    def get_seasonal_adjustment(
        self,
        sector: Optional[str] = None,
        target_date: Optional[date] = None
    ) -> tuple[float, list[str]]:
        """
        Calculate the seasonal adjustment multiplier for signals.
        
        Args:
            sector: Optional sector to get specific adjustment
            target_date: Date to check (defaults to current)
            
        Returns:
            Tuple of (adjustment_multiplier, list of active event names)
        """
        active_events = self.get_active_events(target_date)
        
        if not active_events:
            return 1.0, []
        
        # Filter events by sector if specified
        if sector:
            sector_events = [
                e for e in active_events
                if not e.sectors_affected or sector.lower() in [s.lower() for s in e.sectors_affected]
            ]
        else:
            sector_events = active_events
        
        if not sector_events:
            return 1.0, []
        
        # Combine adjustments (weighted average favoring stronger effects)
        adjustments = [e.trading_adjustment for e in sector_events]
        event_names = [e.name for e in sector_events]
        
        # Use geometric mean for combining multipliers
        from functools import reduce
        import operator
        combined = reduce(operator.mul, adjustments, 1) ** (1 / len(adjustments))
        
        return round(combined, 3), event_names
    
    def get_market_impact(
        self,
        target_date: Optional[date] = None
    ) -> tuple[MarketImpact, str]:
        """
        Get the overall market impact for a date.
        
        Returns:
            Tuple of (MarketImpact, description)
        """
        active_events = self.get_active_events(target_date)
        
        if not active_events:
            season = self.get_current_season()
            return MarketImpact.NEUTRAL, f"No major events - {season.value.title()} season"
        
        # Get the most impactful event
        most_impactful = max(active_events, key=lambda e: abs(e.impact.value - 1.0))
        
        return most_impactful.impact, f"Active: {most_impactful.name}"
    
    def is_holiday_period(self, target_date: Optional[date] = None) -> bool:
        """Check if date is during a major holiday shopping period."""
        active = self.get_active_events(target_date)
        holiday_events = [
            "Black Friday", "Cyber Monday", "Christmas Shopping Season",
            "Valentine's Day", "Mother's Day"
        ]
        return any(e.name in holiday_events for e in active)
    
    def is_earnings_season(self, target_date: Optional[date] = None) -> bool:
        """Check if date is during earnings season."""
        active = self.get_active_events(target_date)
        return any("Earnings Season" in e.name for e in active)
    
    def get_seasonal_context(self, target_date: Optional[date] = None) -> dict:
        """
        Get complete seasonal context for a date.
        
        Returns a dictionary with all seasonal information useful for trading.
        """
        check_date = target_date or self.current_date
        active_events = self.get_active_events(check_date)
        upcoming_events = self.get_upcoming_events(14, check_date)
        adjustment, event_names = self.get_seasonal_adjustment(None, check_date)
        impact, impact_desc = self.get_market_impact(check_date)
        
        return {
            "date": check_date.isoformat(),
            "season": self.get_current_season().value,
            "is_holiday_period": self.is_holiday_period(check_date),
            "is_earnings_season": self.is_earnings_season(check_date),
            "active_events": [
                {
                    "name": e.name,
                    "impact": e.impact.name,
                    "adjustment": e.trading_adjustment,
                    "sectors": e.sectors_affected,
                    "description": e.description,
                }
                for e in active_events
            ],
            "upcoming_events": [
                {
                    "name": e.name,
                    "starts": e.start_date.isoformat(),
                    "impact": e.impact.name,
                }
                for e in upcoming_events
            ],
            "overall_adjustment": adjustment,
            "market_impact": impact.name,
            "market_impact_description": impact_desc,
        }


# Global instance for easy access
_calendar_instance: Optional[SeasonalEventsCalendar] = None


def get_seasonal_calendar() -> SeasonalEventsCalendar:
    """Get or create the global seasonal calendar instance."""
    global _calendar_instance
    if _calendar_instance is None:
        _calendar_instance = SeasonalEventsCalendar()
    else:
        # Refresh date on access
        _calendar_instance.refresh_date()
    return _calendar_instance


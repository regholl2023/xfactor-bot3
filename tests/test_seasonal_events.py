"""
Tests for Seasonal Events Calendar.

Tests holiday detection, market patterns, and trading adjustments.
"""

import pytest
import sys
from datetime import date, datetime, timedelta

# Import directly to avoid pandas_ta import issues in tests
sys.path.insert(0, '/Users/cvanthin/code/trading/000_trading')

# Import seasonal_events directly without going through strategies __init__
from src.strategies.seasonal_events import (
    SeasonalEventsCalendar,
    SeasonalEvent,
    Season,
    MarketImpact,
    get_seasonal_calendar,
)


class TestSeasonalEventsCalendar:
    """Tests for SeasonalEventsCalendar class."""
    
    def test_calendar_initialization(self):
        """Test calendar initializes correctly."""
        calendar = SeasonalEventsCalendar()
        assert calendar.current_date == date.today()
    
    def test_calendar_with_custom_date(self):
        """Test calendar with custom reference date."""
        custom_date = datetime(2024, 12, 25)
        calendar = SeasonalEventsCalendar(reference_date=custom_date)
        assert calendar.current_date == custom_date.date()
    
    def test_get_current_season_winter(self):
        """Test winter season detection."""
        calendar = SeasonalEventsCalendar(datetime(2024, 12, 25))
        assert calendar.get_current_season() == Season.WINTER
        
        calendar = SeasonalEventsCalendar(datetime(2024, 1, 15))
        assert calendar.get_current_season() == Season.WINTER
        
        calendar = SeasonalEventsCalendar(datetime(2024, 2, 28))
        assert calendar.get_current_season() == Season.WINTER
    
    def test_get_current_season_spring(self):
        """Test spring season detection."""
        calendar = SeasonalEventsCalendar(datetime(2024, 3, 15))
        assert calendar.get_current_season() == Season.SPRING
        
        calendar = SeasonalEventsCalendar(datetime(2024, 5, 1))
        assert calendar.get_current_season() == Season.SPRING
    
    def test_get_current_season_summer(self):
        """Test summer season detection."""
        calendar = SeasonalEventsCalendar(datetime(2024, 6, 21))
        assert calendar.get_current_season() == Season.SUMMER
        
        calendar = SeasonalEventsCalendar(datetime(2024, 8, 15))
        assert calendar.get_current_season() == Season.SUMMER
    
    def test_get_current_season_fall(self):
        """Test fall season detection."""
        calendar = SeasonalEventsCalendar(datetime(2024, 9, 22))
        assert calendar.get_current_season() == Season.FALL
        
        calendar = SeasonalEventsCalendar(datetime(2024, 11, 15))
        assert calendar.get_current_season() == Season.FALL
    
    def test_get_events_for_year(self):
        """Test getting all events for a year."""
        calendar = SeasonalEventsCalendar()
        events = calendar.get_events_for_year(2024)
        
        assert len(events) > 10  # Should have many events
        
        # Check for key events
        event_names = [e.name for e in events]
        assert "Black Friday" in event_names
        assert "Christmas Shopping Season" in event_names
        assert "Santa Claus Rally" in event_names
        assert "Summer Doldrums" in event_names
        assert "September Effect" in event_names
    
    def test_black_friday_detection(self):
        """Test Black Friday event detection."""
        # Black Friday 2024 is November 29
        calendar = SeasonalEventsCalendar(datetime(2024, 11, 29))
        active = calendar.get_active_events()
        
        black_friday = next((e for e in active if e.name == "Black Friday"), None)
        assert black_friday is not None
        assert black_friday.impact == MarketImpact.VERY_BULLISH
        assert "retail" in black_friday.sectors_affected
    
    def test_christmas_shopping_season(self):
        """Test Christmas shopping season detection."""
        calendar = SeasonalEventsCalendar(datetime(2024, 12, 15))
        active = calendar.get_active_events()
        
        christmas = next((e for e in active if e.name == "Christmas Shopping Season"), None)
        assert christmas is not None
        assert christmas.impact == MarketImpact.BULLISH
    
    def test_summer_doldrums(self):
        """Test summer doldrums detection."""
        calendar = SeasonalEventsCalendar(datetime(2024, 7, 15))
        active = calendar.get_active_events()
        
        doldrums = next((e for e in active if e.name == "Summer Doldrums"), None)
        assert doldrums is not None
        assert doldrums.impact == MarketImpact.SLIGHTLY_BEARISH
        assert doldrums.trading_adjustment < 1.0
    
    def test_september_effect(self):
        """Test September effect detection."""
        calendar = SeasonalEventsCalendar(datetime(2024, 9, 15))
        active = calendar.get_active_events()
        
        sept = next((e for e in active if e.name == "September Effect"), None)
        assert sept is not None
        assert sept.impact == MarketImpact.SLIGHTLY_BEARISH
    
    def test_q4_rally(self):
        """Test Q4 rally detection."""
        calendar = SeasonalEventsCalendar(datetime(2024, 11, 1))
        active = calendar.get_active_events()
        
        q4 = next((e for e in active if e.name == "Q4 Rally Season"), None)
        assert q4 is not None
        assert q4.impact == MarketImpact.BULLISH
    
    def test_earnings_season_detection(self):
        """Test earnings season detection."""
        # Q1 earnings season (April)
        calendar = SeasonalEventsCalendar(datetime(2024, 4, 20))
        assert calendar.is_earnings_season()
        
        # Outside earnings season
        calendar = SeasonalEventsCalendar(datetime(2024, 6, 15))
        assert not calendar.is_earnings_season()
    
    def test_holiday_period_detection(self):
        """Test holiday period detection."""
        # During Christmas shopping
        calendar = SeasonalEventsCalendar(datetime(2024, 12, 20))
        assert calendar.is_holiday_period()
        
        # Regular day
        calendar = SeasonalEventsCalendar(datetime(2024, 6, 15))
        assert not calendar.is_holiday_period()
    
    def test_get_seasonal_adjustment(self):
        """Test seasonal adjustment calculation."""
        # During bullish period (Q4)
        calendar = SeasonalEventsCalendar(datetime(2024, 11, 15))
        adjustment, events = calendar.get_seasonal_adjustment()
        assert adjustment >= 1.0
        assert len(events) > 0
    
    def test_sector_specific_adjustment(self):
        """Test sector-specific adjustments."""
        calendar = SeasonalEventsCalendar(datetime(2024, 12, 15))
        
        # Retail sector during Christmas
        adj_retail, events_retail = calendar.get_seasonal_adjustment("retail")
        assert adj_retail > 1.0
        assert "Christmas Shopping Season" in events_retail
    
    def test_get_upcoming_events(self):
        """Test getting upcoming events."""
        calendar = SeasonalEventsCalendar(datetime(2024, 11, 20))
        upcoming = calendar.get_upcoming_events(days_ahead=14)
        
        assert len(upcoming) > 0
        # Black Friday and Cyber Monday should be upcoming
        names = [e.name for e in upcoming]
        assert any("Friday" in n or "Monday" in n or "Christmas" in n for n in names)
    
    def test_get_market_impact(self):
        """Test market impact calculation."""
        calendar = SeasonalEventsCalendar(datetime(2024, 12, 25))
        impact, description = calendar.get_market_impact()
        
        assert impact in MarketImpact
        assert len(description) > 0
    
    def test_get_seasonal_context(self):
        """Test full seasonal context."""
        calendar = SeasonalEventsCalendar(datetime(2024, 12, 15))
        context = calendar.get_seasonal_context()
        
        assert "date" in context
        assert "season" in context
        assert "is_holiday_period" in context
        assert "is_earnings_season" in context
        assert "active_events" in context
        assert "upcoming_events" in context
        assert "overall_adjustment" in context
        assert "market_impact" in context
        
        assert context["season"] == "winter"
        assert context["is_holiday_period"] is True
    
    def test_refresh_date(self):
        """Test date refresh functionality."""
        calendar = SeasonalEventsCalendar(datetime(2024, 1, 1))
        old_date = calendar.current_date
        
        calendar.refresh_date()
        new_date = calendar.current_date
        
        # Date should have changed to today
        assert new_date == date.today()
    
    def test_global_calendar_singleton(self):
        """Test global calendar singleton."""
        calendar1 = get_seasonal_calendar()
        calendar2 = get_seasonal_calendar()
        
        # Should return same instance
        assert calendar1 is calendar2


class TestSeasonalEvent:
    """Tests for SeasonalEvent dataclass."""
    
    def test_event_creation(self):
        """Test creating a seasonal event."""
        event = SeasonalEvent(
            name="Test Event",
            start_date=date(2024, 12, 1),
            end_date=date(2024, 12, 31),
            impact=MarketImpact.BULLISH,
            sectors_affected=["retail", "technology"],
            description="Test holiday event",
            trading_adjustment=1.15,
        )
        
        assert event.name == "Test Event"
        assert event.impact == MarketImpact.BULLISH
        assert event.trading_adjustment == 1.15
        assert len(event.sectors_affected) == 2


class TestMarketImpact:
    """Tests for MarketImpact enum."""
    
    def test_impact_values(self):
        """Test market impact values."""
        assert MarketImpact.VERY_BULLISH.value == 2.0
        assert MarketImpact.BULLISH.value == 1.5
        assert MarketImpact.SLIGHTLY_BULLISH.value == 1.2
        assert MarketImpact.NEUTRAL.value == 1.0
        assert MarketImpact.SLIGHTLY_BEARISH.value == 0.8
        assert MarketImpact.BEARISH.value == 0.6
        assert MarketImpact.VERY_BEARISH.value == 0.4


class TestSeason:
    """Tests for Season enum."""
    
    def test_season_values(self):
        """Test season enum values."""
        assert Season.SPRING.value == "spring"
        assert Season.SUMMER.value == "summer"
        assert Season.FALL.value == "fall"
        assert Season.WINTER.value == "winter"


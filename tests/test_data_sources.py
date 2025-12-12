"""Tests for Data Source integrations."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timedelta


class TestAInvestDataSource:
    """Tests for AInvest data source."""

    @pytest.fixture
    def ainvest(self):
        """Create AInvest data source instance."""
        from src.data_sources.ainvest import AInvestDataSource
        return AInvestDataSource()

    @pytest.mark.asyncio
    async def test_connect(self, ainvest):
        """Test connecting to AInvest."""
        result = await ainvest.connect()
        assert result is True
        assert ainvest.connected is True

    @pytest.mark.asyncio
    async def test_disconnect(self, ainvest):
        """Test disconnecting from AInvest."""
        await ainvest.connect()
        await ainvest.disconnect()
        assert ainvest.connected is False

    @pytest.mark.asyncio
    async def test_get_recommendations(self, ainvest):
        """Test getting AI recommendations."""
        await ainvest.connect()
        recommendations = await ainvest.get_ai_recommendations(limit=10)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) <= 10

    @pytest.mark.asyncio
    async def test_get_recommendations_filtered(self, ainvest):
        """Test getting filtered recommendations."""
        await ainvest.connect()
        recommendations = await ainvest.get_ai_recommendations(
            symbols=["AAPL", "NVDA"],
            min_score=70,
            limit=5
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) <= 5

    @pytest.mark.asyncio
    async def test_get_sentiment(self, ainvest):
        """Test getting sentiment for a symbol."""
        await ainvest.connect()
        sentiment = await ainvest.get_sentiment("NVDA")
        
        assert sentiment is not None
        assert sentiment.symbol == "NVDA"
        assert -1 <= sentiment.overall_sentiment <= 1

    @pytest.mark.asyncio
    async def test_get_news(self, ainvest):
        """Test getting news from AInvest."""
        await ainvest.connect()
        news = await ainvest.get_news(limit=10)
        
        assert isinstance(news, list)

    @pytest.mark.asyncio
    async def test_get_trading_signals(self, ainvest):
        """Test getting trading signals."""
        await ainvest.connect()
        signals = await ainvest.get_trading_signals(limit=10)
        
        assert isinstance(signals, list)

    @pytest.mark.asyncio
    async def test_get_insider_trades(self, ainvest):
        """Test getting insider trades."""
        await ainvest.connect()
        trades = await ainvest.get_insider_trades(limit=10)
        
        assert isinstance(trades, list)

    @pytest.mark.asyncio
    async def test_get_earnings_calendar(self, ainvest):
        """Test getting earnings calendar."""
        await ainvest.connect()
        earnings = await ainvest.get_earnings_calendar(days_ahead=7)
        
        assert isinstance(earnings, list)


class TestTradingViewWebhook:
    """Tests for TradingView webhook integration."""

    @pytest.fixture
    def tradingview(self):
        """Create TradingView webhook handler."""
        from src.data_sources.tradingview import TradingViewWebhook
        return TradingViewWebhook()

    @pytest.mark.asyncio
    async def test_connect(self, tradingview):
        """Test connect method."""
        result = await tradingview.connect()
        assert result is True

    @pytest.mark.asyncio
    async def test_process_webhook_alert(self, tradingview):
        """Test processing webhook alerts."""
        await tradingview.connect()
        
        # Test with a sample alert
        alert_data = {
            "symbol": "AAPL",
            "action": "buy",
            "price": 175.50,
            "time": datetime.now().isoformat()
        }
        
        signal = await tradingview.process_alert(alert_data)
        
        if signal:
            assert signal.symbol == "AAPL"


class TestDataSourceRegistry:
    """Tests for DataSourceRegistry."""

    def test_registry_initialization(self):
        """Test registry initializes properly."""
        from src.data_sources.registry import DataSourceRegistry
        
        registry = DataSourceRegistry()
        assert registry is not None

    def test_list_data_sources(self):
        """Test listing connected data sources."""
        from src.data_sources.registry import DataSourceRegistry
        
        registry = DataSourceRegistry()
        sources = registry.connected_sources
        assert isinstance(sources, list)

    def test_register_source_class(self):
        """Test registering a data source class."""
        from src.data_sources.registry import DataSourceRegistry
        
        registry = DataSourceRegistry()
        assert hasattr(registry, 'register_source_class')


class TestNewsArticle:
    """Tests for NewsArticle dataclass."""

    def test_news_article_creation(self):
        """Test creating a news article."""
        from src.data_sources.base import NewsArticle
        
        article = NewsArticle(
            title="Test Article",
            summary="This is a test",
            source="Reuters",
            url="https://example.com/article",
            published=datetime.now(),
            symbols=["AAPL", "MSFT"],
            sentiment=0.5
        )
        
        assert article.title == "Test Article"
        assert article.sentiment == 0.5
        assert "AAPL" in article.symbols


class TestTradingSignal:
    """Tests for TradingSignal dataclass."""

    def test_trading_signal_creation(self):
        """Test creating a trading signal."""
        from src.data_sources.base import TradingSignal
        
        signal = TradingSignal(
            symbol="NVDA",
            signal_type="buy",
            strength=0.8,
            source="technical",
            price=500.0,
            target_price=550.0,
            stop_loss=480.0
        )
        
        assert signal.symbol == "NVDA"
        assert signal.signal_type == "buy"
        assert signal.strength == 0.8


class TestInsiderTrade:
    """Tests for InsiderTrade dataclass."""

    def test_insider_trade_creation(self):
        """Test creating an insider trade record."""
        from src.data_sources.base import InsiderTrade
        
        trade = InsiderTrade(
            symbol="AAPL",
            insider_name="Tim Cook",
            title="CEO",
            transaction_type="sell",
            shares=50000,
            price=175.00,
            value=8750000,
            shares_owned_after=500000,
            filing_date=datetime.now(),
            transaction_date=datetime.now()
        )
        
        assert trade.symbol == "AAPL"
        assert trade.insider_name == "Tim Cook"
        assert trade.transaction_type == "sell"

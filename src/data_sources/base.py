"""
Base data source interface for multi-source market data.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any


class DataSourceType(str, Enum):
    """Supported data source types."""
    POLYGON = "polygon"
    ALPHA_VANTAGE = "alpha_vantage"
    IEX_CLOUD = "iex_cloud"
    TIINGO = "tiingo"
    BARCHART = "barchart"
    FINNHUB = "finnhub"
    YAHOO_FINANCE = "yahoo_finance"
    TRADINGVIEW = "tradingview"
    QUANDL = "quandl"
    FRED = "fred"  # Federal Reserve Economic Data


@dataclass
class Quote:
    """Real-time quote data."""
    symbol: str
    bid: float
    ask: float
    bid_size: int = 0
    ask_size: int = 0
    last: float = 0
    last_size: int = 0
    volume: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    source: DataSourceType = DataSourceType.POLYGON
    
    @property
    def mid(self) -> float:
        """Get mid price."""
        return (self.bid + self.ask) / 2
    
    @property
    def spread(self) -> float:
        """Get bid-ask spread."""
        return self.ask - self.bid
    
    @property
    def spread_pct(self) -> float:
        """Get spread as percentage."""
        if self.mid == 0:
            return 0
        return (self.spread / self.mid) * 100


@dataclass
class Bar:
    """OHLCV bar data."""
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    vwap: Optional[float] = None
    trades: Optional[int] = None
    source: DataSourceType = DataSourceType.POLYGON
    
    @property
    def range(self) -> float:
        """Get high-low range."""
        return self.high - self.low
    
    @property
    def body(self) -> float:
        """Get candle body size."""
        return abs(self.close - self.open)
    
    @property
    def is_bullish(self) -> bool:
        """Check if bullish candle."""
        return self.close > self.open


class BaseDataSource(ABC):
    """
    Abstract base class for market data sources.
    """
    
    def __init__(self, source_type: DataSourceType):
        self.source_type = source_type
        self._connected = False
    
    @property
    def is_connected(self) -> bool:
        return self._connected
    
    @property
    def name(self) -> str:
        return self.source_type.value
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to data source."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from data source."""
        pass
    
    @abstractmethod
    async def get_quote(self, symbol: str) -> Optional[Quote]:
        """Get real-time quote for a symbol."""
        pass
    
    @abstractmethod
    async def get_bars(
        self,
        symbol: str,
        timeframe: str = "1d",
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Bar]:
        """Get historical bars for a symbol."""
        pass
    
    async def get_quotes(self, symbols: List[str]) -> Dict[str, Quote]:
        """Get quotes for multiple symbols."""
        quotes = {}
        for symbol in symbols:
            quote = await self.get_quote(symbol)
            if quote:
                quotes[symbol] = quote
        return quotes
    
    async def search_symbols(self, query: str) -> List[Dict[str, Any]]:
        """Search for symbols. Override if supported."""
        return []
    
    async def get_company_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get company information. Override if supported."""
        return None


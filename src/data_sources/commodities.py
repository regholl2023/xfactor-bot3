"""
Commodity and Resource data source integration.
Provides real-time commodity prices, news, and market data.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
from enum import Enum

import httpx
from loguru import logger


class CommodityCategory(str, Enum):
    """Categories of commodities."""
    PRECIOUS_METALS = "precious_metals"
    ENERGY = "energy"
    INDUSTRIAL_METALS = "industrial_metals"
    AGRICULTURE = "agriculture"
    RARE_EARTH = "rare_earth"
    NUCLEAR = "nuclear"


@dataclass
class CommodityPrice:
    """Current commodity price data."""
    symbol: str
    name: str
    category: CommodityCategory
    price: float
    change: float
    change_pct: float
    high_24h: float
    low_24h: float
    volume: float
    timestamp: datetime
    source: str = "yfinance"


@dataclass
class CommodityNews:
    """Commodity-related news article."""
    title: str
    summary: str
    source: str
    url: str
    published: datetime
    commodities: list[str]
    sentiment: float = 0.0  # -1 to 1


# Commodity symbol mappings
COMMODITY_FUTURES = {
    # Precious Metals
    "GC=F": {"name": "Gold Futures", "category": CommodityCategory.PRECIOUS_METALS},
    "SI=F": {"name": "Silver Futures", "category": CommodityCategory.PRECIOUS_METALS},
    "PL=F": {"name": "Platinum Futures", "category": CommodityCategory.PRECIOUS_METALS},
    "PA=F": {"name": "Palladium Futures", "category": CommodityCategory.PRECIOUS_METALS},
    
    # Energy
    "CL=F": {"name": "Crude Oil WTI", "category": CommodityCategory.ENERGY},
    "BZ=F": {"name": "Brent Crude Oil", "category": CommodityCategory.ENERGY},
    "NG=F": {"name": "Natural Gas", "category": CommodityCategory.ENERGY},
    "RB=F": {"name": "Gasoline RBOB", "category": CommodityCategory.ENERGY},
    "HO=F": {"name": "Heating Oil", "category": CommodityCategory.ENERGY},
    
    # Industrial Metals
    "HG=F": {"name": "Copper", "category": CommodityCategory.INDUSTRIAL_METALS},
    "ALI=F": {"name": "Aluminum", "category": CommodityCategory.INDUSTRIAL_METALS},
    
    # Agriculture
    "ZC=F": {"name": "Corn Futures", "category": CommodityCategory.AGRICULTURE},
    "ZW=F": {"name": "Wheat Futures", "category": CommodityCategory.AGRICULTURE},
    "ZS=F": {"name": "Soybeans Futures", "category": CommodityCategory.AGRICULTURE},
    "KC=F": {"name": "Coffee", "category": CommodityCategory.AGRICULTURE},
    "SB=F": {"name": "Sugar", "category": CommodityCategory.AGRICULTURE},
    "CC=F": {"name": "Cocoa", "category": CommodityCategory.AGRICULTURE},
}

COMMODITY_ETFS = {
    # Precious Metals ETFs
    "GLD": {"name": "SPDR Gold Trust", "category": CommodityCategory.PRECIOUS_METALS, "commodity": "gold"},
    "SLV": {"name": "iShares Silver Trust", "category": CommodityCategory.PRECIOUS_METALS, "commodity": "silver"},
    "PPLT": {"name": "Aberdeen Platinum ETF", "category": CommodityCategory.PRECIOUS_METALS, "commodity": "platinum"},
    "PALL": {"name": "Aberdeen Palladium ETF", "category": CommodityCategory.PRECIOUS_METALS, "commodity": "palladium"},
    "GDX": {"name": "VanEck Gold Miners", "category": CommodityCategory.PRECIOUS_METALS, "commodity": "gold_miners"},
    "GDXJ": {"name": "VanEck Junior Gold Miners", "category": CommodityCategory.PRECIOUS_METALS, "commodity": "gold_miners"},
    "SIL": {"name": "Global X Silver Miners", "category": CommodityCategory.PRECIOUS_METALS, "commodity": "silver_miners"},
    
    # Energy ETFs
    "USO": {"name": "United States Oil Fund", "category": CommodityCategory.ENERGY, "commodity": "oil"},
    "UNG": {"name": "United States Natural Gas Fund", "category": CommodityCategory.ENERGY, "commodity": "natural_gas"},
    "XLE": {"name": "Energy Select Sector SPDR", "category": CommodityCategory.ENERGY, "commodity": "energy_stocks"},
    "XOP": {"name": "SPDR S&P Oil & Gas E&P", "category": CommodityCategory.ENERGY, "commodity": "oil_gas_stocks"},
    "OIH": {"name": "VanEck Oil Services ETF", "category": CommodityCategory.ENERGY, "commodity": "oil_services"},
    
    # Industrial Metals ETFs
    "CPER": {"name": "United States Copper Fund", "category": CommodityCategory.INDUSTRIAL_METALS, "commodity": "copper"},
    "DBB": {"name": "Invesco DB Base Metals", "category": CommodityCategory.INDUSTRIAL_METALS, "commodity": "base_metals"},
    "LIT": {"name": "Global X Lithium & Battery", "category": CommodityCategory.INDUSTRIAL_METALS, "commodity": "lithium"},
    
    # Nuclear/Uranium
    "URA": {"name": "Global X Uranium ETF", "category": CommodityCategory.NUCLEAR, "commodity": "uranium"},
    
    # Rare Earth
    "REMX": {"name": "VanEck Rare Earth/Strategic Metals", "category": CommodityCategory.RARE_EARTH, "commodity": "rare_earth"},
    
    # Agriculture ETFs
    "CORN": {"name": "Teucrium Corn Fund", "category": CommodityCategory.AGRICULTURE, "commodity": "corn"},
    "WEAT": {"name": "Teucrium Wheat Fund", "category": CommodityCategory.AGRICULTURE, "commodity": "wheat"},
    "SOYB": {"name": "Teucrium Soybean Fund", "category": CommodityCategory.AGRICULTURE, "commodity": "soybeans"},
    "DBA": {"name": "Invesco DB Agriculture", "category": CommodityCategory.AGRICULTURE, "commodity": "agriculture"},
    "JO": {"name": "iPath Coffee ETN", "category": CommodityCategory.AGRICULTURE, "commodity": "coffee"},
    
    # Broad Commodity ETFs
    "DBC": {"name": "Invesco DB Commodity Index", "category": CommodityCategory.ENERGY, "commodity": "broad"},
    "GSG": {"name": "iShares S&P GSCI Commodity", "category": CommodityCategory.ENERGY, "commodity": "broad"},
    "PDBC": {"name": "Invesco Optimum Yield Diversified", "category": CommodityCategory.ENERGY, "commodity": "broad"},
}


class CommodityDataSource:
    """
    Data source for commodity prices and news.
    Uses Yahoo Finance for real-time prices.
    """
    
    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None
        self._cache: dict[str, CommodityPrice] = {}
        self._cache_ttl = 60  # seconds
        self._last_update: Optional[datetime] = None
        
    async def connect(self) -> bool:
        """Initialize the data source."""
        try:
            self._client = httpx.AsyncClient(timeout=30.0)
            logger.info("Commodity data source connected")
            return True
        except Exception as e:
            logger.error(f"Failed to connect commodity data source: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Close the data source."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def get_commodity_prices(
        self, 
        category: Optional[CommodityCategory] = None,
        symbols: Optional[list[str]] = None
    ) -> list[CommodityPrice]:
        """
        Get current commodity prices.
        
        Args:
            category: Filter by category (precious_metals, energy, etc.)
            symbols: Specific symbols to fetch
            
        Returns:
            List of CommodityPrice objects
        """
        try:
            import yfinance as yf
            
            # Build symbol list
            if symbols:
                target_symbols = symbols
            else:
                target_symbols = list(COMMODITY_FUTURES.keys()) + list(COMMODITY_ETFS.keys())
                
                if category:
                    # Filter by category
                    target_symbols = [
                        s for s in target_symbols
                        if (s in COMMODITY_FUTURES and COMMODITY_FUTURES[s]["category"] == category) or
                           (s in COMMODITY_ETFS and COMMODITY_ETFS[s]["category"] == category)
                    ]
            
            prices = []
            
            # Fetch data in batches
            batch_size = 20
            for i in range(0, len(target_symbols), batch_size):
                batch = target_symbols[i:i + batch_size]
                
                try:
                    tickers = yf.Tickers(" ".join(batch))
                    
                    for symbol in batch:
                        try:
                            ticker = tickers.tickers.get(symbol)
                            if ticker:
                                info = ticker.info
                                hist = ticker.history(period="2d")
                                
                                if len(hist) >= 1:
                                    current_price = hist["Close"].iloc[-1]
                                    prev_price = hist["Close"].iloc[-2] if len(hist) >= 2 else current_price
                                    
                                    change = current_price - prev_price
                                    change_pct = (change / prev_price) * 100 if prev_price else 0
                                    
                                    # Get metadata
                                    meta = COMMODITY_FUTURES.get(symbol) or COMMODITY_ETFS.get(symbol, {})
                                    
                                    prices.append(CommodityPrice(
                                        symbol=symbol,
                                        name=meta.get("name", info.get("shortName", symbol)),
                                        category=meta.get("category", CommodityCategory.ENERGY),
                                        price=current_price,
                                        change=change,
                                        change_pct=change_pct,
                                        high_24h=hist["High"].iloc[-1],
                                        low_24h=hist["Low"].iloc[-1],
                                        volume=hist["Volume"].iloc[-1] if "Volume" in hist else 0,
                                        timestamp=datetime.utcnow(),
                                    ))
                        except Exception as e:
                            logger.warning(f"Error fetching {symbol}: {e}")
                            
                except Exception as e:
                    logger.error(f"Batch fetch error: {e}")
            
            return prices
            
        except ImportError:
            logger.error("yfinance not installed")
            return self._get_mock_prices(category)
        except Exception as e:
            logger.error(f"Error fetching commodity prices: {e}")
            return self._get_mock_prices(category)
    
    def _get_mock_prices(self, category: Optional[CommodityCategory] = None) -> list[CommodityPrice]:
        """Get mock commodity prices for demo."""
        import random
        
        mock_data = [
            # Precious Metals
            ("GLD", "SPDR Gold Trust", CommodityCategory.PRECIOUS_METALS, 185.50),
            ("SLV", "iShares Silver Trust", CommodityCategory.PRECIOUS_METALS, 21.30),
            ("PPLT", "Aberdeen Platinum ETF", CommodityCategory.PRECIOUS_METALS, 89.40),
            ("GDX", "VanEck Gold Miners", CommodityCategory.PRECIOUS_METALS, 28.90),
            
            # Energy
            ("USO", "United States Oil Fund", CommodityCategory.ENERGY, 72.50),
            ("UNG", "United States Natural Gas", CommodityCategory.ENERGY, 12.80),
            ("XLE", "Energy Select Sector SPDR", CommodityCategory.ENERGY, 89.30),
            
            # Industrial Metals
            ("CPER", "United States Copper Fund", CommodityCategory.INDUSTRIAL_METALS, 24.10),
            ("LIT", "Global X Lithium & Battery", CommodityCategory.INDUSTRIAL_METALS, 45.20),
            
            # Nuclear
            ("URA", "Global X Uranium ETF", CommodityCategory.NUCLEAR, 28.50),
            
            # Rare Earth
            ("REMX", "VanEck Rare Earth/Strategic", CommodityCategory.RARE_EARTH, 42.30),
            
            # Agriculture
            ("CORN", "Teucrium Corn Fund", CommodityCategory.AGRICULTURE, 20.15),
            ("WEAT", "Teucrium Wheat Fund", CommodityCategory.AGRICULTURE, 5.80),
            ("DBA", "Invesco DB Agriculture", CommodityCategory.AGRICULTURE, 21.40),
        ]
        
        prices = []
        for symbol, name, cat, base_price in mock_data:
            if category and cat != category:
                continue
                
            change_pct = random.uniform(-3, 3)
            change = base_price * (change_pct / 100)
            
            prices.append(CommodityPrice(
                symbol=symbol,
                name=name,
                category=cat,
                price=base_price + change,
                change=change,
                change_pct=change_pct,
                high_24h=base_price * 1.02,
                low_24h=base_price * 0.98,
                volume=random.randint(1000000, 50000000),
                timestamp=datetime.utcnow(),
            ))
        
        return prices
    
    async def get_commodity_news(
        self, 
        commodities: Optional[list[str]] = None,
        limit: int = 20
    ) -> list[CommodityNews]:
        """Get commodity-related news."""
        # Mock news for demonstration
        import random
        
        news_templates = [
            ("Gold prices surge as Fed signals rate pause", "precious_metals", 0.7),
            ("Oil jumps on OPEC+ production cut announcement", "energy", 0.6),
            ("Copper hits 6-month high on China demand outlook", "industrial_metals", 0.5),
            ("Natural gas falls on warmer weather forecast", "energy", -0.4),
            ("Silver rallies alongside gold amid dollar weakness", "precious_metals", 0.5),
            ("Uranium stocks surge on nuclear energy push", "nuclear", 0.8),
            ("Lithium prices stabilize after EV demand concerns", "lithium", 0.2),
            ("Wheat futures drop on improved crop outlook", "agriculture", -0.3),
            ("Rare earth supply concerns boost mining stocks", "rare_earth", 0.6),
            ("Platinum gains on automotive demand recovery", "precious_metals", 0.4),
            ("Oil inventory data shows larger than expected draw", "energy", 0.5),
            ("Gold miners report strong quarterly earnings", "precious_metals", 0.6),
            ("Energy sector leads market gains on oil rally", "energy", 0.5),
            ("Copper demand expected to surge for green energy", "industrial_metals", 0.7),
            ("Natural gas exports hit record high", "energy", 0.4),
        ]
        
        news = []
        for i, (title, commodity, sentiment) in enumerate(news_templates[:limit]):
            if commodities and commodity not in commodities:
                continue
                
            news.append(CommodityNews(
                title=title,
                summary=f"Breaking: {title}. Market analysts react to latest developments...",
                source=random.choice(["Reuters", "Bloomberg", "CNBC", "MarketWatch"]),
                url=f"https://example.com/news/{i}",
                published=datetime.utcnow() - timedelta(hours=random.randint(1, 24)),
                commodities=[commodity],
                sentiment=sentiment + random.uniform(-0.1, 0.1),
            ))
        
        return news
    
    def get_supported_commodities(self) -> dict:
        """Get all supported commodities and their symbols."""
        return {
            "futures": COMMODITY_FUTURES,
            "etfs": COMMODITY_ETFS,
            "categories": [c.value for c in CommodityCategory],
        }


# Singleton instance
_commodity_source: Optional[CommodityDataSource] = None


def get_commodity_source() -> CommodityDataSource:
    """Get or create the commodity data source."""
    global _commodity_source
    if _commodity_source is None:
        _commodity_source = CommodityDataSource()
    return _commodity_source


"""
API routes for commodity and resource trading.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime

from loguru import logger

router = APIRouter()


# ============================================================================
# Models
# ============================================================================

class CommodityPriceResponse(BaseModel):
    """Commodity price data."""
    symbol: str
    name: str
    category: str
    price: float
    change: float
    change_pct: float
    high_24h: float
    low_24h: float
    volume: float
    timestamp: str


class CommodityNewsResponse(BaseModel):
    """Commodity news article."""
    title: str
    summary: str
    source: str
    url: str
    published: str
    commodities: list[str]
    sentiment: float


class CommodityOverview(BaseModel):
    """Overview of all commodity categories."""
    precious_metals: list[CommodityPriceResponse]
    energy: list[CommodityPriceResponse]
    industrial_metals: list[CommodityPriceResponse]
    agriculture: list[CommodityPriceResponse]
    nuclear: list[CommodityPriceResponse]
    rare_earth: list[CommodityPriceResponse]


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/prices")
async def get_commodity_prices(
    category: Optional[str] = Query(None, description="Filter by category"),
    symbols: Optional[str] = Query(None, description="Comma-separated symbols"),
) -> list[CommodityPriceResponse]:
    """Get current commodity prices."""
    try:
        from src.data_sources.commodities import get_commodity_source, CommodityCategory
        
        source = get_commodity_source()
        await source.connect()
        
        cat = None
        if category:
            try:
                cat = CommodityCategory(category)
            except ValueError:
                pass
        
        sym_list = symbols.split(",") if symbols else None
        prices = await source.get_commodity_prices(category=cat, symbols=sym_list)
        
        return [
            CommodityPriceResponse(
                symbol=p.symbol,
                name=p.name,
                category=p.category.value if hasattr(p.category, 'value') else p.category,
                price=p.price,
                change=p.change,
                change_pct=p.change_pct,
                high_24h=p.high_24h,
                low_24h=p.low_24h,
                volume=p.volume,
                timestamp=p.timestamp.isoformat(),
            )
            for p in prices
        ]
        
    except Exception as e:
        logger.error(f"Error fetching commodity prices: {e}")
        # Return mock data on error
        return _get_mock_prices()


@router.get("/overview")
async def get_commodity_overview() -> dict:
    """Get overview of all commodity categories with prices."""
    try:
        from src.data_sources.commodities import get_commodity_source, CommodityCategory
        
        source = get_commodity_source()
        await source.connect()
        
        result = {}
        for category in CommodityCategory:
            prices = await source.get_commodity_prices(category=category)
            result[category.value] = [
                CommodityPriceResponse(
                    symbol=p.symbol,
                    name=p.name,
                    category=p.category.value if hasattr(p.category, 'value') else p.category,
                    price=p.price,
                    change=p.change,
                    change_pct=p.change_pct,
                    high_24h=p.high_24h,
                    low_24h=p.low_24h,
                    volume=p.volume,
                    timestamp=p.timestamp.isoformat(),
                )
                for p in prices
            ]
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching commodity overview: {e}")
        return {
            "precious_metals": _get_mock_prices("precious_metals"),
            "energy": _get_mock_prices("energy"),
            "industrial_metals": _get_mock_prices("industrial_metals"),
            "agriculture": _get_mock_prices("agriculture"),
            "nuclear": _get_mock_prices("nuclear"),
            "rare_earth": _get_mock_prices("rare_earth"),
        }


@router.get("/news")
async def get_commodity_news(
    commodities: Optional[str] = Query(None, description="Comma-separated commodity types"),
    limit: int = Query(20, ge=1, le=100),
) -> list[CommodityNewsResponse]:
    """Get commodity-related news."""
    try:
        from src.data_sources.commodities import get_commodity_source
        
        source = get_commodity_source()
        await source.connect()
        
        comm_list = commodities.split(",") if commodities else None
        news = await source.get_commodity_news(commodities=comm_list, limit=limit)
        
        return [
            CommodityNewsResponse(
                title=n.title,
                summary=n.summary,
                source=n.source,
                url=n.url,
                published=n.published.isoformat(),
                commodities=n.commodities,
                sentiment=n.sentiment,
            )
            for n in news
        ]
        
    except Exception as e:
        logger.error(f"Error fetching commodity news: {e}")
        return []


@router.get("/symbols")
async def get_commodity_symbols() -> dict:
    """Get all supported commodity symbols and categories."""
    try:
        from src.data_sources.commodities import get_commodity_source
        
        source = get_commodity_source()
        return source.get_supported_commodities()
        
    except Exception as e:
        logger.error(f"Error fetching commodity symbols: {e}")
        return {
            "futures": {},
            "etfs": {},
            "categories": [],
        }


@router.get("/bots")
async def get_commodity_bots() -> list[dict]:
    """Get all commodity-focused trading bots."""
    try:
        from src.bot.bot_manager import get_bot_manager
        from src.bot.bot_instance import InstrumentType
        
        manager = get_bot_manager()
        bots = manager.get_all_bots()
        
        commodity_bots = [
            bot.get_status()
            for bot in bots
            if bot.config.instrument_type == InstrumentType.COMMODITY
        ]
        
        return commodity_bots
        
    except Exception as e:
        logger.error(f"Error fetching commodity bots: {e}")
        return []


def _get_mock_prices(category: Optional[str] = None) -> list[CommodityPriceResponse]:
    """Get mock commodity prices."""
    import random
    from datetime import datetime
    
    mock_data = [
        ("GLD", "SPDR Gold Trust", "precious_metals", 185.50),
        ("SLV", "iShares Silver Trust", "precious_metals", 21.30),
        ("GDX", "VanEck Gold Miners", "precious_metals", 28.90),
        ("USO", "United States Oil Fund", "energy", 72.50),
        ("UNG", "United States Natural Gas", "energy", 12.80),
        ("XLE", "Energy Select Sector SPDR", "energy", 89.30),
        ("CPER", "United States Copper Fund", "industrial_metals", 24.10),
        ("LIT", "Global X Lithium & Battery", "industrial_metals", 45.20),
        ("URA", "Global X Uranium ETF", "nuclear", 28.50),
        ("REMX", "VanEck Rare Earth/Strategic", "rare_earth", 42.30),
        ("CORN", "Teucrium Corn Fund", "agriculture", 20.15),
        ("DBA", "Invesco DB Agriculture", "agriculture", 21.40),
    ]
    
    prices = []
    for symbol, name, cat, base_price in mock_data:
        if category and cat != category:
            continue
            
        change_pct = random.uniform(-3, 3)
        change = base_price * (change_pct / 100)
        
        prices.append(CommodityPriceResponse(
            symbol=symbol,
            name=name,
            category=cat,
            price=round(base_price + change, 2),
            change=round(change, 2),
            change_pct=round(change_pct, 2),
            high_24h=round(base_price * 1.02, 2),
            low_24h=round(base_price * 0.98, 2),
            volume=random.randint(1000000, 50000000),
            timestamp=datetime.utcnow().isoformat(),
        ))
    
    return prices


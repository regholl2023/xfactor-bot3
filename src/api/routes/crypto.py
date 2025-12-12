"""API routes for cryptocurrency data and trading."""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Query
from pydantic import BaseModel

from src.data_sources.crypto import get_crypto_source, CryptoCategory
from src.bot.bot_manager import get_bot_manager
from src.bot.bot_instance import InstrumentType, CRYPTO_SYMBOLS

router = APIRouter()


@router.get("/prices")
async def get_crypto_prices(
    category: Optional[str] = Query(None),
    symbols: Optional[str] = Query(None)
):
    """Get current cryptocurrency prices."""
    source = get_crypto_source()
    if not source.connected:
        await source.connect()
    
    cat = CryptoCategory(category) if category else None
    sym_list = symbols.upper().split(",") if symbols else None
    prices = await source.get_prices(symbols=sym_list, category=cat)
    
    return {
        "prices": [{
            "symbol": p.symbol, "name": p.name, "category": p.category.value,
            "price": p.price, "change_24h_pct": p.change_24h_pct,
            "volume_24h": p.volume_24h, "market_cap": p.market_cap,
        } for p in prices],
        "count": len(prices),
    }


@router.get("/fear-greed")
async def get_fear_greed_index():
    """Get the Crypto Fear & Greed Index."""
    source = get_crypto_source()
    if not source.connected:
        await source.connect()
    fg = await source.get_fear_greed_index()
    return {"value": fg.value, "classification": fg.classification, "timestamp": fg.timestamp.isoformat()}


@router.get("/news")
async def get_crypto_news(limit: int = Query(20, ge=1, le=100)):
    """Get crypto-related news."""
    source = get_crypto_source()
    if not source.connected:
        await source.connect()
    news = await source.get_crypto_news(limit=limit)
    return {"news": [{"title": n.title, "source": n.source, "coins": n.coins, "sentiment": n.sentiment} for n in news]}


@router.get("/whale-alerts")
async def get_whale_alerts(limit: int = Query(10, ge=1, le=50)):
    """Get recent whale transaction alerts."""
    source = get_crypto_source()
    if not source.connected:
        await source.connect()
    alerts = await source.get_whale_alerts(limit=limit)
    return {"alerts": [{"symbol": a.symbol, "amount": a.amount, "usd_value": a.usd_value, "type": a.transaction_type} for a in alerts]}


@router.get("/symbols")
async def get_crypto_symbols():
    """Get all supported cryptocurrency symbols."""
    source = get_crypto_source()
    data = source.get_supported_cryptos()
    return {
        "symbols": [{"symbol": s, "name": i["name"], "category": i["category"].value} for s, i in data["coins"].items()],
        "categories": data["categories"],
    }


@router.get("/bots")
async def get_crypto_bots():
    """Get all cryptocurrency trading bots."""
    manager = get_bot_manager()
    crypto_bots = [b for b in manager.get_all_bots() if b.config.instrument_type == InstrumentType.CRYPTO]
    return {
        "bots": [{"id": b.id, "name": b.config.name, "status": b.status.value, "symbols": b.config.symbols} for b in crypto_bots],
        "count": len(crypto_bots),
    }


@router.get("/overview")
async def get_crypto_overview():
    """Get crypto market overview."""
    source = get_crypto_source()
    manager = get_bot_manager()
    if not source.connected:
        await source.connect()
    
    prices = await source.get_prices(category=CryptoCategory.MAJOR)
    fg = await source.get_fear_greed_index()
    crypto_bots = [b for b in manager.get_all_bots() if b.config.instrument_type == InstrumentType.CRYPTO]
    
    return {
        "market": {"total_market_cap": sum(p.market_cap for p in prices), "total_volume": sum(p.volume_24h for p in prices)},
        "fear_greed": {"value": fg.value, "classification": fg.classification},
        "top_cryptos": [{"symbol": p.symbol, "price": p.price, "change": p.change_24h_pct} for p in prices[:5]],
        "bots": {"total": len(crypto_bots), "active": sum(1 for b in crypto_bots if b.status.value == "running")},
    }


@router.get("/etfs")
async def get_crypto_etfs():
    """Get crypto ETF data."""
    etfs = CRYPTO_SYMBOLS.get("crypto_etfs", {})
    return {"etfs": [{"symbol": s, "name": n} for s, n in etfs.items()], "count": len(etfs)}


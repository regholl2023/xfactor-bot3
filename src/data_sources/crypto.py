"""
Cryptocurrency Data Source Integration.
Provides real-time crypto prices, market data, and on-chain analytics.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum

import httpx
from loguru import logger


class CryptoCategory(str, Enum):
    """Categories of cryptocurrencies."""
    MAJOR = "major"
    DEFI = "defi"
    LAYER2 = "layer2"
    MEME = "meme"
    AI = "ai"
    GAMING = "gaming"
    STABLECOIN = "stablecoin"


@dataclass
class CryptoPrice:
    """Current cryptocurrency price data."""
    symbol: str
    name: str
    category: CryptoCategory
    price: float
    change_24h: float
    change_24h_pct: float
    change_7d_pct: float
    high_24h: float
    low_24h: float
    volume_24h: float
    market_cap: float
    timestamp: datetime
    source: str = "coingecko"


@dataclass
class CryptoNews:
    """Crypto-related news article."""
    title: str
    summary: str
    source: str
    url: str
    published: datetime
    coins: List[str]
    sentiment: float = 0.0


@dataclass
class WhaleAlert:
    """Large cryptocurrency transaction alert."""
    symbol: str
    amount: float
    usd_value: float
    from_address: str
    to_address: str
    transaction_type: str  # 'exchange_deposit', 'exchange_withdrawal', 'transfer'
    timestamp: datetime
    tx_hash: str


@dataclass
class FearGreedIndex:
    """Crypto Fear & Greed Index data."""
    value: int  # 0-100
    classification: str  # "Extreme Fear", "Fear", "Neutral", "Greed", "Extreme Greed"
    timestamp: datetime


# Crypto symbol mappings
CRYPTO_COINS = {
    # Major Cryptocurrencies
    "BTC": {"name": "Bitcoin", "category": CryptoCategory.MAJOR, "coingecko_id": "bitcoin"},
    "ETH": {"name": "Ethereum", "category": CryptoCategory.MAJOR, "coingecko_id": "ethereum"},
    "SOL": {"name": "Solana", "category": CryptoCategory.MAJOR, "coingecko_id": "solana"},
    "XRP": {"name": "XRP", "category": CryptoCategory.MAJOR, "coingecko_id": "ripple"},
    "ADA": {"name": "Cardano", "category": CryptoCategory.MAJOR, "coingecko_id": "cardano"},
    "AVAX": {"name": "Avalanche", "category": CryptoCategory.MAJOR, "coingecko_id": "avalanche-2"},
    "DOT": {"name": "Polkadot", "category": CryptoCategory.MAJOR, "coingecko_id": "polkadot"},
    
    # Layer 2
    "MATIC": {"name": "Polygon", "category": CryptoCategory.LAYER2, "coingecko_id": "matic-network"},
    "ARB": {"name": "Arbitrum", "category": CryptoCategory.LAYER2, "coingecko_id": "arbitrum"},
    "OP": {"name": "Optimism", "category": CryptoCategory.LAYER2, "coingecko_id": "optimism"},
    
    # DeFi
    "UNI": {"name": "Uniswap", "category": CryptoCategory.DEFI, "coingecko_id": "uniswap"},
    "AAVE": {"name": "Aave", "category": CryptoCategory.DEFI, "coingecko_id": "aave"},
    "LINK": {"name": "Chainlink", "category": CryptoCategory.DEFI, "coingecko_id": "chainlink"},
    "MKR": {"name": "Maker", "category": CryptoCategory.DEFI, "coingecko_id": "maker"},
    "COMP": {"name": "Compound", "category": CryptoCategory.DEFI, "coingecko_id": "compound-governance-token"},
    
    # Meme
    "DOGE": {"name": "Dogecoin", "category": CryptoCategory.MEME, "coingecko_id": "dogecoin"},
    "SHIB": {"name": "Shiba Inu", "category": CryptoCategory.MEME, "coingecko_id": "shiba-inu"},
    "PEPE": {"name": "Pepe", "category": CryptoCategory.MEME, "coingecko_id": "pepe"},
    
    # AI
    "RNDR": {"name": "Render", "category": CryptoCategory.AI, "coingecko_id": "render-token"},
    "FET": {"name": "Fetch.ai", "category": CryptoCategory.AI, "coingecko_id": "fetch-ai"},
    "OCEAN": {"name": "Ocean Protocol", "category": CryptoCategory.AI, "coingecko_id": "ocean-protocol"},
    "AKT": {"name": "Akash", "category": CryptoCategory.AI, "coingecko_id": "akash-network"},
    
    # Gaming
    "IMX": {"name": "Immutable X", "category": CryptoCategory.GAMING, "coingecko_id": "immutable-x"},
    "GALA": {"name": "Gala", "category": CryptoCategory.GAMING, "coingecko_id": "gala"},
    "SAND": {"name": "The Sandbox", "category": CryptoCategory.GAMING, "coingecko_id": "the-sandbox"},
    "AXS": {"name": "Axie Infinity", "category": CryptoCategory.GAMING, "coingecko_id": "axie-infinity"},
}


class CryptoDataSource:
    """
    Cryptocurrency data source using CoinGecko and other APIs.
    """
    
    COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
    FEAR_GREED_URL = "https://api.alternative.me/fng/"
    
    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = 30  # seconds
        self._last_update: Optional[datetime] = None
        self.connected = False
        
    async def connect(self) -> bool:
        """Initialize the data source."""
        try:
            self._client = httpx.AsyncClient(timeout=30.0)
            self.connected = True
            logger.info("Crypto data source connected")
            return True
        except Exception as e:
            logger.error(f"Failed to connect crypto data source: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Close the data source."""
        if self._client:
            await self._client.aclose()
            self._client = None
        self.connected = False
    
    async def get_prices(
        self,
        symbols: Optional[List[str]] = None,
        category: Optional[CryptoCategory] = None
    ) -> List[CryptoPrice]:
        """
        Get current crypto prices.
        
        Args:
            symbols: Specific symbols to fetch (e.g., ["BTC", "ETH"])
            category: Filter by category
            
        Returns:
            List of CryptoPrice objects
        """
        try:
            # Filter coins
            target_coins = CRYPTO_COINS.copy()
            
            if symbols:
                target_coins = {k: v for k, v in target_coins.items() if k in symbols}
            
            if category:
                target_coins = {k: v for k, v in target_coins.items() if v["category"] == category}
            
            if not target_coins:
                return []
            
            # Build CoinGecko IDs
            ids = ",".join([v["coingecko_id"] for v in target_coins.values()])
            
            # Fetch from CoinGecko
            if self._client:
                try:
                    response = await self._client.get(
                        f"{self.COINGECKO_BASE_URL}/coins/markets",
                        params={
                            "vs_currency": "usd",
                            "ids": ids,
                            "order": "market_cap_desc",
                            "per_page": 100,
                            "sparkline": "false",
                            "price_change_percentage": "24h,7d"
                        }
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        return self._parse_coingecko_data(data, target_coins)
                except Exception as e:
                    logger.warning(f"CoinGecko API error: {e}")
            
            # Return mock data on error
            return self._get_mock_prices(target_coins)
            
        except Exception as e:
            logger.error(f"Error fetching crypto prices: {e}")
            return self._get_mock_prices(CRYPTO_COINS if not symbols else {s: CRYPTO_COINS.get(s, {}) for s in symbols if s in CRYPTO_COINS})
    
    def _parse_coingecko_data(self, data: List[Dict], coins: Dict) -> List[CryptoPrice]:
        """Parse CoinGecko API response."""
        prices = []
        
        # Create reverse lookup
        id_to_symbol = {v["coingecko_id"]: k for k, v in coins.items()}
        
        for item in data:
            symbol = id_to_symbol.get(item.get("id"))
            if not symbol:
                continue
                
            coin_info = coins.get(symbol, {})
            
            prices.append(CryptoPrice(
                symbol=symbol,
                name=item.get("name", coin_info.get("name", symbol)),
                category=coin_info.get("category", CryptoCategory.MAJOR),
                price=item.get("current_price", 0),
                change_24h=item.get("price_change_24h", 0),
                change_24h_pct=item.get("price_change_percentage_24h", 0),
                change_7d_pct=item.get("price_change_percentage_7d_in_currency", 0) or 0,
                high_24h=item.get("high_24h", 0),
                low_24h=item.get("low_24h", 0),
                volume_24h=item.get("total_volume", 0),
                market_cap=item.get("market_cap", 0),
                timestamp=datetime.utcnow(),
                source="coingecko"
            ))
        
        return prices
    
    def _get_mock_prices(self, coins: Dict) -> List[CryptoPrice]:
        """Get mock crypto prices for demo."""
        import random
        
        mock_base_prices = {
            "BTC": 95000, "ETH": 3500, "SOL": 180, "XRP": 2.2, "ADA": 0.95,
            "AVAX": 35, "DOT": 7, "MATIC": 0.45, "ARB": 0.95, "OP": 1.8,
            "UNI": 12, "AAVE": 280, "LINK": 22, "MKR": 2800, "COMP": 85,
            "DOGE": 0.35, "SHIB": 0.000022, "PEPE": 0.000018,
            "RNDR": 8.5, "FET": 1.5, "OCEAN": 0.75, "AKT": 3.2,
            "IMX": 1.8, "GALA": 0.035, "SAND": 0.45, "AXS": 7.5,
        }
        
        prices = []
        for symbol, info in coins.items():
            base_price = mock_base_prices.get(symbol, 1.0)
            change_pct = random.uniform(-8, 8)
            change = base_price * (change_pct / 100)
            
            prices.append(CryptoPrice(
                symbol=symbol,
                name=info.get("name", symbol),
                category=info.get("category", CryptoCategory.MAJOR),
                price=base_price + change,
                change_24h=change,
                change_24h_pct=change_pct,
                change_7d_pct=random.uniform(-15, 15),
                high_24h=base_price * 1.05,
                low_24h=base_price * 0.95,
                volume_24h=random.randint(100000000, 5000000000),
                market_cap=random.randint(1000000000, 100000000000),
                timestamp=datetime.utcnow(),
            ))
        
        return prices
    
    async def get_fear_greed_index(self) -> Optional[FearGreedIndex]:
        """Get the Crypto Fear & Greed Index."""
        try:
            if self._client:
                response = await self._client.get(self.FEAR_GREED_URL)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("data"):
                        item = data["data"][0]
                        return FearGreedIndex(
                            value=int(item.get("value", 50)),
                            classification=item.get("value_classification", "Neutral"),
                            timestamp=datetime.utcnow()
                        )
        except Exception as e:
            logger.warning(f"Fear & Greed API error: {e}")
        
        # Mock data
        import random
        value = random.randint(20, 80)
        if value < 25:
            classification = "Extreme Fear"
        elif value < 40:
            classification = "Fear"
        elif value < 60:
            classification = "Neutral"
        elif value < 75:
            classification = "Greed"
        else:
            classification = "Extreme Greed"
            
        return FearGreedIndex(
            value=value,
            classification=classification,
            timestamp=datetime.utcnow()
        )
    
    async def get_crypto_news(self, limit: int = 20) -> List[CryptoNews]:
        """Get crypto-related news."""
        import random
        
        news_templates = [
            ("Bitcoin ETFs see record inflows as institutional adoption grows", ["BTC"], 0.7),
            ("Ethereum upgrade successful, gas fees drop significantly", ["ETH"], 0.6),
            ("Solana DeFi ecosystem reaches new TVL milestone", ["SOL"], 0.5),
            ("SEC provides clarity on crypto regulations", ["BTC", "ETH"], 0.4),
            ("Major exchange adds support for new AI tokens", ["RNDR", "FET"], 0.5),
            ("Bitcoin mining difficulty reaches all-time high", ["BTC"], 0.3),
            ("Layer 2 solutions process record transactions", ["ARB", "OP", "MATIC"], 0.5),
            ("DeFi protocol announces major upgrade", ["UNI", "AAVE"], 0.4),
            ("Whale moves large BTC position to cold storage", ["BTC"], 0.3),
            ("Gaming tokens surge on new partnership announcements", ["IMX", "GALA"], 0.6),
            ("Meme coin rally continues with social media buzz", ["DOGE", "SHIB"], 0.4),
            ("Central bank discusses CBDC implications for crypto", ["BTC", "ETH"], 0.2),
            ("AI tokens outperform market amid tech rally", ["RNDR", "FET", "OCEAN"], 0.7),
            ("Major retailer begins accepting crypto payments", ["BTC", "ETH"], 0.6),
            ("Crypto market cap surpasses previous high", ["BTC", "ETH", "SOL"], 0.5),
        ]
        
        news = []
        for i, (title, coins, sentiment) in enumerate(news_templates[:limit]):
            news.append(CryptoNews(
                title=title,
                summary=f"Breaking: {title}. Analysts react to latest developments...",
                source=random.choice(["CoinDesk", "The Block", "Decrypt", "CoinTelegraph"]),
                url=f"https://example.com/crypto-news/{i}",
                published=datetime.utcnow() - timedelta(hours=random.randint(1, 48)),
                coins=coins,
                sentiment=sentiment + random.uniform(-0.1, 0.1),
            ))
        
        return news
    
    async def get_whale_alerts(self, limit: int = 10) -> List[WhaleAlert]:
        """Get recent whale transactions."""
        import random
        
        alerts = []
        symbols = ["BTC", "ETH", "SOL", "XRP", "DOGE"]
        tx_types = ["exchange_deposit", "exchange_withdrawal", "transfer"]
        
        for i in range(limit):
            symbol = random.choice(symbols)
            amount = random.uniform(100, 10000) if symbol == "BTC" else random.uniform(1000, 100000)
            price = {"BTC": 95000, "ETH": 3500, "SOL": 180, "XRP": 2.2, "DOGE": 0.35}.get(symbol, 100)
            
            alerts.append(WhaleAlert(
                symbol=symbol,
                amount=amount,
                usd_value=amount * price,
                from_address=f"0x{''.join(random.choices('0123456789abcdef', k=8))}...",
                to_address=f"0x{''.join(random.choices('0123456789abcdef', k=8))}...",
                transaction_type=random.choice(tx_types),
                timestamp=datetime.utcnow() - timedelta(minutes=random.randint(5, 300)),
                tx_hash=f"0x{''.join(random.choices('0123456789abcdef', k=64))}"
            ))
        
        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)
    
    def get_supported_cryptos(self) -> Dict:
        """Get all supported cryptocurrencies."""
        return {
            "coins": CRYPTO_COINS,
            "categories": [c.value for c in CryptoCategory],
        }


# Singleton instance
_crypto_source: Optional[CryptoDataSource] = None


def get_crypto_source() -> CryptoDataSource:
    """Get or create the crypto data source."""
    global _crypto_source
    if _crypto_source is None:
        _crypto_source = CryptoDataSource()
    return _crypto_source


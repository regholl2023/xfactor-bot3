"""
AInvest Data Source Integration

AInvest provides AI-powered stock analysis, sentiment analysis, and trading signals.
Website: https://ainvest.com

This integration provides:
- AI-powered stock recommendations
- Sentiment analysis
- Trading signals
- News aggregation
- Earnings tracking
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import httpx
from loguru import logger

from src.data_sources.base import BaseDataSource, NewsArticle, TradingSignal, InsiderTrade
from src.data_sources.registry import DataSourceRegistry
from src.config.settings import get_settings


@dataclass
class AInvestRecommendation:
    """AI-powered stock recommendation from AInvest."""
    symbol: str
    company: str
    ai_score: float  # 0-100
    recommendation: str  # Strong Buy, Buy, Hold, Sell, Strong Sell
    target_price: float
    current_price: float
    upside_pct: float
    signals: List[str]
    confidence: float
    analysis_date: datetime
    
    
@dataclass
class AInvestSentiment:
    """Sentiment analysis for a stock."""
    symbol: str
    overall_sentiment: float  # -1 to 1
    news_sentiment: float
    social_sentiment: float
    analyst_sentiment: float
    volume_sentiment: float  # Based on unusual volume
    last_updated: datetime
    

class AInvestDataSource(BaseDataSource):
    """
    AInvest data source integration.
    
    AInvest provides AI-powered stock analysis including:
    - Stock recommendations with AI scores
    - Sentiment analysis (news, social, analyst)
    - Trading signals based on technical and fundamental analysis
    - Earnings calendar and estimates
    - Options flow analysis
    """
    
    BASE_URL = "https://api.ainvest.com/v1"  # Placeholder - actual API endpoint TBD
    
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.ainvest_api_key if hasattr(settings, 'ainvest_api_key') else ""
        self.connected = False
        self.http_client: Optional[httpx.AsyncClient] = None
        logger.info("AInvestDataSource initialized")
        
    async def connect(self) -> bool:
        """Establish connection to AInvest API."""
        try:
            if not self.api_key:
                logger.warning("AInvest API key not configured. Using mock data mode.")
                self.connected = True
                return True
                
            self.http_client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Accept": "application/json"
                },
                timeout=30.0
            )
            
            # Test connection
            response = await self.http_client.get("/health")
            if response.status_code == 200:
                self.connected = True
                logger.info("Connected to AInvest API")
                return True
            return False
            
        except Exception as e:
            logger.warning(f"Could not connect to AInvest API: {e}. Using mock data.")
            self.connected = True  # Allow mock data
            return True
            
    async def disconnect(self) -> None:
        """Disconnect from AInvest API."""
        if self.http_client:
            await self.http_client.aclose()
            self.http_client = None
        self.connected = False
        logger.info("Disconnected from AInvest")
    
    async def get_quote(self, symbol: str):
        """Get real-time quote for a symbol.
        
        Note: AInvest focuses on AI analysis, not real-time quotes.
        Returns None - use a market data source for quotes.
        """
        return None
    
    async def get_bars(
        self,
        symbol: str,
        timeframe: str = "1d",
        start=None,
        end=None,
        limit: int = 100
    ):
        """Get historical bars for a symbol.
        
        Note: AInvest focuses on AI analysis, not historical data.
        Returns empty list - use a market data source for bars.
        """
        return []
        
    async def get_ai_recommendations(
        self, 
        symbols: Optional[List[str]] = None,
        min_score: float = 0,
        limit: int = 100
    ) -> List[AInvestRecommendation]:
        """
        Get AI-powered stock recommendations.
        
        Args:
            symbols: Optional list of symbols to filter
            min_score: Minimum AI score (0-100)
            limit: Maximum number of recommendations
            
        Returns:
            List of AInvestRecommendation objects
        """
        if not self.connected:
            await self.connect()
            
        try:
            if self.http_client and self.api_key:
                params = {"limit": limit}
                if symbols:
                    params["symbols"] = ",".join(symbols)
                if min_score > 0:
                    params["min_score"] = min_score
                    
                response = await self.http_client.get("/recommendations", params=params)
                response.raise_for_status()
                data = response.json()
                
                return [
                    AInvestRecommendation(
                        symbol=item["symbol"],
                        company=item["company"],
                        ai_score=item["ai_score"],
                        recommendation=item["recommendation"],
                        target_price=item["target_price"],
                        current_price=item["current_price"],
                        upside_pct=item["upside_pct"],
                        signals=item.get("signals", []),
                        confidence=item.get("confidence", 75),
                        analysis_date=datetime.fromisoformat(item["analysis_date"])
                    )
                    for item in data.get("recommendations", [])
                ]
            else:
                # Return mock data
                return self._generate_mock_recommendations(symbols, limit)
                
        except Exception as e:
            logger.error(f"Error fetching AInvest recommendations: {e}")
            return self._generate_mock_recommendations(symbols, limit)
            
    async def get_sentiment(self, symbol: str) -> Optional[AInvestSentiment]:
        """
        Get sentiment analysis for a stock.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            AInvestSentiment object or None
        """
        if not self.connected:
            await self.connect()
            
        try:
            if self.http_client and self.api_key:
                response = await self.http_client.get(f"/sentiment/{symbol}")
                response.raise_for_status()
                data = response.json()
                
                return AInvestSentiment(
                    symbol=symbol,
                    overall_sentiment=data["overall_sentiment"],
                    news_sentiment=data["news_sentiment"],
                    social_sentiment=data["social_sentiment"],
                    analyst_sentiment=data["analyst_sentiment"],
                    volume_sentiment=data.get("volume_sentiment", 0),
                    last_updated=datetime.fromisoformat(data["last_updated"])
                )
            else:
                # Return mock data
                return self._generate_mock_sentiment(symbol)
                
        except Exception as e:
            logger.error(f"Error fetching AInvest sentiment for {symbol}: {e}")
            return self._generate_mock_sentiment(symbol)
            
    async def get_news(
        self, 
        symbols: Optional[List[str]] = None, 
        limit: int = 100
    ) -> List[NewsArticle]:
        """
        Fetch news articles from AInvest.
        
        Args:
            symbols: Optional list of symbols to filter
            limit: Maximum number of articles
            
        Returns:
            List of NewsArticle objects
        """
        if not self.connected:
            await self.connect()
            
        try:
            if self.http_client and self.api_key:
                params = {"limit": limit}
                if symbols:
                    params["symbols"] = ",".join(symbols)
                    
                response = await self.http_client.get("/news", params=params)
                response.raise_for_status()
                data = response.json()
                
                return [
                    NewsArticle(
                        title=item["title"],
                        url=item["url"],
                        source="AInvest",
                        published=datetime.fromisoformat(item["published_at"]),
                        sentiment=item.get("sentiment"),
                        symbols=item.get("symbols", []),
                        content=item.get("content")
                    )
                    for item in data.get("articles", [])
                ]
            else:
                # Return mock data
                return self._generate_mock_news(symbols, limit)
                
        except Exception as e:
            logger.error(f"Error fetching AInvest news: {e}")
            return self._generate_mock_news(symbols, limit)
            
    async def get_trading_signals(
        self, 
        signal_type: Optional[str] = None, 
        limit: int = 100
    ) -> List[TradingSignal]:
        """
        Fetch AI-generated trading signals.
        
        Args:
            signal_type: Optional filter by signal type
            limit: Maximum number of signals
            
        Returns:
            List of TradingSignal objects
        """
        if not self.connected:
            await self.connect()
            
        try:
            if self.http_client and self.api_key:
                params = {"limit": limit}
                if signal_type:
                    params["type"] = signal_type
                    
                response = await self.http_client.get("/signals", params=params)
                response.raise_for_status()
                data = response.json()
                
                return [
                    TradingSignal(
                        source="AInvest",
                        signal_type=item["signal_type"],
                        symbol=item["symbol"],
                        strength=item.get("strength", 0.7),
                        price=item.get("price", 0.0),
                        target_price=item.get("target_price"),
                        stop_loss=item.get("stop_loss"),
                        timestamp=datetime.fromisoformat(item["timestamp"]),
                        confidence=item.get("confidence", 0.7),
                        timeframe=item.get("timeframe", "1d"),
                        reasoning=item.get("reasoning", "")
                    )
                    for item in data.get("signals", [])
                ]
            else:
                # Return mock data
                return self._generate_mock_signals(limit)
                
        except Exception as e:
            logger.error(f"Error fetching AInvest trading signals: {e}")
            return self._generate_mock_signals(limit)
            
    async def get_insider_trades(self, limit: int = 100) -> List[InsiderTrade]:
        """
        Fetch insider trading data via AInvest's SEC filing aggregation.
        
        Args:
            limit: Maximum number of trades
            
        Returns:
            List of InsiderTrade objects
        """
        if not self.connected:
            await self.connect()
            
        try:
            if self.http_client and self.api_key:
                response = await self.http_client.get("/insider-trades", params={"limit": limit})
                response.raise_for_status()
                data = response.json()
                
                return [
                    InsiderTrade(
                        ticker=item["ticker"],
                        insider_name=item["insider_name"],
                        relation=item["relation"],
                        trade_type=item["trade_type"],
                        value=item["value"],
                        shares=item["shares"],
                        trade_date=datetime.fromisoformat(item["trade_date"]),
                        filing_date=datetime.fromisoformat(item["filing_date"])
                    )
                    for item in data.get("trades", [])
                ]
            else:
                # Return mock data
                return self._generate_mock_insider_trades(limit)
                
        except Exception as e:
            logger.error(f"Error fetching AInvest insider trades: {e}")
            return self._generate_mock_insider_trades(limit)
            
    async def get_earnings_calendar(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get upcoming earnings reports.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            limit: Maximum number of reports
            
        Returns:
            List of earnings report dictionaries
        """
        if not self.connected:
            await self.connect()
            
        if start_date is None:
            start_date = datetime.now()
        if end_date is None:
            end_date = start_date + timedelta(days=30)
            
        try:
            if self.http_client and self.api_key:
                params = {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                    "limit": limit
                }
                response = await self.http_client.get("/earnings", params=params)
                response.raise_for_status()
                return response.json().get("earnings", [])
            else:
                return self._generate_mock_earnings(limit)
                
        except Exception as e:
            logger.error(f"Error fetching AInvest earnings calendar: {e}")
            return self._generate_mock_earnings(limit)
            
    # =========================================================================
    # Mock Data Generators (for development/testing without API key)
    # =========================================================================
    
    def _generate_mock_recommendations(
        self, 
        symbols: Optional[List[str]], 
        limit: int
    ) -> List[AInvestRecommendation]:
        """Generate mock AI recommendations."""
        import random
        
        all_symbols = symbols or [
            "NVDA", "AAPL", "MSFT", "GOOGL", "META", "TSLA", "AMZN", "AMD", 
            "PLTR", "SMCI", "CRM", "ORCL", "NFLX", "ADBE", "INTC", "MU",
            "AVGO", "QCOM", "AMAT", "LRCX", "KLAC", "MRVL", "ON", "MCHP"
        ]
        
        recommendations = ["Strong Buy", "Buy", "Hold", "Sell", "Strong Sell"]
        signal_types = [
            "Momentum Surge", "Value Play", "Breakout Imminent", "Oversold Bounce",
            "Earnings Catalyst", "Insider Buying", "Institutional Accumulation",
            "Technical Breakout", "RSI Divergence", "MACD Crossover",
            "Volume Spike", "Price Gap Fill", "Support Bounce", "Channel Breakout"
        ]
        
        results = []
        for i in range(min(limit, len(all_symbols) * 4)):
            symbol = all_symbols[i % len(all_symbols)]
            current_price = random.uniform(50, 500)
            ai_score = random.uniform(55, 95)
            
            # Bias recommendation based on AI score
            if ai_score >= 80:
                rec = random.choice(["Strong Buy", "Buy"])
            elif ai_score >= 65:
                rec = random.choice(["Buy", "Hold"])
            elif ai_score >= 50:
                rec = "Hold"
            else:
                rec = random.choice(["Hold", "Sell"])
                
            upside = random.uniform(-10, 40) if rec in ["Strong Buy", "Buy"] else random.uniform(-20, 15)
            target = current_price * (1 + upside / 100)
            
            results.append(AInvestRecommendation(
                symbol=symbol,
                company=f"{symbol} Corporation",
                ai_score=round(ai_score, 1),
                recommendation=rec,
                target_price=round(target, 2),
                current_price=round(current_price, 2),
                upside_pct=round(upside, 1),
                signals=random.sample(signal_types, random.randint(1, 4)),
                confidence=round(random.uniform(65, 95), 0),
                analysis_date=datetime.now() - timedelta(hours=random.randint(0, 48))
            ))
            
        return results[:limit]
        
    def _generate_mock_sentiment(self, symbol: str) -> AInvestSentiment:
        """Generate mock sentiment data."""
        import random
        
        overall = random.uniform(-0.5, 0.8)
        return AInvestSentiment(
            symbol=symbol,
            overall_sentiment=round(overall, 2),
            news_sentiment=round(overall + random.uniform(-0.2, 0.2), 2),
            social_sentiment=round(overall + random.uniform(-0.3, 0.3), 2),
            analyst_sentiment=round(overall + random.uniform(-0.1, 0.1), 2),
            volume_sentiment=round(random.uniform(-0.5, 0.5), 2),
            last_updated=datetime.now()
        )
        
    def _generate_mock_news(
        self, 
        symbols: Optional[List[str]], 
        limit: int
    ) -> List[NewsArticle]:
        """Generate mock news articles."""
        import random
        
        tickers = symbols or ["NVDA", "AAPL", "MSFT", "GOOGL", "META", "TSLA", "AMZN", "AMD"]
        headlines = [
            "{ticker} Beats Earnings Expectations",
            "{ticker} Announces New Product Launch",
            "Analysts Upgrade {ticker} Rating",
            "{ticker} Expands Into New Markets",
            "{ticker} Partners with Major Tech Company",
            "{ticker} Stock Rises on Strong Guidance",
            "Institutional Investors Increase {ticker} Holdings",
            "{ticker} CEO Discusses Growth Strategy"
        ]
        
        results = []
        for i in range(limit):
            ticker = random.choice(tickers)
            headline = random.choice(headlines).replace("{ticker}", ticker)
            results.append(NewsArticle(
                title=headline,
                summary=f"AI-powered analysis of {ticker}'s market activity and performance.",
                url=f"https://ainvest.com/news/{ticker.lower()}-{i}",
                source="AInvest",
                published=datetime.now() - timedelta(hours=random.randint(0, 72)),
                sentiment=random.uniform(-0.5, 0.8),
                symbols=[ticker],
                relevance=random.uniform(0.6, 0.95),
            ))
            
        return results
        
    def _generate_mock_signals(self, limit: int) -> List[TradingSignal]:
        """Generate mock trading signals."""
        import random
        
        tickers = ["NVDA", "AAPL", "MSFT", "GOOGL", "META", "TSLA", "AMZN", "AMD", "SPY", "QQQ"]
        signal_types = [
            "AI Buy Signal", "Momentum Alert", "Breakout Detected", 
            "Unusual Volume", "RSI Oversold", "MACD Bullish Cross"
        ]
        
        results = []
        for i in range(limit):
            ticker = random.choice(tickers)
            price = round(random.uniform(100, 600), 2)
            results.append(TradingSignal(
                source="AInvest AI",
                signal_type=random.choice(signal_types),
                symbol=ticker,
                strength=random.uniform(0.6, 0.95),
                price=price,
                target_price=round(price * 1.15, 2),
                stop_loss=round(price * 0.95, 2),
                timestamp=datetime.now() - timedelta(hours=random.randint(0, 24)),
                confidence=random.uniform(0.7, 0.95),
                timeframe="1d",
                reasoning=f"AI detected {random.choice(signal_types).lower()} pattern"
            ))
            
        return results
        
    def _generate_mock_insider_trades(self, limit: int) -> List[InsiderTrade]:
        """Generate mock insider trades."""
        import random
        
        tickers = ["NVDA", "AAPL", "MSFT", "GOOGL", "META", "TSLA", "AMZN", "AMD"]
        names = ["CEO", "CFO", "Director", "VP Sales", "COO", "CTO", "Board Member"]
        
        results = []
        for i in range(limit):
            ticker = random.choice(tickers)
            transaction_type = "buy" if random.random() > 0.35 else "sell"
            shares = random.randint(10000, 500000)
            price = round(random.uniform(100, 500), 2)
            
            results.append(InsiderTrade(
                symbol=ticker,
                insider_name=f"{random.choice(['John', 'Jane', 'Robert', 'Sarah'])} {random.choice(['Smith', 'Johnson', 'Williams', 'Brown'])}",
                title=random.choice(names),
                transaction_type=transaction_type,
                shares=shares,
                price=price,
                value=round(shares * price, 2),
                shares_owned_after=random.randint(100000, 5000000),
                transaction_date=datetime.now() - timedelta(days=random.randint(1, 30)),
                filing_date=datetime.now() - timedelta(days=random.randint(0, 29)),
                source="SEC"
            ))
            
        return results
        
    def _generate_mock_earnings(self, limit: int) -> List[Dict[str, Any]]:
        """Generate mock earnings calendar."""
        import random
        
        tickers = ["NVDA", "AAPL", "MSFT", "GOOGL", "META", "TSLA", "AMZN", "AMD", "CRM", "ORCL"]
        
        results = []
        for i in range(limit):
            ticker = tickers[i % len(tickers)]
            report_date = datetime.now() + timedelta(days=random.randint(1, 45))
            
            results.append({
                "ticker": ticker,
                "company": f"{ticker} Corporation",
                "report_date": report_date.isoformat(),
                "report_time": random.choice(["BMO", "AMC"]),
                "eps_estimate": round(random.uniform(1, 10), 2),
                "revenue_estimate": f"${random.randint(10, 100)}B",
                "surprise_history": round(random.uniform(-5, 15), 1),
                "options_iv": random.randint(30, 120)
            })
            
        return results


# Note: Registration happens via get_data_source_registry() singleton
# The registry instance should call:
# registry.register_source_class(DataSourceType.AINVEST, AInvestDataSource)


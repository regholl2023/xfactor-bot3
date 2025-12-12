"""
Data Source Registry - Manages all market data sources.
"""

from typing import Dict, List, Optional, Type
from loguru import logger

from src.data_sources.base import BaseDataSource, DataSourceType, Quote, Bar


class DataSourceRegistry:
    """
    Central registry for managing multiple data sources.
    
    Provides:
    - Unified quote/bar interface across sources
    - Automatic failover between sources
    - Data aggregation and validation
    """
    
    def __init__(self):
        self._sources: Dict[DataSourceType, BaseDataSource] = {}
        self._source_classes: Dict[DataSourceType, Type[BaseDataSource]] = {}
        self._priority: List[DataSourceType] = []  # Ordered by priority
    
    def register_source_class(
        self,
        source_type: DataSourceType,
        source_class: Type[BaseDataSource]
    ) -> None:
        """Register a data source implementation."""
        self._source_classes[source_type] = source_class
        logger.info(f"Registered data source: {source_type.value}")
    
    async def connect_source(
        self,
        source_type: DataSourceType,
        **config
    ) -> bool:
        """Connect to a data source."""
        if source_type not in self._source_classes:
            logger.error(f"Data source not registered: {source_type.value}")
            return False
        
        try:
            source_class = self._source_classes[source_type]
            source = source_class(**config)
            
            if await source.connect():
                self._sources[source_type] = source
                if source_type not in self._priority:
                    self._priority.append(source_type)
                logger.info(f"Connected to data source: {source_type.value}")
                return True
            
        except Exception as e:
            logger.error(f"Error connecting to {source_type.value}: {e}")
        
        return False
    
    async def disconnect_source(self, source_type: DataSourceType) -> None:
        """Disconnect from a data source."""
        if source_type in self._sources:
            await self._sources[source_type].disconnect()
            del self._sources[source_type]
            if source_type in self._priority:
                self._priority.remove(source_type)
    
    def set_priority(self, priority: List[DataSourceType]) -> None:
        """Set data source priority for failover."""
        self._priority = [s for s in priority if s in self._sources]
    
    async def get_quote(
        self,
        symbol: str,
        source: DataSourceType = None
    ) -> Optional[Quote]:
        """
        Get quote, with automatic failover.
        
        Args:
            symbol: Ticker symbol
            source: Specific source to use (optional)
        """
        sources_to_try = [source] if source else self._priority
        
        for src in sources_to_try:
            if src not in self._sources:
                continue
            try:
                quote = await self._sources[src].get_quote(symbol)
                if quote:
                    return quote
            except Exception as e:
                logger.warning(f"Quote failed from {src.value}: {e}")
        
        return None
    
    async def get_quotes(
        self,
        symbols: List[str],
        source: DataSourceType = None
    ) -> Dict[str, Quote]:
        """Get quotes for multiple symbols."""
        quotes = {}
        for symbol in symbols:
            quote = await self.get_quote(symbol, source)
            if quote:
                quotes[symbol] = quote
        return quotes
    
    async def get_bars(
        self,
        symbol: str,
        timeframe: str = "1d",
        limit: int = 100,
        source: DataSourceType = None
    ) -> List[Bar]:
        """Get historical bars with failover."""
        sources_to_try = [source] if source else self._priority
        
        for src in sources_to_try:
            if src not in self._sources:
                continue
            try:
                bars = await self._sources[src].get_bars(symbol, timeframe, limit=limit)
                if bars:
                    return bars
            except Exception as e:
                logger.warning(f"Bars failed from {src.value}: {e}")
        
        return []
    
    @property
    def connected_sources(self) -> List[DataSourceType]:
        """Get connected data sources."""
        return list(self._sources.keys())
    
    def to_dict(self) -> Dict:
        """Get registry status."""
        return {
            "connected_sources": [s.value for s in self.connected_sources],
            "priority": [s.value for s in self._priority],
            "source_status": {
                s.value: self._sources[s].is_connected
                for s in self._sources
            }
        }


# Global registry
_registry: Optional[DataSourceRegistry] = None


def get_data_registry() -> DataSourceRegistry:
    """Get or create global data source registry."""
    global _registry
    if _registry is None:
        _registry = DataSourceRegistry()
    return _registry


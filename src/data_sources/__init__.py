"""
Data Sources Integration Layer for XFactor Bot.
Aggregates market data from multiple providers.
"""

from src.data_sources.base import BaseDataSource, DataSourceType, Quote, Bar
from src.data_sources.tradingview import TradingViewWebhook
from src.data_sources.registry import DataSourceRegistry, get_data_registry

__all__ = [
    "BaseDataSource",
    "DataSourceType",
    "Quote",
    "Bar",
    "TradingViewWebhook",
    "DataSourceRegistry",
    "get_data_registry",
]


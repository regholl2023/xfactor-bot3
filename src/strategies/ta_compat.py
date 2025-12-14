"""
Technical Analysis Compatibility Layer.

Provides pandas_ta-like API using the ta library.
This allows code written for pandas_ta to work with the ta library.
"""

import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator, ROCIndicator
from ta.trend import MACD, ADXIndicator, SMAIndicator, EMAIndicator
from ta.volatility import BollingerBands, AverageTrueRange


def rsi(close: pd.Series, length: int = 14) -> pd.Series:
    """Calculate RSI."""
    indicator = RSIIndicator(close=close, window=length)
    return indicator.rsi()


def macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """Calculate MACD, returning DataFrame with MACD_12_26_9, MACDh_12_26_9, MACDs_12_26_9."""
    indicator = MACD(close=close, window_fast=fast, window_slow=slow, window_sign=signal)
    result = pd.DataFrame({
        f"MACD_{fast}_{slow}_{signal}": indicator.macd(),
        f"MACDh_{fast}_{slow}_{signal}": indicator.macd_diff(),
        f"MACDs_{fast}_{slow}_{signal}": indicator.macd_signal(),
    })
    return result


def sma(series: pd.Series, length: int = 20) -> pd.Series:
    """Calculate Simple Moving Average."""
    indicator = SMAIndicator(close=series, window=length)
    return indicator.sma_indicator()


def ema(series: pd.Series, length: int = 20) -> pd.Series:
    """Calculate Exponential Moving Average."""
    indicator = EMAIndicator(close=series, window=length)
    return indicator.ema_indicator()


def bbands(close: pd.Series, length: int = 20, std: float = 2.0) -> pd.DataFrame:
    """Calculate Bollinger Bands, returning DataFrame with BBL, BBM, BBU, BBB, BBP."""
    indicator = BollingerBands(close=close, window=length, window_dev=int(std))
    result = pd.DataFrame({
        f"BBL_{length}_{std}": indicator.bollinger_lband(),
        f"BBM_{length}_{std}": indicator.bollinger_mavg(),
        f"BBU_{length}_{std}": indicator.bollinger_hband(),
        f"BBB_{length}_{std}": indicator.bollinger_wband(),
        f"BBP_{length}_{std}": indicator.bollinger_pband(),
    })
    return result


def atr(high: pd.Series, low: pd.Series, close: pd.Series, length: int = 14) -> pd.Series:
    """Calculate Average True Range."""
    indicator = AverageTrueRange(high=high, low=low, close=close, window=length)
    return indicator.average_true_range()


def roc(close: pd.Series, length: int = 10) -> pd.Series:
    """Calculate Rate of Change."""
    indicator = ROCIndicator(close=close, window=length)
    return indicator.roc()


def mom(close: pd.Series, length: int = 10) -> pd.Series:
    """Calculate Momentum (simple difference)."""
    return close.diff(length)


def adx(high: pd.Series, low: pd.Series, close: pd.Series, length: int = 14) -> pd.DataFrame:
    """Calculate ADX, returning DataFrame with ADX, DMP, DMN."""
    indicator = ADXIndicator(high=high, low=low, close=close, window=length)
    result = pd.DataFrame({
        f"ADX_{length}": indicator.adx(),
        f"DMP_{length}": indicator.adx_pos(),
        f"DMN_{length}": indicator.adx_neg(),
    })
    return result


def zscore(series: pd.Series, length: int = 20) -> pd.Series:
    """Calculate Z-Score."""
    mean = series.rolling(window=length).mean()
    std = series.rolling(window=length).std()
    return (series - mean) / std


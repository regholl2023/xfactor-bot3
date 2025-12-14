"""
Global Stock Exchange Configuration

Provides access to stocks from all major global exchanges including:
- US: NYSE, NASDAQ, AMEX
- Europe: LSE (London), Euronext, Frankfurt, Milan, Swiss, Madrid
- Asia: Shanghai, Shenzhen, Hong Kong, Tokyo, Taiwan, Singapore, Korea
- Americas: Toronto (TSX), Brazil (B3), Mexico (BMV), Buenos Aires (BCBA)
- Oceania: ASX (Australia), NZX (New Zealand)
- Middle East: Tel Aviv, Saudi, Dubai

This module supports dynamic symbol lookup for ANY stock on these exchanges.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class ExchangeRegion(str, Enum):
    """Geographic regions for exchanges."""
    NORTH_AMERICA = "north_america"
    EUROPE = "europe"
    ASIA_PACIFIC = "asia_pacific"
    LATIN_AMERICA = "latin_america"
    MIDDLE_EAST = "middle_east"
    AFRICA = "africa"


class Currency(str, Enum):
    """Major trading currencies."""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CNY = "CNY"
    HKD = "HKD"
    CAD = "CAD"
    AUD = "AUD"
    CHF = "CHF"
    KRW = "KRW"
    TWD = "TWD"
    SGD = "SGD"
    INR = "INR"
    BRL = "BRL"
    MXN = "MXN"
    ARS = "ARS"
    NZD = "NZD"
    ILS = "ILS"
    SAR = "SAR"
    AED = "AED"
    ZAR = "ZAR"
    SEK = "SEK"
    NOK = "NOK"
    DKK = "DKK"
    PLN = "PLN"
    RUB = "RUB"


@dataclass
class Exchange:
    """Stock exchange configuration."""
    code: str  # Exchange code (e.g., "NYSE", "LSE")
    name: str  # Full name
    country: str
    region: ExchangeRegion
    currency: Currency
    timezone: str
    suffix: str = ""  # Yahoo Finance suffix (e.g., ".L" for London)
    mic: str = ""  # Market Identifier Code (ISO 10383)
    trading_hours: str = ""  # Local trading hours
    is_supported: bool = True
    
    def format_symbol(self, symbol: str) -> str:
        """Format a symbol for this exchange (e.g., add suffix for Yahoo Finance)."""
        if self.suffix and not symbol.endswith(self.suffix):
            return f"{symbol}{self.suffix}"
        return symbol


# ============================================================================
# UNITED STATES EXCHANGES
# ============================================================================
NYSE = Exchange(
    code="NYSE",
    name="New York Stock Exchange",
    country="United States",
    region=ExchangeRegion.NORTH_AMERICA,
    currency=Currency.USD,
    timezone="America/New_York",
    suffix="",
    mic="XNYS",
    trading_hours="09:30-16:00",
)

NASDAQ = Exchange(
    code="NASDAQ",
    name="NASDAQ Stock Market",
    country="United States",
    region=ExchangeRegion.NORTH_AMERICA,
    currency=Currency.USD,
    timezone="America/New_York",
    suffix="",
    mic="XNAS",
    trading_hours="09:30-16:00",
)

AMEX = Exchange(
    code="AMEX",
    name="NYSE American (AMEX)",
    country="United States",
    region=ExchangeRegion.NORTH_AMERICA,
    currency=Currency.USD,
    timezone="America/New_York",
    suffix="",
    mic="XASE",
    trading_hours="09:30-16:00",
)

# ============================================================================
# CANADIAN EXCHANGES
# ============================================================================
TSX = Exchange(
    code="TSX",
    name="Toronto Stock Exchange",
    country="Canada",
    region=ExchangeRegion.NORTH_AMERICA,
    currency=Currency.CAD,
    timezone="America/Toronto",
    suffix=".TO",
    mic="XTSE",
    trading_hours="09:30-16:00",
)

TSXV = Exchange(
    code="TSXV",
    name="TSX Venture Exchange",
    country="Canada",
    region=ExchangeRegion.NORTH_AMERICA,
    currency=Currency.CAD,
    timezone="America/Toronto",
    suffix=".V",
    mic="XTSX",
    trading_hours="09:30-16:00",
)

# ============================================================================
# EUROPEAN EXCHANGES
# ============================================================================
LSE = Exchange(
    code="LSE",
    name="London Stock Exchange",
    country="United Kingdom",
    region=ExchangeRegion.EUROPE,
    currency=Currency.GBP,
    timezone="Europe/London",
    suffix=".L",
    mic="XLON",
    trading_hours="08:00-16:30",
)

EURONEXT_PARIS = Exchange(
    code="EPA",
    name="Euronext Paris",
    country="France",
    region=ExchangeRegion.EUROPE,
    currency=Currency.EUR,
    timezone="Europe/Paris",
    suffix=".PA",
    mic="XPAR",
    trading_hours="09:00-17:30",
)

EURONEXT_AMSTERDAM = Exchange(
    code="AMS",
    name="Euronext Amsterdam",
    country="Netherlands",
    region=ExchangeRegion.EUROPE,
    currency=Currency.EUR,
    timezone="Europe/Amsterdam",
    suffix=".AS",
    mic="XAMS",
    trading_hours="09:00-17:30",
)

EURONEXT_BRUSSELS = Exchange(
    code="EBR",
    name="Euronext Brussels",
    country="Belgium",
    region=ExchangeRegion.EUROPE,
    currency=Currency.EUR,
    timezone="Europe/Brussels",
    suffix=".BR",
    mic="XBRU",
    trading_hours="09:00-17:30",
)

EURONEXT_LISBON = Exchange(
    code="ELI",
    name="Euronext Lisbon",
    country="Portugal",
    region=ExchangeRegion.EUROPE,
    currency=Currency.EUR,
    timezone="Europe/Lisbon",
    suffix=".LS",
    mic="XLIS",
    trading_hours="08:00-16:30",
)

FRANKFURT = Exchange(
    code="FRA",
    name="Frankfurt Stock Exchange (Xetra)",
    country="Germany",
    region=ExchangeRegion.EUROPE,
    currency=Currency.EUR,
    timezone="Europe/Berlin",
    suffix=".DE",
    mic="XFRA",
    trading_hours="09:00-17:30",
)

MILAN = Exchange(
    code="BIT",
    name="Borsa Italiana (Milan)",
    country="Italy",
    region=ExchangeRegion.EUROPE,
    currency=Currency.EUR,
    timezone="Europe/Rome",
    suffix=".MI",
    mic="XMIL",
    trading_hours="09:00-17:30",
)

SWISS = Exchange(
    code="SWX",
    name="SIX Swiss Exchange",
    country="Switzerland",
    region=ExchangeRegion.EUROPE,
    currency=Currency.CHF,
    timezone="Europe/Zurich",
    suffix=".SW",
    mic="XSWX",
    trading_hours="09:00-17:30",
)

MADRID = Exchange(
    code="BME",
    name="Bolsa de Madrid",
    country="Spain",
    region=ExchangeRegion.EUROPE,
    currency=Currency.EUR,
    timezone="Europe/Madrid",
    suffix=".MC",
    mic="XMAD",
    trading_hours="09:00-17:30",
)

VIENNA = Exchange(
    code="VIE",
    name="Vienna Stock Exchange",
    country="Austria",
    region=ExchangeRegion.EUROPE,
    currency=Currency.EUR,
    timezone="Europe/Vienna",
    suffix=".VI",
    mic="XWBO",
    trading_hours="09:00-17:30",
)

STOCKHOLM = Exchange(
    code="STO",
    name="Nasdaq Stockholm",
    country="Sweden",
    region=ExchangeRegion.EUROPE,
    currency=Currency.SEK,
    timezone="Europe/Stockholm",
    suffix=".ST",
    mic="XSTO",
    trading_hours="09:00-17:30",
)

OSLO = Exchange(
    code="OSL",
    name="Oslo Stock Exchange",
    country="Norway",
    region=ExchangeRegion.EUROPE,
    currency=Currency.NOK,
    timezone="Europe/Oslo",
    suffix=".OL",
    mic="XOSL",
    trading_hours="09:00-16:20",
)

COPENHAGEN = Exchange(
    code="CPH",
    name="Nasdaq Copenhagen",
    country="Denmark",
    region=ExchangeRegion.EUROPE,
    currency=Currency.DKK,
    timezone="Europe/Copenhagen",
    suffix=".CO",
    mic="XCSE",
    trading_hours="09:00-17:00",
)

HELSINKI = Exchange(
    code="HEL",
    name="Nasdaq Helsinki",
    country="Finland",
    region=ExchangeRegion.EUROPE,
    currency=Currency.EUR,
    timezone="Europe/Helsinki",
    suffix=".HE",
    mic="XHEL",
    trading_hours="10:00-18:30",
)

WARSAW = Exchange(
    code="WSE",
    name="Warsaw Stock Exchange",
    country="Poland",
    region=ExchangeRegion.EUROPE,
    currency=Currency.PLN,
    timezone="Europe/Warsaw",
    suffix=".WA",
    mic="XWAR",
    trading_hours="09:00-17:00",
)

MOSCOW = Exchange(
    code="MOEX",
    name="Moscow Exchange",
    country="Russia",
    region=ExchangeRegion.EUROPE,
    currency=Currency.RUB,
    timezone="Europe/Moscow",
    suffix=".ME",
    mic="MISX",
    trading_hours="10:00-18:50",
    is_supported=False,  # Sanctions may affect access
)

# ============================================================================
# ASIAN EXCHANGES
# ============================================================================
SHANGHAI = Exchange(
    code="SSE",
    name="Shanghai Stock Exchange",
    country="China",
    region=ExchangeRegion.ASIA_PACIFIC,
    currency=Currency.CNY,
    timezone="Asia/Shanghai",
    suffix=".SS",
    mic="XSHG",
    trading_hours="09:30-15:00",
)

SHENZHEN = Exchange(
    code="SZSE",
    name="Shenzhen Stock Exchange",
    country="China",
    region=ExchangeRegion.ASIA_PACIFIC,
    currency=Currency.CNY,
    timezone="Asia/Shanghai",
    suffix=".SZ",
    mic="XSHE",
    trading_hours="09:30-15:00",
)

HONG_KONG = Exchange(
    code="HKEX",
    name="Hong Kong Stock Exchange",
    country="Hong Kong",
    region=ExchangeRegion.ASIA_PACIFIC,
    currency=Currency.HKD,
    timezone="Asia/Hong_Kong",
    suffix=".HK",
    mic="XHKG",
    trading_hours="09:30-16:00",
)

TOKYO = Exchange(
    code="TSE",
    name="Tokyo Stock Exchange",
    country="Japan",
    region=ExchangeRegion.ASIA_PACIFIC,
    currency=Currency.JPY,
    timezone="Asia/Tokyo",
    suffix=".T",
    mic="XTKS",
    trading_hours="09:00-15:00",
)

TAIWAN = Exchange(
    code="TWSE",
    name="Taiwan Stock Exchange",
    country="Taiwan",
    region=ExchangeRegion.ASIA_PACIFIC,
    currency=Currency.TWD,
    timezone="Asia/Taipei",
    suffix=".TW",
    mic="XTAI",
    trading_hours="09:00-13:30",
)

KOREA = Exchange(
    code="KRX",
    name="Korea Exchange (KOSPI)",
    country="South Korea",
    region=ExchangeRegion.ASIA_PACIFIC,
    currency=Currency.KRW,
    timezone="Asia/Seoul",
    suffix=".KS",
    mic="XKOS",
    trading_hours="09:00-15:30",
)

KOSDAQ = Exchange(
    code="KOSDAQ",
    name="KOSDAQ",
    country="South Korea",
    region=ExchangeRegion.ASIA_PACIFIC,
    currency=Currency.KRW,
    timezone="Asia/Seoul",
    suffix=".KQ",
    mic="XKOS",
    trading_hours="09:00-15:30",
)

SINGAPORE = Exchange(
    code="SGX",
    name="Singapore Exchange",
    country="Singapore",
    region=ExchangeRegion.ASIA_PACIFIC,
    currency=Currency.SGD,
    timezone="Asia/Singapore",
    suffix=".SI",
    mic="XSES",
    trading_hours="09:00-17:00",
)

NSE_INDIA = Exchange(
    code="NSE",
    name="National Stock Exchange of India",
    country="India",
    region=ExchangeRegion.ASIA_PACIFIC,
    currency=Currency.INR,
    timezone="Asia/Kolkata",
    suffix=".NS",
    mic="XNSE",
    trading_hours="09:15-15:30",
)

BSE_INDIA = Exchange(
    code="BSE",
    name="Bombay Stock Exchange",
    country="India",
    region=ExchangeRegion.ASIA_PACIFIC,
    currency=Currency.INR,
    timezone="Asia/Kolkata",
    suffix=".BO",
    mic="XBOM",
    trading_hours="09:15-15:30",
)

THAILAND = Exchange(
    code="SET",
    name="Stock Exchange of Thailand",
    country="Thailand",
    region=ExchangeRegion.ASIA_PACIFIC,
    currency=Currency.USD,  # Often quoted in USD
    timezone="Asia/Bangkok",
    suffix=".BK",
    mic="XBKK",
    trading_hours="10:00-16:30",
)

INDONESIA = Exchange(
    code="IDX",
    name="Indonesia Stock Exchange",
    country="Indonesia",
    region=ExchangeRegion.ASIA_PACIFIC,
    currency=Currency.USD,
    timezone="Asia/Jakarta",
    suffix=".JK",
    mic="XIDX",
    trading_hours="09:00-16:00",
)

MALAYSIA = Exchange(
    code="KLSE",
    name="Bursa Malaysia",
    country="Malaysia",
    region=ExchangeRegion.ASIA_PACIFIC,
    currency=Currency.USD,
    timezone="Asia/Kuala_Lumpur",
    suffix=".KL",
    mic="XKLS",
    trading_hours="09:00-17:00",
)

PHILIPPINES = Exchange(
    code="PSE",
    name="Philippine Stock Exchange",
    country="Philippines",
    region=ExchangeRegion.ASIA_PACIFIC,
    currency=Currency.USD,
    timezone="Asia/Manila",
    suffix=".PS",
    mic="XPHS",
    trading_hours="09:30-15:30",
)

# ============================================================================
# OCEANIA EXCHANGES
# ============================================================================
ASX = Exchange(
    code="ASX",
    name="Australian Securities Exchange",
    country="Australia",
    region=ExchangeRegion.ASIA_PACIFIC,
    currency=Currency.AUD,
    timezone="Australia/Sydney",
    suffix=".AX",
    mic="XASX",
    trading_hours="10:00-16:00",
)

NZX = Exchange(
    code="NZX",
    name="New Zealand Exchange",
    country="New Zealand",
    region=ExchangeRegion.ASIA_PACIFIC,
    currency=Currency.NZD,
    timezone="Pacific/Auckland",
    suffix=".NZ",
    mic="XNZE",
    trading_hours="10:00-16:45",
)

# ============================================================================
# LATIN AMERICAN EXCHANGES
# ============================================================================
B3_BRAZIL = Exchange(
    code="B3",
    name="B3 (Brasil Bolsa Balcão)",
    country="Brazil",
    region=ExchangeRegion.LATIN_AMERICA,
    currency=Currency.BRL,
    timezone="America/Sao_Paulo",
    suffix=".SA",
    mic="BVMF",
    trading_hours="10:00-17:55",
)

BMV_MEXICO = Exchange(
    code="BMV",
    name="Bolsa Mexicana de Valores",
    country="Mexico",
    region=ExchangeRegion.LATIN_AMERICA,
    currency=Currency.MXN,
    timezone="America/Mexico_City",
    suffix=".MX",
    mic="XMEX",
    trading_hours="08:30-15:00",
)

BCBA_ARGENTINA = Exchange(
    code="BCBA",
    name="Buenos Aires Stock Exchange",
    country="Argentina",
    region=ExchangeRegion.LATIN_AMERICA,
    currency=Currency.ARS,
    timezone="America/Argentina/Buenos_Aires",
    suffix=".BA",
    mic="XBUE",
    trading_hours="11:00-17:00",
)

SANTIAGO = Exchange(
    code="BCS",
    name="Bolsa de Comercio de Santiago",
    country="Chile",
    region=ExchangeRegion.LATIN_AMERICA,
    currency=Currency.USD,  # Often quoted in USD
    timezone="America/Santiago",
    suffix=".SN",
    mic="XSGO",
    trading_hours="09:30-16:00",
)

LIMA = Exchange(
    code="BVL",
    name="Bolsa de Valores de Lima",
    country="Peru",
    region=ExchangeRegion.LATIN_AMERICA,
    currency=Currency.USD,
    timezone="America/Lima",
    suffix=".LM",
    mic="XLIM",
    trading_hours="09:00-16:00",
)

BOGOTA = Exchange(
    code="BVC",
    name="Bolsa de Valores de Colombia",
    country="Colombia",
    region=ExchangeRegion.LATIN_AMERICA,
    currency=Currency.USD,
    timezone="America/Bogota",
    suffix=".CL",
    mic="XBOG",
    trading_hours="09:30-16:00",
)

# ============================================================================
# MIDDLE EAST EXCHANGES
# ============================================================================
TEL_AVIV = Exchange(
    code="TASE",
    name="Tel Aviv Stock Exchange",
    country="Israel",
    region=ExchangeRegion.MIDDLE_EAST,
    currency=Currency.ILS,
    timezone="Asia/Jerusalem",
    suffix=".TA",
    mic="XTAE",
    trading_hours="09:00-17:25",
)

SAUDI = Exchange(
    code="TADAWUL",
    name="Saudi Stock Exchange (Tadawul)",
    country="Saudi Arabia",
    region=ExchangeRegion.MIDDLE_EAST,
    currency=Currency.SAR,
    timezone="Asia/Riyadh",
    suffix=".SR",
    mic="XSAU",
    trading_hours="10:00-15:00",
)

DUBAI = Exchange(
    code="DFM",
    name="Dubai Financial Market",
    country="UAE",
    region=ExchangeRegion.MIDDLE_EAST,
    currency=Currency.AED,
    timezone="Asia/Dubai",
    suffix=".DU",
    mic="XDFM",
    trading_hours="10:00-13:50",
)

ABU_DHABI = Exchange(
    code="ADX",
    name="Abu Dhabi Securities Exchange",
    country="UAE",
    region=ExchangeRegion.MIDDLE_EAST,
    currency=Currency.AED,
    timezone="Asia/Dubai",
    suffix=".AD",
    mic="XADS",
    trading_hours="10:00-13:50",
)

# ============================================================================
# AFRICAN EXCHANGES
# ============================================================================
JSE = Exchange(
    code="JSE",
    name="Johannesburg Stock Exchange",
    country="South Africa",
    region=ExchangeRegion.AFRICA,
    currency=Currency.ZAR,
    timezone="Africa/Johannesburg",
    suffix=".JO",
    mic="XJSE",
    trading_hours="09:00-17:00",
)


# ============================================================================
# EXCHANGE REGISTRY
# ============================================================================
ALL_EXCHANGES: Dict[str, Exchange] = {
    # United States
    "NYSE": NYSE,
    "NASDAQ": NASDAQ,
    "AMEX": AMEX,
    
    # Canada
    "TSX": TSX,
    "TSXV": TSXV,
    
    # Europe
    "LSE": LSE,
    "EPA": EURONEXT_PARIS,
    "AMS": EURONEXT_AMSTERDAM,
    "EBR": EURONEXT_BRUSSELS,
    "ELI": EURONEXT_LISBON,
    "FRA": FRANKFURT,
    "BIT": MILAN,
    "SWX": SWISS,
    "BME": MADRID,
    "VIE": VIENNA,
    "STO": STOCKHOLM,
    "OSL": OSLO,
    "CPH": COPENHAGEN,
    "HEL": HELSINKI,
    "WSE": WARSAW,
    "MOEX": MOSCOW,
    
    # Asia
    "SSE": SHANGHAI,
    "SZSE": SHENZHEN,
    "HKEX": HONG_KONG,
    "TSE": TOKYO,
    "TWSE": TAIWAN,
    "KRX": KOREA,
    "KOSDAQ": KOSDAQ,
    "SGX": SINGAPORE,
    "NSE": NSE_INDIA,
    "BSE": BSE_INDIA,
    "SET": THAILAND,
    "IDX": INDONESIA,
    "KLSE": MALAYSIA,
    "PSE": PHILIPPINES,
    
    # Oceania
    "ASX": ASX,
    "NZX": NZX,
    
    # Latin America
    "B3": B3_BRAZIL,
    "BMV": BMV_MEXICO,
    "BCBA": BCBA_ARGENTINA,
    "BCS": SANTIAGO,
    "BVL": LIMA,
    "BVC": BOGOTA,
    
    # Middle East
    "TASE": TEL_AVIV,
    "TADAWUL": SAUDI,
    "DFM": DUBAI,
    "ADX": ABU_DHABI,
    
    # Africa
    "JSE": JSE,
}


def get_exchange(code: str) -> Optional[Exchange]:
    """Get exchange by code."""
    return ALL_EXCHANGES.get(code.upper())


def get_exchanges_by_region(region: ExchangeRegion) -> List[Exchange]:
    """Get all exchanges in a region."""
    return [ex for ex in ALL_EXCHANGES.values() if ex.region == region]


def get_all_supported_exchanges() -> List[Exchange]:
    """Get all supported (tradeable) exchanges."""
    return [ex for ex in ALL_EXCHANGES.values() if ex.is_supported]


def format_symbol_for_exchange(symbol: str, exchange_code: str) -> str:
    """Format a symbol for a specific exchange."""
    exchange = get_exchange(exchange_code)
    if exchange:
        return exchange.format_symbol(symbol)
    return symbol


def detect_exchange_from_symbol(symbol: str) -> Optional[Exchange]:
    """Detect exchange from symbol suffix."""
    for exchange in ALL_EXCHANGES.values():
        if exchange.suffix and symbol.upper().endswith(exchange.suffix.upper()):
            return exchange
    # Default to US exchanges for symbols without suffix
    return NYSE


# Common stock indices for each exchange
MAJOR_INDICES = {
    # US
    "SPX": {"name": "S&P 500", "exchange": "NYSE", "symbol": "^GSPC"},
    "DJI": {"name": "Dow Jones Industrial Average", "exchange": "NYSE", "symbol": "^DJI"},
    "IXIC": {"name": "NASDAQ Composite", "exchange": "NASDAQ", "symbol": "^IXIC"},
    "NDX": {"name": "NASDAQ-100", "exchange": "NASDAQ", "symbol": "^NDX"},
    "RUT": {"name": "Russell 2000", "exchange": "NYSE", "symbol": "^RUT"},
    
    # Europe
    "FTSE": {"name": "FTSE 100", "exchange": "LSE", "symbol": "^FTSE"},
    "DAX": {"name": "DAX", "exchange": "FRA", "symbol": "^GDAXI"},
    "CAC": {"name": "CAC 40", "exchange": "EPA", "symbol": "^FCHI"},
    "STOXX50E": {"name": "Euro Stoxx 50", "exchange": "FRA", "symbol": "^STOXX50E"},
    "IBEX": {"name": "IBEX 35", "exchange": "BME", "symbol": "^IBEX"},
    "FTSEMIB": {"name": "FTSE MIB", "exchange": "BIT", "symbol": "FTSEMIB.MI"},
    "SMI": {"name": "Swiss Market Index", "exchange": "SWX", "symbol": "^SSMI"},
    
    # Asia
    "N225": {"name": "Nikkei 225", "exchange": "TSE", "symbol": "^N225"},
    "HSI": {"name": "Hang Seng Index", "exchange": "HKEX", "symbol": "^HSI"},
    "SHCOMP": {"name": "Shanghai Composite", "exchange": "SSE", "symbol": "000001.SS"},
    "SZCOMP": {"name": "Shenzhen Composite", "exchange": "SZSE", "symbol": "399001.SZ"},
    "TWII": {"name": "Taiwan Weighted", "exchange": "TWSE", "symbol": "^TWII"},
    "KOSPI": {"name": "KOSPI", "exchange": "KRX", "symbol": "^KS11"},
    "STI": {"name": "Straits Times Index", "exchange": "SGX", "symbol": "^STI"},
    "NIFTY50": {"name": "Nifty 50", "exchange": "NSE", "symbol": "^NSEI"},
    "SENSEX": {"name": "S&P BSE Sensex", "exchange": "BSE", "symbol": "^BSESN"},
    
    # Oceania
    "AXJO": {"name": "S&P/ASX 200", "exchange": "ASX", "symbol": "^AXJO"},
    
    # Americas
    "GSPTSE": {"name": "S&P/TSX Composite", "exchange": "TSX", "symbol": "^GSPTSE"},
    "BVSP": {"name": "Bovespa", "exchange": "B3", "symbol": "^BVSP"},
    "MXX": {"name": "IPC Mexico", "exchange": "BMV", "symbol": "^MXX"},
    "MERVAL": {"name": "MERVAL", "exchange": "BCBA", "symbol": "^MERV"},
}


# Number of listed stocks per exchange (approximate)
EXCHANGE_STOCK_COUNTS = {
    "NYSE": 2800,
    "NASDAQ": 3700,
    "AMEX": 200,
    "TSX": 1500,
    "TSXV": 1600,
    "LSE": 2000,
    "EPA": 800,
    "AMS": 200,
    "FRA": 3000,
    "BIT": 400,
    "SWX": 300,
    "BME": 500,
    "SSE": 2200,
    "SZSE": 2800,
    "HKEX": 2600,
    "TSE": 3900,
    "TWSE": 1700,
    "KRX": 2300,
    "SGX": 700,
    "NSE": 2000,
    "BSE": 5500,
    "ASX": 2200,
    "B3": 400,
    "BMV": 150,
    "BCBA": 100,
    "TASE": 500,
    "TADAWUL": 200,
    "JSE": 350,
}


def get_total_available_stocks() -> int:
    """Get approximate total number of stocks available across all exchanges."""
    return sum(EXCHANGE_STOCK_COUNTS.values())


# Logging total
logger.info(f"Global exchange configuration loaded: {len(ALL_EXCHANGES)} exchanges, ~{get_total_available_stocks():,} stocks available")


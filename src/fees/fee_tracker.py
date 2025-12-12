"""
Fee Tracker - Tracks all trading fees and expenses.
Supports multiple brokers with different fee structures.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, Dict, List
from enum import Enum

from loguru import logger


class FeeType(str, Enum):
    """Types of trading fees."""
    COMMISSION = "commission"  # Per-trade commission
    SPREAD = "spread"  # Bid-ask spread cost
    EXCHANGE = "exchange"  # Exchange fees
    REGULATORY = "regulatory"  # SEC/FINRA fees
    CLEARING = "clearing"  # Clearing fees
    DATA = "data"  # Market data fees
    PLATFORM = "platform"  # Platform fees
    MARGIN_INTEREST = "margin_interest"  # Margin borrowing interest
    CRYPTO_NETWORK = "crypto_network"  # Blockchain network fees
    OTHER = "other"


@dataclass
class BrokerFeeStructure:
    """Fee structure for a specific broker."""
    broker_name: str
    
    # Stock/ETF fees
    stock_commission_per_share: float = 0.0  # Per-share commission
    stock_commission_min: float = 0.0  # Minimum per trade
    stock_commission_max: float = 0.0  # Maximum per trade
    stock_commission_flat: float = 0.0  # Flat rate per trade
    
    # Options fees
    options_per_contract: float = 0.65  # Per-contract fee
    options_assignment_fee: float = 0.0
    options_exercise_fee: float = 0.0
    
    # Futures fees
    futures_per_contract: float = 2.25
    futures_exchange_fee: float = 1.50
    
    # Crypto fees
    crypto_maker_pct: float = 0.40  # Maker fee percentage
    crypto_taker_pct: float = 0.60  # Taker fee percentage
    crypto_spread_pct: float = 0.0  # Additional spread
    
    # Regulatory fees (applied to all US trades)
    sec_fee_per_million: float = 8.00  # SEC Transaction Fee
    finra_taf_per_share: float = 0.000119  # FINRA TAF (max $5.95)
    finra_taf_max: float = 5.95
    
    # Other fees
    margin_interest_rate: float = 0.0  # Annual rate
    monthly_data_fee: float = 0.0
    monthly_platform_fee: float = 0.0
    inactivity_fee: float = 0.0


# Pre-configured broker fee structures
BROKER_FEE_STRUCTURES = {
    "ibkr_pro": BrokerFeeStructure(
        broker_name="Interactive Brokers Pro",
        stock_commission_per_share=0.005,
        stock_commission_min=1.00,
        stock_commission_max=0.5,  # 0.5% of trade value
        options_per_contract=0.65,
        futures_per_contract=0.85,
        futures_exchange_fee=1.50,
        crypto_maker_pct=0.18,
        crypto_taker_pct=0.18,
        margin_interest_rate=6.83,
    ),
    "ibkr_lite": BrokerFeeStructure(
        broker_name="Interactive Brokers Lite",
        stock_commission_flat=0.0,  # Free stocks/ETFs
        options_per_contract=0.65,
        futures_per_contract=0.85,
        margin_interest_rate=6.83,
    ),
    "alpaca": BrokerFeeStructure(
        broker_name="Alpaca",
        stock_commission_flat=0.0,  # Free stocks/ETFs
        crypto_maker_pct=0.15,
        crypto_taker_pct=0.25,
    ),
    "schwab": BrokerFeeStructure(
        broker_name="Charles Schwab",
        stock_commission_flat=0.0,  # Free stocks/ETFs
        options_per_contract=0.65,
        futures_per_contract=2.25,
    ),
    "tradier": BrokerFeeStructure(
        broker_name="Tradier",
        stock_commission_flat=0.0,  # Free stocks/ETFs
        options_per_contract=0.35,
    ),
    "robinhood": BrokerFeeStructure(
        broker_name="Robinhood",
        stock_commission_flat=0.0,
        options_per_contract=0.0,  # Free options
        crypto_spread_pct=0.5,  # Hidden in spread
    ),
    "coinbase": BrokerFeeStructure(
        broker_name="Coinbase",
        crypto_maker_pct=0.40,
        crypto_taker_pct=0.60,
    ),
    "coinbase_pro": BrokerFeeStructure(
        broker_name="Coinbase Pro",
        crypto_maker_pct=0.04,
        crypto_taker_pct=0.06,
    ),
}


@dataclass
class TradeFee:
    """Record of a fee charged for a specific trade."""
    trade_id: str
    bot_id: Optional[str]
    timestamp: datetime
    symbol: str
    fee_type: FeeType
    amount: float
    broker: str
    trade_value: float
    quantity: float
    description: str = ""


@dataclass
class FeeReport:
    """Summary report of fees."""
    period_start: date
    period_end: date
    total_fees: float
    fee_breakdown: Dict[FeeType, float]
    fees_by_broker: Dict[str, float]
    fees_by_bot: Dict[str, float]
    trade_count: int
    avg_fee_per_trade: float
    fees_as_pct_of_volume: float
    fees_as_pct_of_portfolio: float
    total_trade_volume: float
    portfolio_value: float


class FeeTracker:
    """
    Tracks all trading fees and provides expense analytics.
    """
    
    def __init__(self, default_broker: str = "ibkr_pro"):
        self._fees: List[TradeFee] = []
        self._fee_structures: Dict[str, BrokerFeeStructure] = BROKER_FEE_STRUCTURES.copy()
        self._default_broker = default_broker
        self._portfolio_value = 100000.0  # Will be updated
        
    def set_portfolio_value(self, value: float) -> None:
        """Update the current portfolio value."""
        self._portfolio_value = value
        
    def add_broker_fee_structure(self, broker_id: str, structure: BrokerFeeStructure) -> None:
        """Add or update a broker fee structure."""
        self._fee_structures[broker_id] = structure
        
    def calculate_stock_fee(
        self,
        symbol: str,
        quantity: float,
        price: float,
        broker: Optional[str] = None,
        is_sell: bool = False,
    ) -> Dict[FeeType, float]:
        """
        Calculate fees for a stock/ETF trade.
        
        Returns dict of fee types and amounts.
        """
        broker = broker or self._default_broker
        structure = self._fee_structures.get(broker, self._fee_structures["ibkr_pro"])
        
        fees = {}
        trade_value = abs(quantity * price)
        
        # Commission
        if structure.stock_commission_flat > 0:
            fees[FeeType.COMMISSION] = structure.stock_commission_flat
        elif structure.stock_commission_per_share > 0:
            commission = abs(quantity) * structure.stock_commission_per_share
            commission = max(commission, structure.stock_commission_min)
            if structure.stock_commission_max > 0:
                max_fee = trade_value * (structure.stock_commission_max / 100)
                commission = min(commission, max_fee)
            fees[FeeType.COMMISSION] = commission
        
        # Regulatory fees (only on sells for SEC, all trades for FINRA)
        if is_sell:
            sec_fee = (trade_value / 1_000_000) * structure.sec_fee_per_million
            fees[FeeType.REGULATORY] = sec_fee
        
        # FINRA TAF (all trades)
        finra_fee = min(abs(quantity) * structure.finra_taf_per_share, structure.finra_taf_max)
        if FeeType.REGULATORY in fees:
            fees[FeeType.REGULATORY] += finra_fee
        else:
            fees[FeeType.REGULATORY] = finra_fee
            
        return fees
    
    def calculate_options_fee(
        self,
        contracts: int,
        price_per_contract: float,
        broker: Optional[str] = None,
        is_assignment: bool = False,
        is_exercise: bool = False,
    ) -> Dict[FeeType, float]:
        """Calculate fees for an options trade."""
        broker = broker or self._default_broker
        structure = self._fee_structures.get(broker, self._fee_structures["ibkr_pro"])
        
        fees = {}
        trade_value = abs(contracts * price_per_contract * 100)
        
        # Per-contract commission
        fees[FeeType.COMMISSION] = abs(contracts) * structure.options_per_contract
        
        # Assignment/exercise fees
        if is_assignment and structure.options_assignment_fee > 0:
            fees[FeeType.CLEARING] = structure.options_assignment_fee
        if is_exercise and structure.options_exercise_fee > 0:
            fees[FeeType.CLEARING] = structure.options_exercise_fee
            
        # Regulatory fees
        sec_fee = (trade_value / 1_000_000) * structure.sec_fee_per_million
        fees[FeeType.REGULATORY] = sec_fee
        
        return fees
    
    def calculate_futures_fee(
        self,
        contracts: int,
        broker: Optional[str] = None,
    ) -> Dict[FeeType, float]:
        """Calculate fees for a futures trade."""
        broker = broker or self._default_broker
        structure = self._fee_structures.get(broker, self._fee_structures["ibkr_pro"])
        
        fees = {}
        
        # Per-contract commission
        fees[FeeType.COMMISSION] = abs(contracts) * structure.futures_per_contract
        
        # Exchange fees
        fees[FeeType.EXCHANGE] = abs(contracts) * structure.futures_exchange_fee
        
        return fees
    
    def calculate_crypto_fee(
        self,
        symbol: str,
        quantity: float,
        price: float,
        broker: Optional[str] = None,
        is_maker: bool = False,
    ) -> Dict[FeeType, float]:
        """Calculate fees for a crypto trade."""
        broker = broker or "coinbase"
        structure = self._fee_structures.get(broker, self._fee_structures["coinbase"])
        
        fees = {}
        trade_value = abs(quantity * price)
        
        # Trading fee (maker vs taker)
        fee_pct = structure.crypto_maker_pct if is_maker else structure.crypto_taker_pct
        fees[FeeType.COMMISSION] = trade_value * (fee_pct / 100)
        
        # Spread cost (if applicable)
        if structure.crypto_spread_pct > 0:
            fees[FeeType.SPREAD] = trade_value * (structure.crypto_spread_pct / 100)
        
        return fees
    
    def record_trade_fee(
        self,
        trade_id: str,
        symbol: str,
        quantity: float,
        price: float,
        fees: Dict[FeeType, float],
        broker: str,
        bot_id: Optional[str] = None,
    ) -> List[TradeFee]:
        """Record fees for a completed trade."""
        trade_value = abs(quantity * price)
        recorded = []
        
        for fee_type, amount in fees.items():
            if amount > 0:
                fee = TradeFee(
                    trade_id=trade_id,
                    bot_id=bot_id,
                    timestamp=datetime.utcnow(),
                    symbol=symbol,
                    fee_type=fee_type,
                    amount=amount,
                    broker=broker,
                    trade_value=trade_value,
                    quantity=quantity,
                )
                self._fees.append(fee)
                recorded.append(fee)
        
        return recorded
    
    def get_total_fees(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        bot_id: Optional[str] = None,
        broker: Optional[str] = None,
    ) -> float:
        """Get total fees for a period."""
        fees = self._filter_fees(start_date, end_date, bot_id, broker)
        return sum(f.amount for f in fees)
    
    def get_fee_breakdown(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict[FeeType, float]:
        """Get breakdown by fee type."""
        fees = self._filter_fees(start_date, end_date)
        breakdown = {}
        for fee in fees:
            breakdown[fee.fee_type] = breakdown.get(fee.fee_type, 0) + fee.amount
        return breakdown
    
    def get_fees_by_broker(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict[str, float]:
        """Get breakdown by broker."""
        fees = self._filter_fees(start_date, end_date)
        by_broker = {}
        for fee in fees:
            by_broker[fee.broker] = by_broker.get(fee.broker, 0) + fee.amount
        return by_broker
    
    def get_fees_by_bot(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict[str, float]:
        """Get breakdown by bot."""
        fees = self._filter_fees(start_date, end_date)
        by_bot = {}
        for fee in fees:
            bot = fee.bot_id or "manual"
            by_bot[bot] = by_bot.get(bot, 0) + fee.amount
        return by_bot
    
    def generate_report(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> FeeReport:
        """Generate a comprehensive fee report."""
        if not start_date:
            start_date = date.today().replace(day=1)  # Start of month
        if not end_date:
            end_date = date.today()
            
        fees = self._filter_fees(start_date, end_date)
        
        total_fees = sum(f.amount for f in fees)
        total_volume = sum(f.trade_value for f in fees)
        trade_ids = set(f.trade_id for f in fees)
        trade_count = len(trade_ids)
        
        return FeeReport(
            period_start=start_date,
            period_end=end_date,
            total_fees=total_fees,
            fee_breakdown=self.get_fee_breakdown(start_date, end_date),
            fees_by_broker=self.get_fees_by_broker(start_date, end_date),
            fees_by_bot=self.get_fees_by_bot(start_date, end_date),
            trade_count=trade_count,
            avg_fee_per_trade=total_fees / trade_count if trade_count > 0 else 0,
            fees_as_pct_of_volume=(total_fees / total_volume * 100) if total_volume > 0 else 0,
            fees_as_pct_of_portfolio=(total_fees / self._portfolio_value * 100) if self._portfolio_value > 0 else 0,
            total_trade_volume=total_volume,
            portfolio_value=self._portfolio_value,
        )
    
    def _filter_fees(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        bot_id: Optional[str] = None,
        broker: Optional[str] = None,
    ) -> List[TradeFee]:
        """Filter fees by criteria."""
        result = self._fees
        
        if start_date:
            result = [f for f in result if f.timestamp.date() >= start_date]
        if end_date:
            result = [f for f in result if f.timestamp.date() <= end_date]
        if bot_id:
            result = [f for f in result if f.bot_id == bot_id]
        if broker:
            result = [f for f in result if f.broker == broker]
            
        return result
    
    def get_available_brokers(self) -> List[Dict]:
        """Get list of available brokers with fee info."""
        brokers = []
        for broker_id, structure in self._fee_structures.items():
            brokers.append({
                "id": broker_id,
                "name": structure.broker_name,
                "stock_commission": structure.stock_commission_flat or f"${structure.stock_commission_per_share}/share",
                "options_per_contract": structure.options_per_contract,
                "crypto_fee_pct": structure.crypto_taker_pct,
            })
        return brokers


# Global instance
_fee_tracker: Optional[FeeTracker] = None


def get_fee_tracker() -> FeeTracker:
    """Get or create the global fee tracker."""
    global _fee_tracker
    if _fee_tracker is None:
        _fee_tracker = FeeTracker()
    return _fee_tracker


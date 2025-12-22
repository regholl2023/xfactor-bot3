"""
Trading Compliance Manager.

Enforces FINRA, SEC, and IRS trading regulations to protect users from violations.

Regulations Covered:
1. Pattern Day Trader (PDT) Rule - FINRA Rule 4210
2. Good Faith Violations - Cash account settlement rules
3. Freeriding Violations - Cash account purchase violations
4. Day Trading Buying Power - Margin account limits
5. Wash Sale Rule - IRS tax regulation
6. Settlement Rules - T+1 (and upcoming T+0)

2025/2026 Proposed Changes:
- SEC considering T+0 settlement
- Enhanced monitoring requirements
"""

from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from enum import Enum
from typing import Optional, List, Dict, Any
from collections import defaultdict

from loguru import logger


class ViolationType(str, Enum):
    """Types of trading violations."""
    PDT_WARNING = "pdt_warning"  # Approaching PDT threshold
    PDT_VIOLATION = "pdt_violation"  # Would trigger PDT status
    GOOD_FAITH = "good_faith"  # Selling unsettled securities
    FREERIDING = "freeriding"  # Using unsettled proceeds
    MARGIN_CALL = "margin_call"  # Day trading buying power exceeded
    WASH_SALE = "wash_sale"  # Tax implication warning
    SETTLEMENT_RISK = "settlement_risk"  # Settlement date conflict


class AccountType(str, Enum):
    """Account types with different rules."""
    CASH = "cash"
    MARGIN = "margin"
    IRA = "ira"
    PAPER = "paper"  # No compliance needed


class ComplianceAction(str, Enum):
    """Actions to take for compliance issues."""
    ALLOW = "allow"  # No issue
    WARN = "warn"  # Show warning, allow proceed
    CONFIRM = "confirm"  # Require user confirmation
    BLOCK = "block"  # Block the trade
    STOP_DAY = "stop_day"  # Stop trading for the day


@dataclass
class DayTrade:
    """Record of a day trade (open and close same day)."""
    symbol: str
    trade_date: date
    buy_time: datetime
    sell_time: datetime
    quantity: float
    buy_price: float
    sell_price: float
    pnl: float = 0.0

    def __post_init__(self):
        self.pnl = (self.sell_price - self.buy_price) * self.quantity


@dataclass
class UnsettledPosition:
    """Track unsettled securities."""
    symbol: str
    quantity: float
    purchase_date: date
    settlement_date: date
    cost_basis: float
    
    @property
    def is_settled(self) -> bool:
        return date.today() >= self.settlement_date


@dataclass
class ComplianceViolation:
    """A compliance violation or warning."""
    type: ViolationType
    severity: str  # 'info', 'warning', 'critical'
    action: ComplianceAction
    title: str
    description: str
    regulation: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "severity": self.severity,
            "action": self.action.value,
            "title": self.title,
            "description": self.description,
            "regulation": self.regulation,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ComplianceCheckResult:
    """Result of a pre-trade compliance check."""
    allowed: bool
    action: ComplianceAction
    violations: List[ComplianceViolation] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    requires_confirmation: bool = False
    stop_trading: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "allowed": self.allowed,
            "action": self.action.value,
            "violations": [v.to_dict() for v in self.violations],
            "warnings": self.warnings,
            "requires_confirmation": self.requires_confirmation,
            "stop_trading": self.stop_trading,
        }


class ComplianceManager:
    """
    Manages trading compliance and regulatory requirements.
    
    Key Features:
    - Pattern Day Trader (PDT) tracking and prevention
    - Good Faith violation detection
    - Freeriding violation detection
    - Day trading buying power monitoring
    - Wash sale rule warnings
    - Settlement date tracking
    
    Usage:
        compliance = ComplianceManager(account_type='margin', equity=50000)
        result = compliance.check_order(symbol='AAPL', side='sell', quantity=100)
        if result.requires_confirmation:
            # Prompt user
            pass
    """
    
    # FINRA PDT Rule constants
    PDT_THRESHOLD = 4  # Number of day trades in 5 business days
    PDT_LOOKBACK_DAYS = 5  # Business days to look back
    PDT_EQUITY_MINIMUM = 25000.0  # Minimum equity requirement
    
    # Settlement rules (T+1 as of May 2024)
    STOCK_SETTLEMENT_DAYS = 1  # T+1
    OPTIONS_SETTLEMENT_DAYS = 1  # T+1
    
    # Cash account restrictions
    GOOD_FAITH_RESTRICTION_DAYS = 90
    FREERIDING_RESTRICTION_DAYS = 90
    
    # Wash sale rule
    WASH_SALE_WINDOW_DAYS = 30
    
    def __init__(
        self,
        account_type: str = "margin",
        equity: float = 0.0,
        buying_power: float = 0.0,
        day_trading_buying_power: float = 0.0,
        is_pattern_day_trader: bool = False,
    ):
        self.account_type = AccountType(account_type.lower())
        self.equity = equity
        self.buying_power = buying_power
        self.day_trading_buying_power = day_trading_buying_power
        self.is_pattern_day_trader = is_pattern_day_trader
        
        # Day trade tracking
        self._day_trades: List[DayTrade] = []
        self._today_day_trades = 0
        
        # Position tracking for intraday
        self._intraday_positions: Dict[str, Dict] = {}  # symbol -> {quantity, avg_price, open_time}
        
        # Unsettled positions (cash accounts)
        self._unsettled_positions: List[UnsettledPosition] = []
        
        # Trade history for wash sale detection
        self._trade_history: Dict[str, List[Dict]] = defaultdict(list)  # symbol -> trades
        
        # Violation history
        self._violations: List[ComplianceViolation] = []
        
        # Restrictions
        self._restricted_until: Optional[date] = None
        self._restriction_type: Optional[str] = None
        
        # Auto-stop flag
        self._trading_stopped = False
        self._stop_reason: Optional[str] = None
    
    def update_account(
        self,
        equity: Optional[float] = None,
        buying_power: Optional[float] = None,
        day_trading_buying_power: Optional[float] = None,
        is_pattern_day_trader: Optional[bool] = None,
    ) -> None:
        """Update account information."""
        if equity is not None:
            self.equity = equity
        if buying_power is not None:
            self.buying_power = buying_power
        if day_trading_buying_power is not None:
            self.day_trading_buying_power = day_trading_buying_power
        if is_pattern_day_trader is not None:
            self.is_pattern_day_trader = is_pattern_day_trader
    
    def record_trade(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        timestamp: Optional[datetime] = None,
    ) -> List[ComplianceViolation]:
        """
        Record a trade and check for violations.
        
        Args:
            symbol: Stock symbol
            side: 'buy' or 'sell'
            quantity: Number of shares
            price: Execution price
            timestamp: Trade time (defaults to now)
            
        Returns:
            List of any violations triggered
        """
        timestamp = timestamp or datetime.now()
        trade_date = timestamp.date()
        violations = []
        
        # Record in trade history for wash sale detection
        self._trade_history[symbol].append({
            "side": side,
            "quantity": quantity,
            "price": price,
            "timestamp": timestamp,
        })
        
        if side.lower() == "buy":
            # Track intraday position
            if symbol in self._intraday_positions:
                # Add to existing position
                pos = self._intraday_positions[symbol]
                total_qty = pos["quantity"] + quantity
                avg_price = (pos["quantity"] * pos["avg_price"] + quantity * price) / total_qty
                pos["quantity"] = total_qty
                pos["avg_price"] = avg_price
            else:
                self._intraday_positions[symbol] = {
                    "quantity": quantity,
                    "avg_price": price,
                    "open_time": timestamp,
                }
            
            # For cash accounts, track unsettled position
            if self.account_type == AccountType.CASH:
                settlement_date = self._calculate_settlement_date(trade_date)
                self._unsettled_positions.append(UnsettledPosition(
                    symbol=symbol,
                    quantity=quantity,
                    purchase_date=trade_date,
                    settlement_date=settlement_date,
                    cost_basis=quantity * price,
                ))
        
        elif side.lower() == "sell":
            # Check if this closes an intraday position (day trade)
            if symbol in self._intraday_positions:
                pos = self._intraday_positions[symbol]
                
                # If opened today, this is a day trade
                if pos["open_time"].date() == trade_date:
                    day_trade = DayTrade(
                        symbol=symbol,
                        trade_date=trade_date,
                        buy_time=pos["open_time"],
                        sell_time=timestamp,
                        quantity=min(quantity, pos["quantity"]),
                        buy_price=pos["avg_price"],
                        sell_price=price,
                    )
                    self._day_trades.append(day_trade)
                    self._today_day_trades += 1
                    
                    # Check PDT implications
                    pdt_check = self._check_pdt_after_trade()
                    if pdt_check:
                        violations.append(pdt_check)
                
                # Update or remove position
                remaining = pos["quantity"] - quantity
                if remaining <= 0:
                    del self._intraday_positions[symbol]
                else:
                    pos["quantity"] = remaining
            
            # Check wash sale
            wash_sale = self._check_wash_sale(symbol, side, quantity, price, timestamp)
            if wash_sale:
                violations.append(wash_sale)
        
        # Store violations
        self._violations.extend(violations)
        
        return violations
    
    def check_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        estimated_price: float,
        is_closing: bool = False,
    ) -> ComplianceCheckResult:
        """
        Pre-trade compliance check.
        
        Args:
            symbol: Stock symbol
            side: 'buy' or 'sell'
            quantity: Order quantity
            estimated_price: Estimated execution price
            is_closing: Whether this closes an existing position
            
        Returns:
            ComplianceCheckResult with violations and required actions
        """
        violations = []
        warnings = []
        
        # Paper trading has no compliance requirements
        if self.account_type == AccountType.PAPER:
            return ComplianceCheckResult(
                allowed=True,
                action=ComplianceAction.ALLOW,
            )
        
        # Check if trading is stopped
        if self._trading_stopped:
            violations.append(ComplianceViolation(
                type=ViolationType.PDT_VIOLATION,
                severity="critical",
                action=ComplianceAction.BLOCK,
                title="Trading Stopped",
                description=f"Trading has been stopped for today: {self._stop_reason}",
                regulation="Internal Risk Control",
            ))
            return ComplianceCheckResult(
                allowed=False,
                action=ComplianceAction.BLOCK,
                violations=violations,
                stop_trading=True,
            )
        
        # Check account restrictions
        if self._restricted_until and date.today() < self._restricted_until:
            violations.append(ComplianceViolation(
                type=ViolationType.FREERIDING if self._restriction_type == "freeriding" else ViolationType.GOOD_FAITH,
                severity="critical",
                action=ComplianceAction.BLOCK,
                title=f"Account Restricted",
                description=f"Account is restricted until {self._restricted_until} due to {self._restriction_type} violation.",
                regulation="FINRA Rule 4210 / Reg T",
                details={"restriction_ends": self._restricted_until.isoformat()},
            ))
            return ComplianceCheckResult(
                allowed=False,
                action=ComplianceAction.BLOCK,
                violations=violations,
            )
        
        # 1. Pattern Day Trader (PDT) Check
        pdt_violations = self._check_pdt_preorder(symbol, side, is_closing)
        violations.extend(pdt_violations)
        
        # 2. Good Faith Violation Check (Cash Accounts)
        if self.account_type == AccountType.CASH and side.lower() == "sell":
            gfv = self._check_good_faith(symbol, quantity)
            if gfv:
                violations.append(gfv)
        
        # 3. Freeriding Check (Cash Accounts)
        if self.account_type == AccountType.CASH and side.lower() == "buy":
            freeride = self._check_freeriding(quantity * estimated_price)
            if freeride:
                violations.append(freeride)
        
        # 4. Day Trading Buying Power Check (Margin Accounts)
        if self.account_type == AccountType.MARGIN and side.lower() == "buy":
            dtbp = self._check_day_trading_buying_power(quantity * estimated_price)
            if dtbp:
                violations.append(dtbp)
        
        # 5. Wash Sale Warning
        if side.lower() == "buy":
            wash_sale = self._check_wash_sale_preorder(symbol)
            if wash_sale:
                warnings.append(wash_sale)
        
        # Determine action based on violations
        if any(v.action == ComplianceAction.BLOCK for v in violations):
            return ComplianceCheckResult(
                allowed=False,
                action=ComplianceAction.BLOCK,
                violations=violations,
                warnings=warnings,
            )
        
        if any(v.action == ComplianceAction.STOP_DAY for v in violations):
            self._stop_trading("PDT threshold reached")
            return ComplianceCheckResult(
                allowed=False,
                action=ComplianceAction.STOP_DAY,
                violations=violations,
                warnings=warnings,
                stop_trading=True,
            )
        
        if any(v.action == ComplianceAction.CONFIRM for v in violations):
            return ComplianceCheckResult(
                allowed=True,
                action=ComplianceAction.CONFIRM,
                violations=violations,
                warnings=warnings,
                requires_confirmation=True,
            )
        
        if any(v.action == ComplianceAction.WARN for v in violations):
            return ComplianceCheckResult(
                allowed=True,
                action=ComplianceAction.WARN,
                violations=violations,
                warnings=warnings,
            )
        
        return ComplianceCheckResult(
            allowed=True,
            action=ComplianceAction.ALLOW,
            warnings=warnings,
        )
    
    def _check_pdt_preorder(
        self,
        symbol: str,
        side: str,
        is_closing: bool,
    ) -> List[ComplianceViolation]:
        """Check Pattern Day Trader rule before order."""
        violations = []
        
        # Only applies to margin accounts with < $25k equity
        if self.account_type != AccountType.MARGIN:
            return violations
        
        if self.equity >= self.PDT_EQUITY_MINIMUM:
            # Account meets PDT equity requirement
            return violations
        
        # Check if this would be a day trade
        is_potential_day_trade = False
        if side.lower() == "sell" and symbol in self._intraday_positions:
            pos = self._intraday_positions[symbol]
            if pos["open_time"].date() == date.today():
                is_potential_day_trade = True
        elif side.lower() == "buy" and is_closing:
            # Short covering same day
            is_potential_day_trade = True
        
        if not is_potential_day_trade:
            return violations
        
        # Count day trades in last 5 business days
        day_trades_count = self._count_recent_day_trades()
        
        if day_trades_count >= self.PDT_THRESHOLD:
            # Already PDT - block
            violations.append(ComplianceViolation(
                type=ViolationType.PDT_VIOLATION,
                severity="critical",
                action=ComplianceAction.BLOCK,
                title="Pattern Day Trader Threshold Exceeded",
                description=(
                    f"You have made {day_trades_count} day trades in the last 5 business days. "
                    f"FINRA rules require $25,000 minimum equity to continue day trading. "
                    f"Your equity: ${self.equity:,.2f}"
                ),
                regulation="FINRA Rule 4210 (Pattern Day Trader)",
                details={
                    "day_trades_count": day_trades_count,
                    "threshold": self.PDT_THRESHOLD,
                    "equity": self.equity,
                    "required_equity": self.PDT_EQUITY_MINIMUM,
                },
            ))
        elif day_trades_count == self.PDT_THRESHOLD - 1:
            # One more day trade will trigger PDT - require confirmation
            violations.append(ComplianceViolation(
                type=ViolationType.PDT_WARNING,
                severity="warning",
                action=ComplianceAction.CONFIRM,
                title="PDT Warning: Final Day Trade",
                description=(
                    f"This would be your {day_trades_count + 1}th day trade in 5 business days. "
                    f"Proceeding will flag your account as a Pattern Day Trader, requiring "
                    f"$25,000 minimum equity. Your equity: ${self.equity:,.2f}"
                ),
                regulation="FINRA Rule 4210 (Pattern Day Trader)",
                details={
                    "day_trades_count": day_trades_count,
                    "after_trade": day_trades_count + 1,
                    "threshold": self.PDT_THRESHOLD,
                    "equity": self.equity,
                },
            ))
        elif day_trades_count >= 2:
            # Warning - getting close
            remaining = self.PDT_THRESHOLD - day_trades_count - 1
            violations.append(ComplianceViolation(
                type=ViolationType.PDT_WARNING,
                severity="info",
                action=ComplianceAction.WARN,
                title=f"PDT Alert: {remaining} Day Trade(s) Remaining",
                description=(
                    f"You have made {day_trades_count} day trades in the last 5 business days. "
                    f"You have {remaining} day trade(s) remaining before triggering PDT rules."
                ),
                regulation="FINRA Rule 4210 (Pattern Day Trader)",
                details={
                    "day_trades_count": day_trades_count,
                    "remaining": remaining,
                    "threshold": self.PDT_THRESHOLD,
                },
            ))
        
        return violations
    
    def _check_pdt_after_trade(self) -> Optional[ComplianceViolation]:
        """Check PDT status after a day trade is recorded."""
        if self.account_type != AccountType.MARGIN:
            return None
        
        if self.equity >= self.PDT_EQUITY_MINIMUM:
            return None
        
        day_trades_count = self._count_recent_day_trades()
        
        if day_trades_count >= self.PDT_THRESHOLD:
            self.is_pattern_day_trader = True
            return ComplianceViolation(
                type=ViolationType.PDT_VIOLATION,
                severity="critical",
                action=ComplianceAction.STOP_DAY,
                title="Pattern Day Trader Status Triggered",
                description=(
                    f"You have been flagged as a Pattern Day Trader ({day_trades_count} day trades "
                    f"in 5 business days). Trading is stopped for today. You must maintain "
                    f"$25,000 minimum equity to continue day trading."
                ),
                regulation="FINRA Rule 4210",
                details={
                    "day_trades_count": day_trades_count,
                    "equity": self.equity,
                    "required_equity": self.PDT_EQUITY_MINIMUM,
                },
            )
        
        return None
    
    def _check_good_faith(
        self,
        symbol: str,
        quantity: float,
    ) -> Optional[ComplianceViolation]:
        """Check for Good Faith Violation (selling unsettled securities)."""
        # Find unsettled positions for this symbol
        unsettled = [
            p for p in self._unsettled_positions
            if p.symbol == symbol and not p.is_settled
        ]
        
        if not unsettled:
            return None
        
        unsettled_qty = sum(p.quantity for p in unsettled)
        
        if quantity > unsettled_qty:
            # Selling more than unsettled - check if we have settled shares
            return None
        
        # Selling unsettled securities
        return ComplianceViolation(
            type=ViolationType.GOOD_FAITH,
            severity="warning",
            action=ComplianceAction.CONFIRM,
            title="Good Faith Violation Warning",
            description=(
                f"You are attempting to sell {quantity} shares of {symbol} that have not "
                f"settled yet. Selling securities before settlement (T+{self.STOCK_SETTLEMENT_DAYS}) "
                f"may result in a Good Faith Violation. Three violations in 12 months will "
                f"result in a 90-day cash-upfront restriction."
            ),
            regulation="Regulation T / FINRA",
            details={
                "symbol": symbol,
                "quantity": quantity,
                "unsettled_quantity": unsettled_qty,
                "settlement_dates": [p.settlement_date.isoformat() for p in unsettled],
            },
        )
    
    def _check_freeriding(self, order_value: float) -> Optional[ComplianceViolation]:
        """Check for Freeriding Violation (buying with unsettled proceeds)."""
        # Calculate unsettled proceeds from recent sales
        unsettled_proceeds = self._calculate_unsettled_proceeds()
        
        if unsettled_proceeds <= 0:
            return None
        
        # Check if buying power relies on unsettled funds
        settled_buying_power = self.buying_power - unsettled_proceeds
        
        if order_value > settled_buying_power and order_value <= self.buying_power:
            return ComplianceViolation(
                type=ViolationType.FREERIDING,
                severity="warning",
                action=ComplianceAction.CONFIRM,
                title="Freeriding Risk Warning",
                description=(
                    f"This purchase of ${order_value:,.2f} uses unsettled proceeds from recent sales. "
                    f"If you sell this position before your sale proceeds settle (T+{self.STOCK_SETTLEMENT_DAYS}), "
                    f"you may incur a Freeriding Violation, resulting in a 90-day restriction."
                ),
                regulation="Regulation T",
                details={
                    "order_value": order_value,
                    "unsettled_proceeds": unsettled_proceeds,
                    "settled_buying_power": max(0, settled_buying_power),
                },
            )
        
        return None
    
    def _check_day_trading_buying_power(
        self,
        order_value: float,
    ) -> Optional[ComplianceViolation]:
        """Check Day Trading Buying Power limits (margin accounts)."""
        if not self.is_pattern_day_trader:
            return None
        
        if self.day_trading_buying_power <= 0:
            return None
        
        # Calculate used DTBP today
        used_dtbp = self._calculate_used_dtbp()
        remaining_dtbp = self.day_trading_buying_power - used_dtbp
        
        if order_value > remaining_dtbp:
            return ComplianceViolation(
                type=ViolationType.MARGIN_CALL,
                severity="critical",
                action=ComplianceAction.BLOCK,
                title="Day Trading Buying Power Exceeded",
                description=(
                    f"This order of ${order_value:,.2f} exceeds your remaining Day Trading "
                    f"Buying Power of ${remaining_dtbp:,.2f}. Exceeding DTBP will result in "
                    f"a margin call requiring immediate deposit."
                ),
                regulation="FINRA Margin Rules",
                details={
                    "order_value": order_value,
                    "day_trading_buying_power": self.day_trading_buying_power,
                    "used_dtbp": used_dtbp,
                    "remaining_dtbp": remaining_dtbp,
                },
            )
        
        return None
    
    def _check_wash_sale(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        timestamp: datetime,
    ) -> Optional[ComplianceViolation]:
        """Check for Wash Sale after a loss sale."""
        if side.lower() != "sell":
            return None
        
        # Get recent trades for this symbol
        recent_trades = self._trade_history.get(symbol, [])
        
        # Check for recent buys (within wash sale window before this sell)
        window_start = timestamp - timedelta(days=self.WASH_SALE_WINDOW_DAYS)
        recent_buys = [
            t for t in recent_trades
            if t["side"].lower() == "buy" and t["timestamp"] >= window_start
        ]
        
        if not recent_buys:
            return None
        
        # Check if this sell is at a loss
        avg_buy_price = sum(t["price"] * t["quantity"] for t in recent_buys) / sum(t["quantity"] for t in recent_buys)
        
        if price >= avg_buy_price:
            return None  # Not a loss sale
        
        return ComplianceViolation(
            type=ViolationType.WASH_SALE,
            severity="info",
            action=ComplianceAction.WARN,
            title="Potential Wash Sale",
            description=(
                f"You sold {symbol} at a loss within 30 days of purchasing. If you "
                f"repurchase {symbol} (or substantially identical security) within the "
                f"next 30 days, this loss may be disallowed for tax purposes (Wash Sale Rule)."
            ),
            regulation="IRS Wash Sale Rule (Section 1091)",
            details={
                "symbol": symbol,
                "sale_price": price,
                "avg_buy_price": avg_buy_price,
                "loss_per_share": avg_buy_price - price,
                "wash_sale_window_ends": (timestamp + timedelta(days=30)).date().isoformat(),
            },
        )
    
    def _check_wash_sale_preorder(self, symbol: str) -> Optional[str]:
        """Check if buying would trigger wash sale on previous loss."""
        # Look for recent loss sales
        recent_trades = self._trade_history.get(symbol, [])
        window_start = datetime.now() - timedelta(days=self.WASH_SALE_WINDOW_DAYS)
        
        recent_sells = [
            t for t in recent_trades
            if t["side"].lower() == "sell" and t["timestamp"] >= window_start
        ]
        
        if recent_sells:
            return (
                f"Buying {symbol} may trigger wash sale rule if you sold at a loss "
                f"in the last 30 days. The loss may be disallowed for tax purposes."
            )
        
        return None
    
    def _count_recent_day_trades(self) -> int:
        """Count day trades in the last 5 business days."""
        today = date.today()
        cutoff = today - timedelta(days=7)  # Extra days to account for weekends
        
        # Get business days
        business_days = []
        current = today
        while len(business_days) < self.PDT_LOOKBACK_DAYS:
            if current.weekday() < 5:  # Monday = 0, Friday = 4
                business_days.append(current)
            current -= timedelta(days=1)
        
        oldest_date = business_days[-1] if business_days else cutoff
        
        return sum(
            1 for dt in self._day_trades
            if dt.trade_date >= oldest_date
        )
    
    def _calculate_settlement_date(self, trade_date: date) -> date:
        """Calculate settlement date (T+1)."""
        settlement = trade_date + timedelta(days=self.STOCK_SETTLEMENT_DAYS)
        
        # Skip weekends
        while settlement.weekday() >= 5:
            settlement += timedelta(days=1)
        
        return settlement
    
    def _calculate_unsettled_proceeds(self) -> float:
        """Calculate total unsettled proceeds from recent sales."""
        # This would need actual sale tracking in production
        # For now, return 0 as a placeholder
        return 0.0
    
    def _calculate_used_dtbp(self) -> float:
        """Calculate used Day Trading Buying Power today."""
        today = date.today()
        today_trades = [
            dt for dt in self._day_trades
            if dt.trade_date == today
        ]
        
        return sum(dt.buy_price * dt.quantity for dt in today_trades)
    
    def _stop_trading(self, reason: str) -> None:
        """Stop all trading for the day."""
        self._trading_stopped = True
        self._stop_reason = reason
        logger.warning(f"Trading stopped: {reason}")
    
    def reset_daily(self) -> None:
        """Reset daily counters (call at market open)."""
        self._trading_stopped = False
        self._stop_reason = None
        self._today_day_trades = 0
        self._intraday_positions.clear()
        
        # Clean up old unsettled positions
        self._unsettled_positions = [
            p for p in self._unsettled_positions
            if not p.is_settled
        ]
        
        # Clean up old day trades (keep last 7 days)
        cutoff = date.today() - timedelta(days=7)
        self._day_trades = [
            dt for dt in self._day_trades
            if dt.trade_date >= cutoff
        ]
        
        # Clean up old trade history (keep last 60 days for wash sale)
        history_cutoff = datetime.now() - timedelta(days=60)
        for symbol in self._trade_history:
            self._trade_history[symbol] = [
                t for t in self._trade_history[symbol]
                if t["timestamp"] >= history_cutoff
            ]
    
    def get_status(self) -> Dict[str, Any]:
        """Get current compliance status."""
        day_trades_count = self._count_recent_day_trades()
        remaining_day_trades = max(0, self.PDT_THRESHOLD - day_trades_count - 1) if self.equity < self.PDT_EQUITY_MINIMUM else None
        
        return {
            "account_type": self.account_type.value,
            "equity": self.equity,
            "pdt_status": {
                "is_pattern_day_trader": self.is_pattern_day_trader,
                "day_trades_last_5_days": day_trades_count,
                "remaining_day_trades": remaining_day_trades,
                "pdt_threshold": self.PDT_THRESHOLD,
                "equity_requirement": self.PDT_EQUITY_MINIMUM,
                "meets_equity_requirement": self.equity >= self.PDT_EQUITY_MINIMUM,
            },
            "trading_status": {
                "trading_allowed": not self._trading_stopped,
                "stop_reason": self._stop_reason,
            },
            "restrictions": {
                "restricted": self._restricted_until is not None and date.today() < self._restricted_until,
                "restriction_type": self._restriction_type,
                "restriction_ends": self._restricted_until.isoformat() if self._restricted_until else None,
            },
            "settlement": {
                "settlement_days": self.STOCK_SETTLEMENT_DAYS,
                "unsettled_positions": len([p for p in self._unsettled_positions if not p.is_settled]),
            },
            "recent_violations": [v.to_dict() for v in self._violations[-10:]],
        }
    
    def get_day_trades(self) -> List[Dict[str, Any]]:
        """Get recent day trades."""
        return [
            {
                "symbol": dt.symbol,
                "trade_date": dt.trade_date.isoformat(),
                "quantity": dt.quantity,
                "buy_price": dt.buy_price,
                "sell_price": dt.sell_price,
                "pnl": dt.pnl,
            }
            for dt in self._day_trades
        ]


# Singleton instance
_compliance_manager: Optional[ComplianceManager] = None


def get_compliance_manager() -> ComplianceManager:
    """Get or create the compliance manager singleton."""
    global _compliance_manager
    if _compliance_manager is None:
        _compliance_manager = ComplianceManager()
    return _compliance_manager


def reset_compliance_manager() -> None:
    """Reset the compliance manager (for testing)."""
    global _compliance_manager
    _compliance_manager = None


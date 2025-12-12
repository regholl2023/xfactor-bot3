"""
API routes for managing broker and data source integrations.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from loguru import logger

from src.brokers import BrokerType, get_broker_registry
from src.data_sources import DataSourceType, get_data_registry
from src.banking import get_plaid_client


router = APIRouter()


# =========================================================================
# Request/Response Models
# =========================================================================

class BrokerConnectRequest(BaseModel):
    """Request to connect a broker."""
    broker_type: str
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    account_id: Optional[str] = None
    paper: bool = True
    # Additional config can be passed
    config: Dict[str, Any] = {}


class DataSourceConnectRequest(BaseModel):
    """Request to connect a data source."""
    source_type: str
    api_key: str = ""
    config: Dict[str, Any] = {}


class PlaidLinkRequest(BaseModel):
    """Request for Plaid link token."""
    user_id: str
    redirect_uri: Optional[str] = None


class PlaidExchangeRequest(BaseModel):
    """Request to exchange Plaid public token."""
    public_token: str


class TransferRequest(BaseModel):
    """Bank transfer request."""
    bank_account_id: str
    brokerage_account_id: str
    broker_name: str
    amount: float
    direction: str  # "deposit" or "withdraw"
    description: str = ""


# =========================================================================
# Broker Routes
# =========================================================================

@router.get("/brokers")
async def get_brokers() -> Dict[str, Any]:
    """Get all available and connected brokers."""
    registry = get_broker_registry()
    return {
        "available": [b.value for b in BrokerType],
        "connected": registry.to_dict(),
    }


@router.post("/brokers/connect")
async def connect_broker(request: BrokerConnectRequest) -> Dict[str, Any]:
    """Connect to a broker."""
    registry = get_broker_registry()
    
    try:
        broker_type = BrokerType(request.broker_type.lower())
    except ValueError:
        raise HTTPException(400, f"Unknown broker type: {request.broker_type}")
    
    config = {
        "api_key": request.api_key,
        "secret_key": request.secret_key,
        "account_id": request.account_id,
        "paper": request.paper,
        **request.config
    }
    
    success = await registry.connect_broker(broker_type, **config)
    
    if success:
        return {"status": "connected", "broker": broker_type.value}
    else:
        raise HTTPException(500, f"Failed to connect to {broker_type.value}")


@router.post("/brokers/disconnect/{broker_type}")
async def disconnect_broker(broker_type: str) -> Dict[str, Any]:
    """Disconnect from a broker."""
    registry = get_broker_registry()
    
    try:
        bt = BrokerType(broker_type.lower())
    except ValueError:
        raise HTTPException(400, f"Unknown broker type: {broker_type}")
    
    await registry.disconnect_broker(bt)
    return {"status": "disconnected", "broker": broker_type}


@router.get("/brokers/{broker_type}/accounts")
async def get_broker_accounts(broker_type: str) -> Dict[str, Any]:
    """Get accounts for a connected broker."""
    registry = get_broker_registry()
    
    try:
        bt = BrokerType(broker_type.lower())
    except ValueError:
        raise HTTPException(400, f"Unknown broker type: {broker_type}")
    
    broker = registry.get_broker(bt)
    if not broker:
        raise HTTPException(404, f"Broker not connected: {broker_type}")
    
    accounts = await broker.get_accounts()
    return {
        "broker": broker_type,
        "accounts": [
            {
                "account_id": a.account_id,
                "type": a.account_type,
                "buying_power": a.buying_power,
                "portfolio_value": a.portfolio_value,
                "cash": a.cash,
            }
            for a in accounts
        ]
    }


@router.get("/brokers/portfolio")
async def get_total_portfolio() -> Dict[str, Any]:
    """Get aggregated portfolio across all brokers."""
    registry = get_broker_registry()
    
    total_value = await registry.get_total_portfolio_value()
    total_buying_power = await registry.get_total_buying_power()
    all_accounts = await registry.get_all_accounts()
    
    return {
        "total_portfolio_value": total_value,
        "total_buying_power": total_buying_power,
        "by_broker": {
            bt.value: [
                {
                    "account_id": a.account_id,
                    "portfolio_value": a.portfolio_value,
                    "buying_power": a.buying_power,
                }
                for a in accounts
            ]
            for bt, accounts in all_accounts.items()
        }
    }


# =========================================================================
# Data Source Routes
# =========================================================================

@router.get("/data-sources")
async def get_data_sources() -> Dict[str, Any]:
    """Get available and connected data sources."""
    registry = get_data_registry()
    return {
        "available": [s.value for s in DataSourceType],
        "connected": registry.to_dict(),
    }


@router.post("/data-sources/connect")
async def connect_data_source(request: DataSourceConnectRequest) -> Dict[str, Any]:
    """Connect to a data source."""
    registry = get_data_registry()
    
    try:
        source_type = DataSourceType(request.source_type.lower())
    except ValueError:
        raise HTTPException(400, f"Unknown data source: {request.source_type}")
    
    config = {"api_key": request.api_key, **request.config}
    success = await registry.connect_source(source_type, **config)
    
    if success:
        return {"status": "connected", "source": source_type.value}
    else:
        raise HTTPException(500, f"Failed to connect to {source_type.value}")


@router.get("/data-sources/quote/{symbol}")
async def get_quote(symbol: str, source: Optional[str] = None) -> Dict[str, Any]:
    """Get quote for a symbol."""
    registry = get_data_registry()
    
    source_type = None
    if source:
        try:
            source_type = DataSourceType(source.lower())
        except ValueError:
            raise HTTPException(400, f"Unknown data source: {source}")
    
    quote = await registry.get_quote(symbol.upper(), source_type)
    
    if quote:
        return {
            "symbol": quote.symbol,
            "bid": quote.bid,
            "ask": quote.ask,
            "last": quote.last,
            "volume": quote.volume,
            "source": quote.source.value,
            "timestamp": quote.timestamp.isoformat(),
        }
    else:
        raise HTTPException(404, f"No quote available for {symbol}")


# =========================================================================
# Banking Routes (Plaid)
# =========================================================================

@router.get("/banking/status")
async def get_banking_status() -> Dict[str, Any]:
    """Get Plaid banking integration status."""
    client = get_plaid_client()
    return client.to_dict()


@router.post("/banking/link-token")
async def create_link_token(request: PlaidLinkRequest) -> Dict[str, Any]:
    """Create Plaid Link token for frontend."""
    client = get_plaid_client()
    
    if not await client.initialize():
        raise HTTPException(500, "Plaid not configured")
    
    token = await client.create_link_token(
        user_id=request.user_id,
        redirect_uri=request.redirect_uri
    )
    
    if token:
        return {"link_token": token}
    else:
        raise HTTPException(500, "Failed to create link token")


@router.post("/banking/exchange-token")
async def exchange_public_token(request: PlaidExchangeRequest) -> Dict[str, Any]:
    """Exchange Plaid public token for access token."""
    client = get_plaid_client()
    
    access_token = await client.exchange_public_token(request.public_token)
    
    if access_token:
        accounts = await client.get_linked_accounts()
        return {
            "status": "linked",
            "accounts": [
                {
                    "account_id": a.account_id,
                    "institution": a.institution_name,
                    "name": a.account_name,
                    "type": a.account_type,
                    "mask": a.account_mask,
                }
                for a in accounts
            ]
        }
    else:
        raise HTTPException(500, "Failed to exchange token")


@router.get("/banking/accounts")
async def get_linked_bank_accounts() -> Dict[str, Any]:
    """Get all linked bank accounts."""
    client = get_plaid_client()
    accounts = await client.get_linked_accounts()
    
    return {
        "accounts": [
            {
                "account_id": a.account_id,
                "institution": a.institution_name,
                "name": a.account_name,
                "type": a.account_type,
                "mask": a.account_mask,
                "available_balance": a.available_balance,
                "current_balance": a.current_balance,
                "verified": a.verified,
            }
            for a in accounts
        ]
    }


@router.post("/banking/transfer")
async def initiate_transfer(request: TransferRequest) -> Dict[str, Any]:
    """Initiate a bank transfer."""
    from src.banking.plaid_client import TransferDirection
    
    client = get_plaid_client()
    
    try:
        direction = TransferDirection(request.direction.lower())
    except ValueError:
        raise HTTPException(400, "Direction must be 'deposit' or 'withdraw'")
    
    transfer = await client.initiate_transfer(
        account_id=request.bank_account_id,
        amount=request.amount,
        direction=direction,
        brokerage_account_id=request.brokerage_account_id,
        broker_name=request.broker_name,
        description=request.description
    )
    
    if transfer:
        return {
            "transfer_id": transfer.transfer_id,
            "status": transfer.status.value,
            "amount": transfer.amount,
            "direction": transfer.direction.value,
        }
    else:
        raise HTTPException(500, "Failed to initiate transfer")


# =========================================================================
# TradingView Webhook
# =========================================================================

@router.post("/webhooks/tradingview")
async def tradingview_webhook(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle TradingView webhook alerts."""
    from src.data_sources.tradingview import get_tradingview_webhook
    
    webhook = get_tradingview_webhook()
    alert = await webhook.handle_webhook(data)
    
    if alert:
        return {
            "status": "received",
            "action": alert.action.value,
            "symbol": alert.symbol,
            "price": alert.price,
        }
    else:
        raise HTTPException(400, "Invalid webhook payload")


@router.get("/webhooks/tradingview/alerts")
async def get_tradingview_alerts(
    limit: int = 50,
    symbol: Optional[str] = None
) -> Dict[str, Any]:
    """Get recent TradingView alerts."""
    from src.data_sources.tradingview import get_tradingview_webhook
    
    webhook = get_tradingview_webhook()
    alerts = webhook.get_recent_alerts(limit=limit, symbol=symbol)
    
    return {
        "alerts": [
            {
                "action": a.action.value,
                "symbol": a.symbol,
                "price": a.price,
                "strategy": a.strategy,
                "timestamp": a.timestamp.isoformat(),
            }
            for a in alerts
        ]
    }


"""
Plaid Banking Integration.

Plaid provides secure bank account linking for:
- ACH transfers to/from brokerage accounts
- Account balance verification
- Identity verification
- Transaction history

This integration allows users to:
1. Link bank accounts securely
2. Initiate transfers to fund trading accounts
3. Withdraw profits to bank accounts
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any

from loguru import logger


class TransferDirection(str, Enum):
    """Transfer direction."""
    DEPOSIT = "deposit"      # Bank -> Brokerage
    WITHDRAW = "withdraw"    # Brokerage -> Bank


class TransferStatus(str, Enum):
    """Transfer status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class LinkedBankAccount:
    """Linked bank account information."""
    account_id: str
    institution_name: str
    account_name: str
    account_type: str  # checking, savings
    account_mask: str  # Last 4 digits
    available_balance: Optional[float] = None
    current_balance: Optional[float] = None
    currency: str = "USD"
    verified: bool = False
    linked_at: datetime = None
    
    def __post_init__(self):
        if self.linked_at is None:
            self.linked_at = datetime.now()


@dataclass
class Transfer:
    """Bank transfer record."""
    transfer_id: str
    direction: TransferDirection
    amount: float
    status: TransferStatus
    bank_account_id: str
    brokerage_account_id: str
    broker_name: str
    description: str = ""
    created_at: datetime = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class PlaidBankingClient:
    """
    Plaid client for bank account linking and transfers.
    
    Plaid Flow:
    1. Create link token (for Plaid Link UI)
    2. User completes Plaid Link
    3. Exchange public token for access token
    4. Use access token to get account info
    5. Create processor token for broker integration
    
    Environment variables needed:
    - PLAID_CLIENT_ID
    - PLAID_SECRET
    - PLAID_ENV (sandbox/development/production)
    """
    
    PLAID_ENVS = {
        "sandbox": "https://sandbox.plaid.com",
        "development": "https://development.plaid.com",
        "production": "https://production.plaid.com",
    }
    
    def __init__(
        self,
        client_id: str = "",
        secret: str = "",
        environment: str = "sandbox"
    ):
        self.client_id = client_id
        self.secret = secret
        self.environment = environment
        self.base_url = self.PLAID_ENVS.get(environment, self.PLAID_ENVS["sandbox"])
        self._client = None
        self._linked_accounts: Dict[str, LinkedBankAccount] = {}
        self._access_tokens: Dict[str, str] = {}  # account_id -> access_token
    
    async def initialize(self) -> bool:
        """Initialize Plaid client."""
        try:
            import plaid
            from plaid.api import plaid_api
            from plaid.model.country_code import CountryCode
            from plaid.model.products import Products
            
            configuration = plaid.Configuration(
                host=self._get_plaid_host(),
                api_key={
                    'clientId': self.client_id,
                    'secret': self.secret,
                }
            )
            
            api_client = plaid.ApiClient(configuration)
            self._client = plaid_api.PlaidApi(api_client)
            
            logger.info(f"Plaid client initialized ({self.environment})")
            return True
            
        except ImportError:
            logger.warning("plaid-python not installed. Run: pip install plaid-python")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Plaid: {e}")
            return False
    
    def _get_plaid_host(self) -> str:
        """Get Plaid host based on environment."""
        import plaid
        env_map = {
            "sandbox": plaid.Environment.Sandbox,
            "development": plaid.Environment.Development,
            "production": plaid.Environment.Production,
        }
        return env_map.get(self.environment, plaid.Environment.Sandbox)
    
    async def create_link_token(
        self,
        user_id: str,
        redirect_uri: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a Plaid Link token for the frontend.
        
        Args:
            user_id: Unique user identifier
            redirect_uri: OAuth redirect URI (for OAuth institutions)
            
        Returns:
            Link token for Plaid Link initialization
        """
        if not self._client:
            await self.initialize()
        
        try:
            from plaid.model.link_token_create_request import LinkTokenCreateRequest
            from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
            from plaid.model.country_code import CountryCode
            from plaid.model.products import Products
            
            request = LinkTokenCreateRequest(
                products=[Products("auth"), Products("transactions")],
                client_name="XFactor Bot",
                country_codes=[CountryCode("US")],
                language="en",
                user=LinkTokenCreateRequestUser(client_user_id=user_id),
            )
            
            if redirect_uri:
                request.redirect_uri = redirect_uri
            
            response = self._client.link_token_create(request)
            return response.link_token
            
        except Exception as e:
            logger.error(f"Failed to create link token: {e}")
            return None
    
    async def exchange_public_token(
        self,
        public_token: str
    ) -> Optional[str]:
        """
        Exchange public token from Plaid Link for access token.
        
        Args:
            public_token: Token received from Plaid Link
            
        Returns:
            Access token for API calls
        """
        if not self._client:
            return None
        
        try:
            from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
            
            request = ItemPublicTokenExchangeRequest(public_token=public_token)
            response = self._client.item_public_token_exchange(request)
            
            access_token = response.access_token
            item_id = response.item_id
            
            # Get account info
            await self._fetch_accounts(access_token)
            
            logger.info(f"Successfully linked bank account (item: {item_id})")
            return access_token
            
        except Exception as e:
            logger.error(f"Failed to exchange public token: {e}")
            return None
    
    async def _fetch_accounts(self, access_token: str) -> List[LinkedBankAccount]:
        """Fetch accounts for an access token."""
        try:
            from plaid.model.accounts_get_request import AccountsGetRequest
            
            request = AccountsGetRequest(access_token=access_token)
            response = self._client.accounts_get(request)
            
            institution_name = "Unknown"
            try:
                from plaid.model.institutions_get_by_id_request import InstitutionsGetByIdRequest
                from plaid.model.country_code import CountryCode
                
                inst_request = InstitutionsGetByIdRequest(
                    institution_id=response.item.institution_id,
                    country_codes=[CountryCode("US")]
                )
                inst_response = self._client.institutions_get_by_id(inst_request)
                institution_name = inst_response.institution.name
            except Exception:
                pass
            
            accounts = []
            for acc in response.accounts:
                linked = LinkedBankAccount(
                    account_id=acc.account_id,
                    institution_name=institution_name,
                    account_name=acc.name,
                    account_type=acc.subtype.value if acc.subtype else "checking",
                    account_mask=acc.mask or "****",
                    available_balance=float(acc.balances.available) if acc.balances.available else None,
                    current_balance=float(acc.balances.current) if acc.balances.current else None,
                    currency=acc.balances.iso_currency_code or "USD",
                    verified=True
                )
                accounts.append(linked)
                self._linked_accounts[acc.account_id] = linked
                self._access_tokens[acc.account_id] = access_token
            
            return accounts
            
        except Exception as e:
            logger.error(f"Failed to fetch accounts: {e}")
            return []
    
    async def get_linked_accounts(self) -> List[LinkedBankAccount]:
        """Get all linked bank accounts."""
        return list(self._linked_accounts.values())
    
    async def get_account_balance(
        self,
        account_id: str
    ) -> Optional[Dict[str, float]]:
        """Get current balance for a linked account."""
        if account_id not in self._access_tokens:
            return None
        
        try:
            from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
            
            access_token = self._access_tokens[account_id]
            request = AccountsBalanceGetRequest(access_token=access_token)
            response = self._client.accounts_balance_get(request)
            
            for acc in response.accounts:
                if acc.account_id == account_id:
                    return {
                        "available": float(acc.balances.available) if acc.balances.available else 0,
                        "current": float(acc.balances.current) if acc.balances.current else 0,
                    }
            return None
            
        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            return None
    
    async def create_processor_token(
        self,
        account_id: str,
        processor: str  # "alpaca", "interactive_brokers", etc.
    ) -> Optional[str]:
        """
        Create a processor token for broker integration.
        
        This allows the broker to directly debit/credit the linked bank account.
        
        Args:
            account_id: The linked bank account ID
            processor: The processor/broker name
            
        Returns:
            Processor token for broker integration
        """
        if account_id not in self._access_tokens:
            logger.error(f"Account not linked: {account_id}")
            return None
        
        try:
            from plaid.model.processor_token_create_request import ProcessorTokenCreateRequest
            from plaid.model.processor_token_create_request_processor import ProcessorTokenCreateRequestProcessor
            
            # Map processor names
            processor_map = {
                "alpaca": ProcessorTokenCreateRequestProcessor("alpaca"),
                "interactive_brokers": ProcessorTokenCreateRequestProcessor("interactive_brokers"),
                "drivewealth": ProcessorTokenCreateRequestProcessor("drivewealth"),
            }
            
            if processor.lower() not in processor_map:
                logger.error(f"Unsupported processor: {processor}")
                return None
            
            access_token = self._access_tokens[account_id]
            request = ProcessorTokenCreateRequest(
                access_token=access_token,
                account_id=account_id,
                processor=processor_map[processor.lower()]
            )
            
            response = self._client.processor_token_create(request)
            return response.processor_token
            
        except Exception as e:
            logger.error(f"Failed to create processor token: {e}")
            return None
    
    async def initiate_transfer(
        self,
        account_id: str,
        amount: float,
        direction: TransferDirection,
        brokerage_account_id: str,
        broker_name: str,
        description: str = ""
    ) -> Optional[Transfer]:
        """
        Initiate a transfer between bank and brokerage.
        
        Note: Actual ACH transfers are typically handled by the broker
        using the processor token. This is a record-keeping function.
        
        Args:
            account_id: Bank account ID
            amount: Amount to transfer
            direction: deposit or withdraw
            brokerage_account_id: Destination brokerage account
            broker_name: Broker handling the transfer
            description: Transfer description
            
        Returns:
            Transfer record
        """
        if account_id not in self._linked_accounts:
            logger.error(f"Account not linked: {account_id}")
            return None
        
        transfer = Transfer(
            transfer_id=f"xf-{datetime.now().strftime('%Y%m%d%H%M%S')}-{account_id[:8]}",
            direction=direction,
            amount=amount,
            status=TransferStatus.PENDING,
            bank_account_id=account_id,
            brokerage_account_id=brokerage_account_id,
            broker_name=broker_name,
            description=description or f"{direction.value.title()} via Plaid"
        )
        
        logger.info(f"Transfer initiated: {transfer.transfer_id} - ${amount} {direction.value}")
        return transfer
    
    async def unlink_account(self, account_id: str) -> bool:
        """Unlink a bank account."""
        if account_id in self._linked_accounts:
            del self._linked_accounts[account_id]
        if account_id in self._access_tokens:
            # Optionally invalidate the access token with Plaid
            del self._access_tokens[account_id]
        logger.info(f"Bank account unlinked: {account_id}")
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Get client status as dictionary."""
        return {
            "environment": self.environment,
            "initialized": self._client is not None,
            "linked_accounts": [
                {
                    "account_id": acc.account_id,
                    "institution": acc.institution_name,
                    "name": acc.account_name,
                    "type": acc.account_type,
                    "mask": acc.account_mask,
                    "verified": acc.verified,
                }
                for acc in self._linked_accounts.values()
            ]
        }


# Global instance
_plaid_client: Optional[PlaidBankingClient] = None


def get_plaid_client() -> PlaidBankingClient:
    """Get or create global Plaid client."""
    global _plaid_client
    if _plaid_client is None:
        from src.config.settings import get_settings
        settings = get_settings()
        _plaid_client = PlaidBankingClient(
            client_id=getattr(settings, 'plaid_client_id', ''),
            secret=getattr(settings, 'plaid_secret', ''),
            environment=getattr(settings, 'plaid_environment', 'sandbox')
        )
    return _plaid_client


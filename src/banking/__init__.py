"""
Banking Integration Layer for XFactor Bot.
Supports bank account linking and ACH transfers via Plaid.
"""

from src.banking.plaid_client import PlaidBankingClient, get_plaid_client

__all__ = [
    "PlaidBankingClient",
    "get_plaid_client",
]


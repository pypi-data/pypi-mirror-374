"""
Account Information Services (AIS) Core Module.

This module provides the core types, enums, base classes, and interfaces
for implementing PSD2-compliant Account Information Services.

The AIS module is based on the Berlin Group NextGenPSD2 Framework v1.3.14
and provides standardized data models and interfaces for:
- Account information retrieval
- Transaction history
- Balance information
- Consent management
- Authentication and authorization

All banks and credit card providers should implement these interfaces
to ensure PSD2 compliance and interoperability.
"""

from israel_open_banking.core.ais.general.base import (
    AISAccountManager,
    AISBalanceManager,
    AISBaseClient,
    AISConsentManager,
    AISTransactionManager,
)
from .general.enums import AccountStatus, AccountUsage, AuthenticationType, BookingStatus, CashAccountType, \
    ConsentStatus, TransactionStatus, BalanceType, FrequencyCode, DayOfExecution, ExecutionRule, TppMessageCategory
from .general.exceptions import (
    AISAccountException,
    AISAuthenticationException,
    AISConsentException,
    AISException,
    AISTransactionException,
)

__all__ = [
    # Enums
    "AccountStatus",
    "AccountUsage",
    "AuthenticationType",
    "BookingStatus",
    "CashAccountType",
    "ConsentStatus",
    "TransactionStatus",
    "BalanceType",
    "FrequencyCode",
    "DayOfExecution",
    "ExecutionRule",
    # Models
    "AccountDetails",
    "AccountList",
    "AccountOwner",
    "AccountReference",
    "AccountReport",
    "Balance",
    "BalanceList",
    "Transaction",
    "TransactionDetails",
    "TransactionList",
    "CardTransaction",
    "Consent",
    "ConsentStatusResponse",
    "ConsentAccess",
    "ConsentAccountAccess",
    "ConsentCardAccountAccess",
    "AuthenticationObject",
    "ChallengeData",
    "ScaMethods",
    "Amount",
    "Address",
    "BankTransactionCode",
    "ExchangeRate",
    "ExchangeRateList",
    "HrefType",
    "Links",
    "TppMessage",
    "TppMessageCategory",
    # Base classes
    "AISBaseClient",
    "AISConsentManager",
    "AISAccountManager",
    "AISTransactionManager",
    "AISBalanceManager",
    # Exceptions
    "AISException",
    "AISConsentException",
    "AISAccountException",
    "AISTransactionException",
    "AISAuthenticationException",
]

from .general.models import AccountDetails, AccountList, AccountOwner, AccountReference, AccountReport, Balance, \
    BalanceList, Transaction, TransactionDetails, TransactionList, CardTransaction, Consent, ConsentStatusResponse, \
    ConsentAccess, ConsentAccountAccess, ConsentCardAccountAccess, AuthenticationObject, ChallengeData, ScaMethods, \
    Amount, Address, BankTransactionCode, ExchangeRate, ExchangeRateList, HrefType, Links, TppMessage

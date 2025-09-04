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

from .base import (
    AISSavingsAccountManager,
    AISSavingsBalanceManager,
    AISSavingsBaseClient,
    AISSavingsTransactionManager,
)


__all__ = [
    # Enums

    # Base classes
    "AISSavingsBaseClient",
    "AISSavingsAccountManager",
    "AISSavingsTransactionManager",
    "AISSavingsBalanceManager",
    # Exceptions
    "AISSavingsAndLoansException",
    "AISConsentSavingsAndLoansException",
    "AISAccountSavingsAndLoansException",
    "AISTransactionSavingsAndLoansException",
]

from .exceptions import AISSavingsAndLoansException, AISConsentSavingsAndLoansException, \
    AISAccountSavingsAndLoansException, AISTransactionSavingsAndLoansException

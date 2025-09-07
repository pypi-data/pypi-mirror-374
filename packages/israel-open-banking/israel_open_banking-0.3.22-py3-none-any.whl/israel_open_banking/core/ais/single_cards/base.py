"""
PSD2 AIS Base Classes.

This module contains abstract base classes that define the interface
for PSD2-compliant Account Information Services.

All banks and credit card providers should implement these base classes
to ensure PSD2 compliance and interoperability.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Optional, TYPE_CHECKING

from .models import (
    CardAccountList,
    CardAccountDetails, CardBalanceList, CardAccountTransactionReport,
)
from .. import BookingStatus

if TYPE_CHECKING:
    from core.client import OpenBankingClient


class AISSingleCardsBaseClient(ABC):
    """
    Abstract base class for AIS Single Cards clients.

    This class defines the interface that all AIS clients must implement
    to be PSD2-compliant. It provides the core functionality for:
    - Account information retrieval
    - Transaction history
    - Balance information
    """

    def __init__(self, client: "OpenBankingClient") -> None:
        """
        Initialize the AIS base client.

        Args:
            client: The underlying OpenBankingClient instance
        """
        self.client = client
        # These will be set by concrete implementations
        self.cards: AISSingleCardsManager | None = None
        self.transactions: AISSingleCardsTransactionManager | None = None
        self.balances: AISSingleCardsBalanceManager | None = None

    @abstractmethod
    def get_cards(self) -> CardAccountList:
        """
        Get list of cards accounts.

        Returns:
            List of cards accounts
        """
        pass

    @abstractmethod
    def get_card_details(
            self, card_account_id: str
    ) -> CardAccountDetails:
        """
        Get savings account details.

        Args:
            card_account_id: Savings account identifier

        Returns:
            Card account details
        """
        pass

    @abstractmethod
    def get_transactions(
            self,
            card_account_id: str,
            date_from: Optional[date] = None,
            date_to: Optional[date] = None,
            value_date_from: Optional[date] = None,
            value_date_to: Optional[date] = None,
            booking_status: BookingStatus = BookingStatus.BOOKED,
            delta_list: bool = False,
    ) -> CardAccountTransactionReport:
        """
        Get card account transactions.

        Args:
            card_account_id: Card account identifier
            date_from: Start date for transaction range
            date_to: End date for transaction range
            value_date_from: Start value date for transaction range
            value_date_to: End value date for transaction range
            booking_status: Booking status filter
            delta_list: Whether to return delta list

        Returns:
            List of cards transactions
        """
        pass

    @abstractmethod
    def get_balances(
            self, card_account_id: str,
            date_from: Optional[date] = None,
            value_date_from: Optional[date] = None
    ) -> CardBalanceList:
        """
        Get card account balances.

        Args:
            card_account_id: Account identifier
            date_from: Start date for balance retrieval
            value_date_from: Value date for balance retrieval

        Returns:
            Card account balances
        """
        pass


class AISSingleCardsManager(ABC):
    """
    Abstract base class for account management.

    This class defines the interface for account-related operations
    including account listing and details retrieval.
    """

    def __init__(self, ais_client: AISSingleCardsBaseClient) -> None:
        """
        Initialize the account manager.

        Args:
            ais_client: The AIS client instance
        """
        self.ais_client = ais_client

    @abstractmethod
    def get_cards(self) -> CardAccountList:
        """
        Get list of card accounts.

        Returns:
            List of card accounts
        """
        pass

    @abstractmethod
    def get_card_details(
            self, card_account_id: str
    ) -> CardAccountDetails:
        """
        Get card account details.

        Args:
            card_account_id: Savings account identifier

        Returns:
            Card account details
        """
        pass


class AISSingleCardsTransactionManager(ABC):
    """
    Abstract base class for transaction management.

    This class defines the interface for transaction-related operations
    including transaction listing and details retrieval.
    """

    def __init__(self, ais_client: AISSingleCardsBaseClient) -> None:
        """
        Initialize the transaction manager.

        Args:
            ais_client: The AIS client instance
        """
        self.ais_client = ais_client

    @abstractmethod
    def get_transactions(
            self,
            card_account_id: str,
            date_from: Optional[date] = None,
            date_to: Optional[date] = None,
            value_date_from: Optional[date] = None,
            value_date_to: Optional[date] = None,
            booking_status: BookingStatus = BookingStatus.BOOKED,
            delta_list: bool = False,
    ) -> CardAccountTransactionReport:
        """
        Get card account transactions.

        Args:
            card_account_id: Card account identifier
            date_from: Start date for transaction range
            date_to: End date for transaction range
            value_date_from: Start value date for transaction range
            value_date_to: End value date for transaction range
            booking_status: Booking status filter
            delta_list: Whether to return delta list

        Returns:
            List of savings transactions
        """
        pass


class AISSingleCardsBalanceManager(ABC):
    """
    Abstract base class for balance management.

    This class defines the interface for balance-related operations
    including balance retrieval.
    """

    def __init__(self, ais_client: AISSingleCardsBaseClient) -> None:
        """
        Initialize the balance manager.

        Args:
            ais_client: The AIS client instance
        """
        self.ais_client = ais_client

    @abstractmethod
    def get_balances(self, card_account_id: str,
                     date_from: Optional[date] = None,
                     value_date_from: Optional[date] = None
                     ) -> CardBalanceList:
        """
        Get card account balances.

        Args:
            card_account_id: Account identifier
            date_from: Start date for balance retrieval
            value_date_from: Value date for balance retrieval

        Returns:
            Card account balances
        """
        pass

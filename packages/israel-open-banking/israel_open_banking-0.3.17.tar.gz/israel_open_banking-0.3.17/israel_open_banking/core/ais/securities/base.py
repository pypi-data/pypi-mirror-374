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

from .enums import OrderStatusCode
from .models import (
    SecuritiesAccountList, SecuritiesAccountDetails, SecuritiesAccountPositionsWrapper, SecuritiesTransactionsWrapper,
    SecuritiesTransaction, SecuritiesOrdersWrapper, SecuritiesOrder,
)

if TYPE_CHECKING:
    from core.client import OpenBankingClient


class AISSecuritiesBaseClient(ABC):
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
        self.cards: AISSecuritiesAccountManager | None = None
        self.positions: AISSecuritiesPositionManager | None = None
        self.transactions: AISSecuritiesTransactionManager | None = None
        self.orders: AISSecuritiesOrderManager | None = None

    @abstractmethod
    def get_accounts(self, evaluation_currency: Optional[str] = None) -> SecuritiesAccountList:
        """
        Get list of psd2_securities accounts.

        Args:
            evaluation_currency: Currency for evaluation

        Returns:
            List of psd2_securities accounts
        """
        pass

    @abstractmethod
    def get_account_details(
            self, securities_account_id: str,
            evaluation_currency: Optional[str] = None
    ) -> SecuritiesAccountDetails:
        """
        Get psd2_securities account details.

        Args:
            securities_account_id: Securities account identifier
            evaluation_currency: Currency for evaluation

        Returns:
            Securities account details
        """
        pass

    @abstractmethod
    def get_positions(self, securities_account_id: str) -> SecuritiesAccountPositionsWrapper:
        """
        Get psd2_securities account positions.

        Args:
            securities_account_id: Account identifier

        Returns:
            Securities account positions
        """
        pass

    @abstractmethod
    def get_transactions(
            self,
            securities_account_id: str,
            date_from: date,
            date_to: Optional[date] = None,
            entry_reference_from: Optional[str] = None,
            delta_list: bool = False,
    ) -> SecuritiesTransactionsWrapper:
        """
        Get psd2_securities transactions.

        Args:
            securities_account_id: Card account identifier
            date_from: Start date for transaction range
            date_to: End date for transaction range
            entry_reference_from: Entry reference for pagination
            delta_list: Whether to return delta list

        Returns:
            List of psd2_securities transactions
        """
        pass

    @abstractmethod
    def get_transaction_details(
            self, securities_account_id: str, transaction_id: str
    ) -> SecuritiesTransaction:
        """
        Get details of a specific psd2_securities transaction.

        Args:
            securities_account_id: Securities account identifier
            transaction_id: Transaction identifier

        Returns:
            Details of the psd2_securities transaction
        """
        pass

    @abstractmethod
    def get_orders(self, securities_account_id: str,
                   date_from: date,
                   date_to: Optional[date] = None,
                   order_status: Optional[OrderStatusCode] = None
                   ) -> SecuritiesOrdersWrapper:
        """
        Get psd2_securities orders.

        Args:
              securities_account_id: Account identifier
              date_from: Start date for order range
              date_to: End date for order range
              order_status: Status of the orders to filter

        Returns:
              List of psd2_securities orders
        """
        pass

    @abstractmethod
    def get_order_details(
            self, securities_account_id: str, order_id: str
    ) -> SecuritiesOrder:
        """
        Get details of a specific psd2_securities order.

        Args:
            securities_account_id: Securities account identifier
            order_id: Order identifier

        Returns:
            Details of the psd2_securities order
        """
        pass


class AISSecuritiesAccountManager(ABC):
    """
    Abstract base class for account management.

    This class defines the interface for account-related operations
    including account listing and details retrieval.
    """

    def __init__(self, ais_client: AISSecuritiesBaseClient) -> None:
        """
        Initialize the account manager.

        Args:
            ais_client: The AIS client instance
        """
        self.ais_client = ais_client

    @abstractmethod
    def get_accounts(self, evaluation_currency: Optional[str] = None) -> SecuritiesAccountList:
        """
        Get list of psd2_securities accounts.
        Args:
            evaluation_currency: Currency for evaluation

        Returns:
            List of psd2_securities accounts
        """
        pass

    @abstractmethod
    def get_account_details(
            self, securities_account_id: str,
            evaluation_currency: Optional[str] = None
    ) -> SecuritiesAccountDetails:
        """
        Get psd2_securities account details.

        Args:
            securities_account_id: Securities account identifier
            evaluation_currency: Currency for evaluation

        Returns:
            Securities account details
        """
        pass


class AISSecuritiesPositionManager(ABC):
    """
    Abstract base class for position management.

    This class defines the interface for balance-related operations
    including balance retrieval.
    """

    def __init__(self, ais_client: AISSecuritiesBaseClient) -> None:
        """
        Initialize the position manager.

        Args:
            ais_client: The AIS client instance
        """
        self.ais_client = ais_client

    @abstractmethod
    def get_positions(self, securities_account_id: str) -> SecuritiesAccountPositionsWrapper:
        """
        Get psd2_securities account positions.

        Args:
            securities_account_id: Account identifier


        Returns:
            Securities account positions
        """
        pass


class AISSecuritiesTransactionManager(ABC):
    """
    Abstract base class for transaction management.

    This class defines the interface for transaction-related operations
    including transaction listing and details retrieval.
    """

    def __init__(self, ais_client: AISSecuritiesBaseClient) -> None:
        """
        Initialize the transaction manager.

        Args:
            ais_client: The AIS client instance
        """
        self.ais_client = ais_client

    @abstractmethod
    def get_transactions(
            self,
            securities_account_id: str,
            date_from: date,
            date_to: Optional[date] = None,
            entry_reference_from: Optional[str] = None,
            delta_list: bool = False,
    ) -> SecuritiesTransactionsWrapper:
        """
        Get psd2_securities transactions.

        Args:
            securities_account_id: Card account identifier
            date_from: Start date for transaction range
            date_to: End date for transaction range
            entry_reference_from: Entry reference for pagination
            delta_list: Whether to return delta list

        Returns:
            List of psd2_securities transactions
        """
        pass

    @abstractmethod
    def get_transaction_details(
            self, securities_account_id: str, transaction_id: str
    ) -> SecuritiesTransaction:
        """
        Get details of a specific psd2_securities transaction.

        Args:
            securities_account_id: Securities account identifier
            transaction_id: Transaction identifier

        Returns:
            Details of the psd2_securities transaction
        """
        pass


class AISSecuritiesOrderManager(ABC):
    """
    Abstract base class for order management.

    This class defines the interface for order-related operations
    including order listing and details retrieval.
    """

    def __init__(self, ais_client: AISSecuritiesBaseClient) -> None:
        """
        Initialize the order manager.

        Args:
            ais_client: The AIS client instance
        """
        self.ais_client = ais_client

    @abstractmethod
    def get_orders(self, securities_account_id: str,
                   date_from: date,
                   date_to: Optional[date] = None,
                   order_status: Optional[OrderStatusCode] = None
                   ) -> SecuritiesOrdersWrapper:
        """
        Get psd2_securities orders.

        Args:
            securities_account_id: Account identifier
            date_from: Start date for order range
            date_to: End date for order range
            order_status: Status of the orders to filter

        Returns:
            List of psd2_securities orders
        """
        pass

    @abstractmethod
    def get_order_details(
            self, securities_account_id: str, order_id: str
    ) -> SecuritiesOrder:
        """
        Get details of a specific psd2_securities order.

        Args:
            securities_account_id: Securities account identifier
            order_id: Order identifier

        Returns:
            Details of the psd2_securities order
        """
        pass

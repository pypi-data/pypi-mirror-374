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
    SavingAccountList, SavingBalanceList, SavingAccountTransactionReport,
    LoanAccountList, AccountDetailsSavingsLoans, LoanBalanceList, LoanAccountTransactionReport,
)
from .. import BookingStatus

if TYPE_CHECKING:
    from core.client import OpenBankingClient


class AISSavingsBaseClient(ABC):
    """
    Abstract base class for AIS clients.

    This class defines the interface that all AIS clients must implement
    to be PSD2-compliant. It provides the core functionality for:
    - Account information retrieval
    - Transaction history
    - Balance information
    - Consent management
    - Authentication and authorization
    """

    def __init__(self, client: "OpenBankingClient") -> None:
        """
        Initialize the AIS base client.

        Args:
            client: The underlying OpenBankingClient instance
        """
        self.client = client
        # These will be set by concrete implementations
        self.accounts: AISSavingsAccountManager | None = None
        self.transactions: AISSavingsTransactionManager | None = None
        self.balances: AISSavingsBalanceManager | None = None

    @abstractmethod
    def get_accounts(self) -> SavingAccountList:
        """
        Get list of savings accounts.

        Returns:
            List of savings accounts
        """
        pass

    @abstractmethod
    def get_account_details(
            self, savings_account_id: str
    ) -> AccountDetailsSavingsLoans:
        """
        Get savings account details.

        Args:
            savings_account_id: Savings account identifier

        Returns:
            Account details
        """
        pass

    @abstractmethod
    def get_transactions(
            self,
            savings_account_id: str,
            date_from: date,
            booking_status: BookingStatus,
            date_to: Optional[date] = None,
            entry_reference_from: str | None = None,
            delta_list: bool = False,
    ) -> SavingAccountTransactionReport:
        """
        Get savings account transactions.

        Args:
            savings_account_id: Savings account identifier
            date_from: Start date for transaction range
            date_to: End date for transaction range
            booking_status: Booking status filter
            entry_reference_from: Entry reference from
            delta_list: Whether to return delta list

        Returns:
            List of savings transactions
        """
        pass

    @abstractmethod
    def get_balances(
            self, saving_account_id: str
    ) -> SavingBalanceList:
        """
        Get savings account balances.

        Args:
            saving_account_id: Savings account identifier

        Returns:
            Saving account balances
        """
        pass


class AISSavingsAccountManager(ABC):
    """
    Abstract base class for account management.

    This class defines the interface for account-related operations
    including account listing and details retrieval.
    """

    def __init__(self, ais_client: AISSavingsBaseClient) -> None:
        """
        Initialize the account manager.

        Args:
            ais_client: The AIS client instance
        """
        self.ais_client = ais_client

    @abstractmethod
    def get_accounts(self) -> SavingAccountList:
        """
        Get list of savings accounts.

        Returns:
            List of savings accounts
        """
        pass

    @abstractmethod
    def get_account_details(
            self, savings_account_id: str
    ) -> AccountDetailsSavingsLoans:
        """
        Get account details.

        Args:
            savings_account_id: Savings account identifier

        Returns:
            Account details
        """
        pass


class AISSavingsTransactionManager(ABC):
    """
    Abstract base class for transaction management.

    This class defines the interface for transaction-related operations
    including transaction listing and details retrieval.
    """

    def __init__(self, ais_client: AISSavingsBaseClient) -> None:
        """
        Initialize the transaction manager.

        Args:
            ais_client: The AIS client instance
        """
        self.ais_client = ais_client

    @abstractmethod
    def get_transactions(
            self,
            savings_account_id: str,
            date_from: date,
            booking_status: BookingStatus,
            date_to: Optional[date] = None,
            entry_reference_from: str | None = None,
            delta_list: bool = False,
    ) -> SavingAccountTransactionReport:
        """
        Get savings account transactions.

        Args:
            savings_account_id: Savings account identifier
            date_from: Start date for transaction range
            date_to: End date for transaction range
            booking_status: Booking status filter
            entry_reference_from: Entry reference from
            delta_list: Whether to return delta list

        Returns:
            List of savings transactions
        """
        pass


class AISSavingsBalanceManager(ABC):
    """
    Abstract base class for balance management.

    This class defines the interface for balance-related operations
    including balance retrieval.
    """

    def __init__(self, ais_client: AISSavingsBaseClient) -> None:
        """
        Initialize the balance manager.

        Args:
            ais_client: The AIS client instance
        """
        self.ais_client = ais_client

    @abstractmethod
    def get_balances(self, saving_account_id: str) -> SavingBalanceList:
        """
        Get account balances.

        Args:
            saving_account_id: Account identifier

        Returns:
            Saving account balances
        """
        pass


class AISLoansBaseClient(ABC):
    """
    Abstract base class for AIS clients.

    This class defines the interface that all AIS clients must implement
    to be PSD2-compliant. It provides the core functionality for:
    - Account information retrieval
    - Transaction history
    - Balance information
    - Consent management
    - Authentication and authorization
    """

    def __init__(self, client: "OpenBankingClient") -> None:
        """
        Initialize the AIS base client.

        Args:
            client: The underlying OpenBankingClient instance
        """
        self.client = client
        # These will be set by concrete implementations
        self.accounts: AISLoansAccountManager | None = None
        self.transactions: AISLoansTransactionManager | None = None
        self.balances: AISLoansBalanceManager | None = None

    @abstractmethod
    def get_accounts(self) -> LoanAccountList:
        """
        Get list of loan accounts.

        Returns:
            List of loan accounts
        """
        pass

    @abstractmethod
    def get_account_details(
            self, loan_account_id: str
    ) -> AccountDetailsSavingsLoans:
        """
        Get loan account details.

        Args:
            loan_account_id: Loan account identifier

        Returns:
            Loan account details
        """
        pass

    @abstractmethod
    def get_transactions(
            self,
            loan_account_id: str,
            date_from: date,
            booking_status: BookingStatus,
            date_to: Optional[date] = None,
            entry_reference_from: str | None = None,
            delta_list: bool = False,
    ) -> LoanAccountTransactionReport:
        """
        Get loan account transactions.

        Args:
            loan_account_id: Loan account identifier
            date_from: Start date for transaction range
            date_to: End date for transaction range
            booking_status: Booking status filter
            entry_reference_from: Entry reference from
            delta_list: Whether to return delta list

        Returns:
            List of loan transactions
        """
        pass

    @abstractmethod
    def get_balances(
            self, loan_account_id: str
    ) -> LoanBalanceList:
        """
        Get loan account balances.

        Args:
            loan_account_id: Loan account identifier

        Returns:
            Loan account balances
        """
        pass


class AISLoansAccountManager(ABC):
    """
    Abstract base class for account management.

    This class defines the interface for account-related operations
    including account listing and details retrieval.
    """

    def __init__(self, ais_client: AISLoansBaseClient) -> None:
        """
        Initialize the account manager.

        Args:
            ais_client: The AIS client instance
        """
        self.ais_client = ais_client

    @abstractmethod
    def get_accounts(self) -> LoanAccountList:
        """
        Get list of loan accounts.

        Returns:
            List of loan accounts
        """
        pass

    @abstractmethod
    def get_account_details(
            self, loan_account_id: str
    ) -> AccountDetailsSavingsLoans:
        """
        Get loan account details.

        Args:
            loan_account_id: Loan account identifier

        Returns:
            Loan account details
        """
        pass


class AISLoansTransactionManager(ABC):
    """
    Abstract base class for transaction management.

    This class defines the interface for transaction-related operations
    including transaction listing and details retrieval.
    """

    def __init__(self, ais_client: AISLoansBaseClient) -> None:
        """
        Initialize the transaction manager.

        Args:
            ais_client: The AIS client instance
        """
        self.ais_client = ais_client

    @abstractmethod
    def get_transactions(
            self,
            loan_account_id: str,
            date_from: date,
            booking_status: BookingStatus,
            date_to: Optional[date] = None,
            entry_reference_from: str | None = None,
            delta_list: bool = False,
    ) -> LoanAccountTransactionReport:
        """
        Get loan account transactions.

        Args:
            loan_account_id: Loan account identifier
            date_from: Start date for transaction range
            date_to: End date for transaction range
            booking_status: Booking status filter
            entry_reference_from: Entry reference from
            delta_list: Whether to return delta list

        Returns:
            List of loan transactions
        """
        pass


class AISLoansBalanceManager(ABC):
    """
    Abstract base class for balance management.

    This class defines the interface for balance-related operations
    including balance retrieval.
    """

    def __init__(self, ais_client: AISLoansBaseClient) -> None:
        """
        Initialize the balance manager.

        Args:
            ais_client: The AIS client instance
        """
        self.ais_client = ais_client

    @abstractmethod
    def get_balances(self, loan_account_id: str) -> LoanBalanceList:
        """
        Get loan account balances.

        Args:
            loan_account_id: Loan account identifier

        Returns:
            Loan account balances
        """
        pass

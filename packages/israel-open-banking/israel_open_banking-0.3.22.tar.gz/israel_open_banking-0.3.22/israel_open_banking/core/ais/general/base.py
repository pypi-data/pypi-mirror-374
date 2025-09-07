"""
PSD2 AIS Base Classes.

This module contains abstract base classes that define the interface
for PSD2-compliant Account Information Services.

All banks and credit card providers should implement these base classes
to ensure PSD2 compliance and interoperability.
"""

from abc import ABC, abstractmethod
from datetime import date
from typing import Any, Optional, TYPE_CHECKING

from .enums import BookingStatus
from .models import (
    AccountDetails,
    AccountList,
    BalanceList,
    Consent,
    ConsentAccess,
    ConsentAccountAccess,
    ConsentCardAccountAccess,
    ConsentStatusResponse,
    TransactionDetails,
    AccountTransactionReport, )

if TYPE_CHECKING:
    from core.client import OpenBankingClient


class AISBaseClient(ABC):
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
        self.consents: AISConsentManager | None = None
        self.accounts: AISAccountManager | None = None
        self.transactions: AISTransactionManager | None = None
        self.balances: AISBalanceManager | None = None

    @abstractmethod
    def get_accounts(self, with_balance: bool = False) -> AccountList:
        """
        Get list of accounts.

        Args:
            with_balance: Whether to include balance information

        Returns:
            List of accounts
        """
        pass

    @abstractmethod
    def get_account_details(
            self, account_id: str, with_balance: bool = False
    ) -> AccountDetails:
        """
        Get account details.

        Args:
            account_id: Account identifier
            with_balance: Whether to include balance information

        Returns:
            Account details
        """
        pass

    @abstractmethod
    def get_balances(self, account_id: str) -> BalanceList:
        """
        Get account balances.

        Args:
            account_id: Account identifier

        Returns:
            Account balances
        """
        pass

    @abstractmethod
    def get_transactions(
            self,
            account_id: str,
            date_to: date,
            booking_status: BookingStatus = BookingStatus.BOOKED,
            date_from: Optional[date] = None,
            with_balance: bool = False,
            entry_reference_from: str | None = None,
            delta_list: bool = False,
    ) -> AccountTransactionReport:
        """
        Get account transactions.

        Args:
            account_id: Account identifier
            date_from: Start date for transaction range
            date_to: End date for transaction range
            booking_status: Booking status filter - all banks support booked
            with_balance: Whether to include balance information
            entry_reference_from: Entry reference from
            delta_list: Whether to return delta list

        Returns:
            List of transactions
        """
        pass

    @abstractmethod
    def get_transaction_details(
            self, account_id: str, transaction_id: str
    ) -> TransactionDetails:
        """
        Get transaction details.

        Args:
            account_id: Account identifier
            transaction_id: Transaction identifier

        Returns:
            Transaction details
        """
        pass


class AISConsentManager(ABC):
    """
    Abstract base class for consent management.

    This class defines the interface for managing PSD2 consents,
    including creation, status checking, and revocation.
    """

    def __init__(self, ais_client: AISBaseClient) -> None:
        """
        Initialize the consent manager.

        Args:
            ais_client: The AIS client instance
        """
        self.ais_client = ais_client

    @abstractmethod
    def create_consent(
            self,
            access: ConsentAccess,
            recurring_indicator: bool,
            valid_until: date,
            frequency_per_day: int,
            combined_service_indicator: bool = False,
            card_number: str | None = None,
            expiration_date: date | None = None,
            card_information: str | None = None,
            registration_information: str | None = None,
            accounts: ConsentAccountAccess | None = None,
            card_accounts: ConsentCardAccountAccess | None = None,
    ) -> Consent:
        """
        Create a new consent.

        Args:
            access: Consent access configuration
            recurring_indicator: Whether consent is recurring
            valid_until: Consent validity end date
            frequency_per_day: Maximum frequency per day
            combined_service_indicator: Whether combined with payment service
            card_number: Card number (for card accounts)
            expiration_date: Card expiration date
            card_information: Additional card information
            registration_information: Registration information
            accounts: Account access configuration
            card_accounts: Card account access configuration

        Returns:
            Created consent
        """
        pass

    @abstractmethod
    def get_consent(self, consent_id: str) -> Consent:
        """
        Get consent information.

        Args:
            consent_id: Consent identifier

        Returns:
            Consent information
        """
        pass

    @abstractmethod
    def get_consent_status(self, consent_id: str) -> ConsentStatusResponse:
        """
        Get consent status.

        Args:
            consent_id: Consent identifier

        Returns:
            Consent status
        """
        pass

    @abstractmethod
    def delete_consent(self, consent_id: str) -> None:
        """
        Delete consent.

        Args:
            consent_id: Consent identifier
        """
        pass

    @abstractmethod
    def start_authorization(
            self,
            consent_id: str,
            psu_id: str | None = None,
            psu_corporate_id: str | None = None,
            psu_ip_address: str | None = None,
            psu_id_type: str | None = None,
            psu_corporate_id_type: str | None = None,
            psu_ip_port: str | None = None,
            psu_accept: str | None = None,
            psu_accept_charset: str | None = None,
            psu_accept_encoding: str | None = None,
            psu_accept_language: str | None = None,
            psu_user_agent: str | None = None,
            psu_http_method: str | None = None,
            psu_device_id: str | None = None,
            psu_geo_location: str | None = None,
    ) -> dict[str, Any]:
        """
        Start authorization process for consent.

        Args:
            consent_id: Consent identifier
            psu_id: PSU identifier
            psu_corporate_id: PSU corporate identifier
            psu_ip_address: PSU IP address
            psu_id_type: PSU ID type
            psu_corporate_id_type: PSU corporate ID type
            psu_ip_port: PSU IP port
            psu_accept: PSU accept header
            psu_accept_charset: PSU accept charset
            psu_accept_encoding: PSU accept encoding
            psu_accept_language: PSU accept language
            psu_user_agent: PSU user agent
            psu_http_method: PSU HTTP method
            psu_device_id: PSU device ID
            psu_geo_location: PSU geo location

        Returns:
            Authorization response
        """
        pass

    @abstractmethod
    def get_authorization_status(
            self, consent_id: str, authorization_id: str
    ) -> dict[str, Any]:
        """
        Get authorization status.

        Args:
            consent_id: Consent identifier
            authorization_id: Authorization identifier

        Returns:
            Authorization status
        """
        pass

    @abstractmethod
    def update_psu_data(
            self,
            consent_id: str,
            authorization_id: str,
            psu_authentication: dict[str, Any] | None = None,
            psu_identification: dict[str, Any] | None = None,
            psu_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Update PSU data for authorization.

        Args:
            consent_id: Consent identifier
            authorization_id: Authorization identifier
            psu_authentication: PSU authentication data
            psu_identification: PSU identification data
            psu_data: PSU data

        Returns:
            Update response
        """
        pass


class AISAccountManager(ABC):
    """
    Abstract base class for account management.

    This class defines the interface for account-related operations
    including account listing and details retrieval.
    """

    def __init__(self, ais_client: AISBaseClient) -> None:
        """
        Initialize the account manager.

        Args:
            ais_client: The AIS client instance
        """
        self.ais_client = ais_client

    @abstractmethod
    def get_accounts(self, with_balance: bool = False) -> AccountList:
        """
        Get list of accounts.

        Args:
            with_balance: Whether to include balance information

        Returns:
            List of accounts
        """
        pass

    @abstractmethod
    def get_account_details(
            self, account_id: str, with_balance: bool = False
    ) -> AccountDetails:
        """
        Get account details.

        Args:
            account_id: Account identifier
            with_balance: Whether to include balance information

        Returns:
            Account details
        """
        pass


class AISTransactionManager(ABC):
    """
    Abstract base class for transaction management.

    This class defines the interface for transaction-related operations
    including transaction listing and details retrieval.
    """

    def __init__(self, ais_client: AISBaseClient) -> None:
        """
        Initialize the transaction manager.

        Args:
            ais_client: The AIS client instance
        """
        self.ais_client = ais_client

    @abstractmethod
    def get_transactions(
            self,
            account_id: str,
            date_from: date,
            booking_status: BookingStatus,
            date_to: Optional[date] = None,
            with_balance: bool = False,
            entry_reference_from: str | None = None,
            delta_list: bool = False,
    ) -> AccountTransactionReport:
        """
        Get account transactions.

        Args:
            account_id: Account identifier
            date_from: Start date for transaction range
            date_to: End date for transaction range
            booking_status: Booking status filter
            with_balance: Whether to include balance information
            entry_reference_from: Entry reference from
            delta_list: Whether to return delta list

        Returns:
            List of transactions
        """
        pass

    @abstractmethod
    def get_transaction_details(
            self, account_id: str, transaction_id: str
    ) -> TransactionDetails:
        """
        Get transaction details.

        Args:
            account_id: Account identifier
            transaction_id: Transaction identifier

        Returns:
            Transaction details
        """
        pass


class AISBalanceManager(ABC):
    """
    Abstract base class for balance management.

    This class defines the interface for balance-related operations
    including balance retrieval.
    """

    def __init__(self, ais_client: AISBaseClient) -> None:
        """
        Initialize the balance manager.

        Args:
            ais_client: The AIS client instance
        """
        self.ais_client = ais_client

    @abstractmethod
    def get_balances(self, account_id: str) -> BalanceList:
        """
        Get account balances.

        Args:
            account_id: Account identifier

        Returns:
            Account balances
        """
        pass

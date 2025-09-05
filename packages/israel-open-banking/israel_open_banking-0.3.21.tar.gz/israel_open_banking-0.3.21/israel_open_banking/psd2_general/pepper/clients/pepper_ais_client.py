from __future__ import annotations

from israel_open_banking.core.ais.general.models import AccountTransactionReport
from israel_open_banking.psd2_general.pepper.services.pepper_bank_service import PepperBankService

"""Pepper‑Bank concrete implementation of the PSD2 AIS abstraction layer.

This file wires the bank‑specific HTTP wrapper (``PepperBankService``)
into the generic AIS interfaces so the rest of the application can stay
vendor‑agnostic.

All network exceptions are captured and remapped to domain‑specific AIS
exceptions defined in ``israel_open_banking.core.ais.exceptions``.
"""

from datetime import date
from typing import Optional

from israel_open_banking.core.ais import (
    AccountDetails,
    AccountList,
    AISBaseClient,
    BalanceList,
    TransactionDetails,
    BookingStatus, )
from israel_open_banking.psd2_general.pepper.clients.pepper_account_manager import PepperAccountManager
from israel_open_banking.psd2_general.pepper.clients.pepper_balance_manager import PepperBalanceManager
from israel_open_banking.psd2_general.pepper.clients.pepper_transaction_manager import PepperTransactionManager


class PepperAISClient(AISBaseClient):
    """PSD2‑compliant AIS adapter for Pepper Bank."""

    def __init__(self, service: PepperBankService) -> None:
        super().__init__(client=None)  # We do not use a generic OpenBankingClient
        self._svc: PepperBankService = service

        # plug‑in concrete managers
        self.accounts: PepperAccountManager = PepperAccountManager(self)
        self.transactions: PepperTransactionManager = PepperTransactionManager(self)
        self.balances: PepperBalanceManager = PepperBalanceManager(self)

    def get_accounts(self, with_balance: bool = False) -> AccountList:  # noqa: D401
        return self.accounts.get_accounts(with_balance)

    def get_account_details(
            self, account_id: str, with_balance: bool = False
    ) -> AccountDetails:
        return self.accounts.get_account_details(account_id, with_balance)

    def get_balances(self, account_id: str) -> BalanceList:  # noqa: D401
        return self.balances.get_balances(account_id)

    def get_transactions(
            self,
            account_id: str,
            date_from: date,
            booking_status: BookingStatus = BookingStatus.BOOKED,
            date_to: Optional[date] = None,
            with_balance: bool = False,
            entry_reference_from: Optional[str] = None,
            delta_list: bool = False,
    ) -> AccountTransactionReport:
        return self.transactions.get_transactions(
            account_id,
            date_from,
            booking_status,
            date_to,
            with_balance,
            entry_reference_from,
            delta_list,
        )

    def get_transaction_details(
            self, account_id: str, transaction_id: str
    ) -> TransactionDetails:
        return self.transactions.get_transaction_details(account_id, transaction_id)

    @property
    def svc(self) -> PepperBankService:
        return self._svc

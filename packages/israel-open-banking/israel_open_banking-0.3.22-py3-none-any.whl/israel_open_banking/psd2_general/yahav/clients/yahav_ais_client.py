from __future__ import annotations

from israel_open_banking.core.ais.general.models import  AccountTransactionReport
from israel_open_banking.psd2_general.yahav.services.yahav_bank_service import YahavBankService

"""Yahav‑Bank concrete implementation of the PSD2 AIS abstraction layer.

This file wires the bank‑specific HTTP wrapper (``YahavBankService``)
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
from israel_open_banking.psd2_general.yahav.clients.yahav_account_manager import YahavAccountManager
from israel_open_banking.psd2_general.yahav.clients.yahav_balance_manager import YahavBalanceManager
from israel_open_banking.psd2_general.yahav.clients.yahav_transaction_manager import YahavTransactionManager


class YahavAISClient(AISBaseClient):
    """PSD2‑compliant AIS adapter for Yahav Bank."""

    def __init__(self, service: YahavBankService) -> None:
        super().__init__(client=None)  # We do not use a generic OpenBankingClient
        self._svc: YahavBankService = service

        # plug‑in concrete managers
        self.accounts: YahavAccountManager = YahavAccountManager(self)
        self.transactions: YahavTransactionManager = YahavTransactionManager(self)
        self.balances: YahavBalanceManager = YahavBalanceManager(self)

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
    def svc(self) -> YahavBankService:
        return self._svc

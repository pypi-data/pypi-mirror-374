from __future__ import annotations

from israel_open_banking.core.ais import BookingStatus
from israel_open_banking.core.ais.savings_and_loans.models import SavingAccountList, AccountDetailsSavingsLoans, \
    SavingBalanceList, SavingAccountTransactionReport
from israel_open_banking.psd2_savings_and_loans.savings.yahav.clients.yahav_savings_account_manager import \
    YahavSavingsAccountManager
from israel_open_banking.psd2_savings_and_loans.savings.yahav.clients.yahav_savings_balance_manager import \
    YahavSavingsBalanceManager
from israel_open_banking.psd2_savings_and_loans.savings.yahav.clients.yahav_savings_transaction_manager import \
    YahavSavingsTransactionManager
from israel_open_banking.psd2_savings_and_loans.savings.yahav.services.yahav_savings_bank_service import \
    YahavBankSavingsService

"""Yahav‑Bank concrete implementation of the PSD2 AIS abstraction layer.

This file wires the bank‑specific HTTP wrapper (``YahavBankService``)
into the generic AIS interfaces so the rest of the application can stay
vendor‑agnostic.

All network exceptions are captured and remapped to domain‑specific AIS
exceptions defined in ``open_banking_savings_and_loans.core.ais.exceptions``.
"""

from datetime import date
from typing import Optional

from israel_open_banking.core.ais.savings_and_loans import (
    AISSavingsBaseClient, )


class YahavAISSavingsClient(AISSavingsBaseClient):
    """PSD2‑compliant AIS adapter for Yahav Bank."""

    def __init__(self, service: YahavBankSavingsService) -> None:
        super().__init__(client=None)  # We do not use a generic OpenBankingClient
        self._svc: YahavBankSavingsService = service

        # plug‑in concrete managers
        self.accounts: YahavSavingsAccountManager = YahavSavingsAccountManager(self)
        self.transactions: YahavSavingsTransactionManager = YahavSavingsTransactionManager(self)
        self.balances: YahavSavingsBalanceManager = YahavSavingsBalanceManager(self)

    def get_accounts(self) -> SavingAccountList:
        return self.accounts.get_accounts()

    def get_account_details(self, savings_account_id: str) -> AccountDetailsSavingsLoans:
        return self.accounts.get_account_details(savings_account_id)

    def get_balances(
            self, saving_account_id: str
    ) -> SavingBalanceList:
        return self.balances.get_balances(saving_account_id)

    def get_transactions(
            self,
            savings_account_id: str,
            date_from: date,
            booking_status: BookingStatus,
            date_to: Optional[date] = None,
            entry_reference_from: str | None = None,
            delta_list: bool = False,
    ) -> SavingAccountTransactionReport:
        return self.transactions.get_transactions(
            savings_account_id,
            date_from,
            booking_status,
            date_to,
            entry_reference_from,
            delta_list,
        )

    # Expose the raw service for internal helpers ---------------------------------
    @property
    def svc(self) -> YahavBankSavingsService:
        return self._svc

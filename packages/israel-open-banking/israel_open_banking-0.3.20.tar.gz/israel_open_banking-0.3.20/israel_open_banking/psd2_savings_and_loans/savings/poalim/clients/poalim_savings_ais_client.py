from __future__ import annotations

from israel_open_banking.core.ais import BookingStatus
from israel_open_banking.core.ais.savings_and_loans.models import SavingAccountList, AccountDetailsSavingsLoans, \
    SavingBalanceList, SavingAccountTransactionReport
from israel_open_banking.psd2_savings_and_loans.savings.poalim.clients.poalim_savings_account_manager import \
    PoalimSavingsAccountManager
from israel_open_banking.psd2_savings_and_loans.savings.poalim.clients.poalim_savings_balance_manager import \
    PoalimSavingsBalanceManager
from israel_open_banking.psd2_savings_and_loans.savings.poalim.clients.poalim_savings_transaction_manager import \
    PoalimSavingsTransactionManager
from israel_open_banking.psd2_savings_and_loans.savings.poalim.services.poalim_savings_bank_service import \
    PoalimBankSavingsService

"""Poalim‑Bank concrete implementation of the PSD2 AIS abstraction layer.

This file wires the bank‑specific HTTP wrapper (``PoalimBankService``)
into the generic AIS interfaces so the rest of the application can stay
vendor‑agnostic.

All network exceptions are captured and remapped to domain‑specific AIS
exceptions defined in ``open_banking_savings_and_loans.core.ais.exceptions``.
"""

from datetime import date
from typing import Optional

from israel_open_banking.core.ais.savings_and_loans import (
    AISSavingsBaseClient, )


class PoalimAISSavingsClient(AISSavingsBaseClient):
    """PSD2‑compliant AIS adapter for Poalim Bank."""

    def __init__(self, service: PoalimBankSavingsService) -> None:
        super().__init__(client=None)  # We do not use a generic OpenBankingClient
        self._svc: PoalimBankSavingsService = service

        # plug‑in concrete managers
        self.accounts: PoalimSavingsAccountManager = PoalimSavingsAccountManager(self)
        self.transactions: PoalimSavingsTransactionManager = PoalimSavingsTransactionManager(self)
        self.balances: PoalimSavingsBalanceManager = PoalimSavingsBalanceManager(self)

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
    def svc(self) -> PoalimBankSavingsService:
        return self._svc

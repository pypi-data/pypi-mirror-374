from __future__ import annotations

from israel_open_banking.core.ais import BookingStatus
from israel_open_banking.core.ais.savings_and_loans.models import SavingAccountList, AccountDetailsSavingsLoans, \
    SavingBalanceList, SavingAccountTransactionReport
from israel_open_banking.psd2_savings_and_loans.savings.mercantile.clients.mercantile_savings_account_manager import \
    MercantileSavingsAccountManager
from israel_open_banking.psd2_savings_and_loans.savings.mercantile.clients.mercantile_savings_balance_manager import \
    MercantileSavingsBalanceManager
from israel_open_banking.psd2_savings_and_loans.savings.mercantile.clients.mercantile_savings_transaction_manager import \
    MercantileSavingsTransactionManager
from israel_open_banking.psd2_savings_and_loans.savings.mercantile.services.mercantile_savings_bank_service import \
    MercantileBankSavingsService

"""Mercantile‑Bank concrete implementation of the PSD2 AIS abstraction layer.

This file wires the bank‑specific HTTP wrapper (``MercantileBankService``)
into the generic AIS interfaces so the rest of the application can stay
vendor‑agnostic.

All network exceptions are captured and remapped to domain‑specific AIS
exceptions defined in ``open_banking_savings_and_loans.core.ais.exceptions``.
"""

from datetime import date
from typing import Optional

from israel_open_banking.core.ais.savings_and_loans import (
    AISSavingsBaseClient, )


class MercantileAISSavingsClient(AISSavingsBaseClient):
    """PSD2‑compliant AIS adapter for Mercantile Bank."""

    def __init__(self, service: MercantileBankSavingsService) -> None:
        super().__init__(client=None)  # We do not use a generic OpenBankingClient
        self._svc: MercantileBankSavingsService = service

        # plug‑in concrete managers
        self.accounts: MercantileSavingsAccountManager = MercantileSavingsAccountManager(self)
        self.transactions: MercantileSavingsTransactionManager = MercantileSavingsTransactionManager(self)
        self.balances: MercantileSavingsBalanceManager = MercantileSavingsBalanceManager(self)

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
    def svc(self) -> MercantileBankSavingsService:
        return self._svc

from __future__ import annotations

from israel_open_banking.core.ais import BookingStatus
from israel_open_banking.core.ais.savings_and_loans.base import AISLoansBaseClient
from israel_open_banking.core.ais.savings_and_loans.models import AccountDetailsSavingsLoans, \
    LoanAccountList, LoanBalanceList, LoanAccountTransactionReport
from israel_open_banking.psd2_savings_and_loans.loans.poalim.clients.poalim_loans_account_manager import \
    PoalimLoansAccountManager
from israel_open_banking.psd2_savings_and_loans.loans.poalim.clients.poalim_loans_balance_manager import \
    PoalimLoansBalanceManager
from israel_open_banking.psd2_savings_and_loans.loans.poalim.clients.poalim_loans_transaction_manager import \
    PoalimLoansTransactionManager
from israel_open_banking.psd2_savings_and_loans.loans.poalim.services.poalim_loans_bank_service import \
    PoalimBankLoansService

"""Poalim‑Bank concrete implementation of the PSD2 AIS abstraction layer.

This file wires the bank‑specific HTTP wrapper (``PoalimBankService``)
into the generic AIS interfaces so the rest of the application can stay
vendor‑agnostic.

All network exceptions are captured and remapped to domain‑specific AIS
exceptions defined in ``open_banking_savings_and_loans.core.ais.exceptions``.
"""

from datetime import date
from typing import Optional


class PoalimAISLoansClient(AISLoansBaseClient):
    """PSD2‑compliant AIS adapter for Poalim Bank."""

    def __init__(self, service: PoalimBankLoansService) -> None:
        super().__init__(client=None)  # We do not use a generic OpenBankingClient
        self._svc: PoalimBankLoansService = service

        # plug‑in concrete managers
        self.accounts: PoalimLoansAccountManager = PoalimLoansAccountManager(self)
        self.transactions: PoalimLoansTransactionManager = PoalimLoansTransactionManager(self)
        self.balances: PoalimLoansBalanceManager = PoalimLoansBalanceManager(self)

    def get_accounts(self) -> LoanAccountList:
        return self.accounts.get_accounts()

    def get_account_details(self, loan_account_id: str) -> AccountDetailsSavingsLoans:
        return self.accounts.get_account_details(loan_account_id)

    def get_balances(
            self, loan_account_id: str
    ) -> LoanBalanceList:
        return self.balances.get_balances(loan_account_id)

    def get_transactions(
            self,
            loan_account_id: str,
            date_from: date,
            booking_status: BookingStatus,
            date_to: Optional[date] = None,
            entry_reference_from: str | None = None,
            delta_list: bool = False,
    ) -> LoanAccountTransactionReport:
        return self.transactions.get_transactions(
            loan_account_id,
            date_from,
            booking_status,
            date_to,
            entry_reference_from,
            delta_list,
        )

    # Expose the raw service for internal helpers ---------------------------------
    @property
    def svc(self) -> PoalimBankLoansService:
        return self._svc

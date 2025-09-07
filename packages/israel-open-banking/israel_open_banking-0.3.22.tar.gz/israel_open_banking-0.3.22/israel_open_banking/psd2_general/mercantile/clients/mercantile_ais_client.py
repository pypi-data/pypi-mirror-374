from __future__ import annotations

from israel_open_banking.core.ais.general.models import AccountTransactionReport
from israel_open_banking.psd2_general.mercantile.services.mercantile_bank_service import MercantileBankService

"""Mercantile‑Bank concrete implementation of the PSD2 AIS abstraction layer.

This file wires the bank‑specific HTTP wrapper (``MercantileBankService``)
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
from israel_open_banking.psd2_general.mercantile.clients.mercantile_account_manager import MercantileAccountManager
from israel_open_banking.psd2_general.mercantile.clients.mercantile_balance_manager import MercantileBalanceManager
from israel_open_banking.psd2_general.mercantile.clients.mercantile_transaction_manager import MercantileTransactionManager


class MercantileAISClient(AISBaseClient):
    """PSD2‑compliant AIS adapter for Mercantile Bank."""

    def __init__(self, service: MercantileBankService) -> None:
        super().__init__(client=None)  # We do not use a generic OpenBankingClient
        self._svc: MercantileBankService = service

        # plug‑in concrete managers
        self.accounts: MercantileAccountManager = MercantileAccountManager(self)
        self.transactions: MercantileTransactionManager = MercantileTransactionManager(self)
        self.balances: MercantileBalanceManager = MercantileBalanceManager(self)

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
    def svc(self) -> MercantileBankService:
        return self._svc

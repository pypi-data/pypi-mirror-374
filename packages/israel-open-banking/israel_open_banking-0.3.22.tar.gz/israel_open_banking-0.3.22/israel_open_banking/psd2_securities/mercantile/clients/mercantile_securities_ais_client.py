from __future__ import annotations

from israel_open_banking.core.ais.securities.base import AISSecuritiesBaseClient
from israel_open_banking.core.ais.securities.enums import OrderStatusCode
from israel_open_banking.core.ais.securities.models import SecuritiesAccountList, SecuritiesAccountDetails, \
    SecuritiesAccountPositionsWrapper, SecuritiesTransactionsWrapper, SecuritiesTransaction, SecuritiesOrdersWrapper, \
    SecuritiesOrder
from israel_open_banking.psd2_securities.mercantile.clients.mercantile_securities_account_manager import \
    MercantileSecuritiesAccountManager
from israel_open_banking.psd2_securities.mercantile.clients.mercantile_securities_order_manager import \
    MercantileSecuritiesOrderManager
from israel_open_banking.psd2_securities.mercantile.clients.mercantile_securities_position_manager import \
    MercantileSecuritiesPositionManager
from israel_open_banking.psd2_securities.mercantile.clients.mercantile_securities_transaction_manager import \
    MercantileSecuritiesTransactionManager
from israel_open_banking.psd2_securities.mercantile.services.mercantile_securities_bank_service import \
    MercantileBankSecuritiesService

"""Mercantile‑Bank concrete implementation of the PSD2 AIS abstraction layer.

This file wires the bank‑specific HTTP wrapper (``MercantileBankService``)
into the generic AIS interfaces so the rest of the application can stay
vendor‑agnostic.

All network exceptions are captured and remapped to domain‑specific AIS
exceptions defined in ``open_banking_savings_and_loans.core.ais.exceptions``.
"""

from datetime import date
from typing import Optional


class MercantileAISSecuritiesClient(AISSecuritiesBaseClient):
    """PSD2‑compliant AIS adapter for Mercantile Bank."""

    def __init__(self, service: MercantileBankSecuritiesService) -> None:
        super().__init__(client=None)  # We do not use a generic OpenBankingClient
        self._svc: MercantileBankSecuritiesService = service

        # plug‑in concrete managers
        self.accounts: MercantileSecuritiesAccountManager = MercantileSecuritiesAccountManager(self)
        self.positions: MercantileSecuritiesPositionManager = MercantileSecuritiesPositionManager(self)
        self.transactions: MercantileSecuritiesTransactionManager = MercantileSecuritiesTransactionManager(self)
        self.orders: MercantileSecuritiesOrderManager = MercantileSecuritiesOrderManager(self)

    def get_accounts(self, evaluation_currency: Optional[str] = None) -> SecuritiesAccountList:
        return self.accounts.get_accounts(evaluation_currency)

    def get_account_details(
            self, securities_account_id: str,
            evaluation_currency: Optional[str] = None
    ) -> SecuritiesAccountDetails:
        return self.accounts.get_account_details(securities_account_id, evaluation_currency)

    def get_positions(self, securities_account_id: str) -> SecuritiesAccountPositionsWrapper:
        return self.positions.get_positions(securities_account_id)

    def get_transactions(
            self,
            securities_account_id: str,
            date_from: date,
            date_to: Optional[date] = None,
            entry_reference_from: Optional[str] = None,
            delta_list: bool = False,
    ) -> SecuritiesTransactionsWrapper:
        return self.transactions.get_transactions(
            securities_account_id,
            date_from,
            date_to,
            entry_reference_from,
            delta_list,
        )

    def get_transaction_details(
            self, securities_account_id: str, transaction_id: str
    ) -> SecuritiesTransaction:
        return self.transactions.get_transaction_details(securities_account_id, transaction_id)

    def get_orders(self, securities_account_id: str,
                   date_from: date,
                   date_to: Optional[date] = None,
                   order_status: Optional[OrderStatusCode] = None
                   ) -> SecuritiesOrdersWrapper:
        return self.orders.get_orders(
            securities_account_id,
            date_from,
            date_to,
            order_status
        )

    def get_order_details(
            self, securities_account_id: str, order_id: str
    ) -> SecuritiesOrder:
        return self.orders.get_order_details(securities_account_id, order_id)

    # Expose the raw service for internal helpers ---------------------------------
    @property
    def svc(self) -> MercantileBankSecuritiesService:
        return self._svc

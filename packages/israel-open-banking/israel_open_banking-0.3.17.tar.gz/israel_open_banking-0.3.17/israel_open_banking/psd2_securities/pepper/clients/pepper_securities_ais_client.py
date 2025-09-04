from __future__ import annotations

from israel_open_banking.core.ais.securities.base import AISSecuritiesBaseClient
from israel_open_banking.core.ais.securities.enums import OrderStatusCode
from israel_open_banking.core.ais.securities.models import SecuritiesAccountList, SecuritiesAccountDetails, \
    SecuritiesAccountPositionsWrapper, SecuritiesTransactionsWrapper, SecuritiesTransaction, SecuritiesOrdersWrapper, \
    SecuritiesOrder
from israel_open_banking.psd2_securities.pepper.clients.pepper_securities_account_manager import \
    PepperSecuritiesAccountManager
from israel_open_banking.psd2_securities.pepper.clients.pepper_securities_order_manager import \
    PepperSecuritiesOrderManager
from israel_open_banking.psd2_securities.pepper.clients.pepper_securities_position_manager import \
    PepperSecuritiesPositionManager
from israel_open_banking.psd2_securities.pepper.clients.pepper_securities_transaction_manager import \
    PepperSecuritiesTransactionManager
from israel_open_banking.psd2_securities.pepper.services.pepper_securities_bank_service import \
    PepperBankSecuritiesService

"""Pepper‑Bank concrete implementation of the PSD2 AIS abstraction layer.

This file wires the bank‑specific HTTP wrapper (``PepperBankService``)
into the generic AIS interfaces so the rest of the application can stay
vendor‑agnostic.

All network exceptions are captured and remapped to domain‑specific AIS
exceptions defined in ``open_banking_savings_and_loans.core.ais.exceptions``.
"""

from datetime import date
from typing import Optional


class PepperAISSecuritiesClient(AISSecuritiesBaseClient):
    """PSD2‑compliant AIS adapter for Pepper Bank."""

    def __init__(self, service: PepperBankSecuritiesService) -> None:
        super().__init__(client=None)  # We do not use a generic OpenBankingClient
        self._svc: PepperBankSecuritiesService = service

        # plug‑in concrete managers
        self.accounts: PepperSecuritiesAccountManager = PepperSecuritiesAccountManager(self)
        self.positions: PepperSecuritiesPositionManager = PepperSecuritiesPositionManager(self)
        self.transactions: PepperSecuritiesTransactionManager = PepperSecuritiesTransactionManager(self)
        self.orders: PepperSecuritiesOrderManager = PepperSecuritiesOrderManager(self)

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
    def svc(self) -> PepperBankSecuritiesService:
        return self._svc

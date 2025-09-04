from __future__ import annotations

from israel_open_banking.core.ais import BookingStatus
from israel_open_banking.core.ais.single_cards.models import CardAccountList, CardAccountDetails, CardBalanceList, \
    CardAccountTransactionReport
from israel_open_banking.psd2_single_cards.american_express.clients.american_express_single_cards_account_manager import \
    AmericanExpressSingleCardsManager
from israel_open_banking.psd2_single_cards.american_express.clients.american_express_single_cards_balance_manager import \
    AmericanExpressSingleCardsBalanceManager
from israel_open_banking.psd2_single_cards.american_express.clients.american_express_single_cards_transaction_manager import \
    AmericanExpressSingleCardsTransactionManager
from israel_open_banking.psd2_single_cards.american_express.services.american_express_single_cards_bank_service import AmericanExpressSingleCardsService

"""AmericanExpress‑Bank concrete implementation of the PSD2 AIS abstraction layer.

This file wires the bank‑specific HTTP wrapper (``AmericanExpressBankService``)
into the generic AIS interfaces so the rest of the application can stay
vendor‑agnostic.

All network exceptions are captured and remapped to domain‑specific AIS
exceptions defined in ``single_cards.core.ais.exceptions``.
"""

from datetime import date
from typing import Optional

from israel_open_banking.core.ais.single_cards import (AISSingleCardsBaseClient)


class AmericanExpressAISSingleCardsClient(AISSingleCardsBaseClient):
    """PSD2‑compliant AIS adapter for AmericanExpress Bank."""

    def __init__(self, service: AmericanExpressSingleCardsService) -> None:
        super().__init__(client=None)  # We do not use a generic OpenBankingClient
        self._svc: AmericanExpressSingleCardsService = service

        # plug‑in concrete managers
        self.cards: AmericanExpressSingleCardsManager = AmericanExpressSingleCardsManager(self)
        self.transactions: AmericanExpressSingleCardsTransactionManager = AmericanExpressSingleCardsTransactionManager(self)
        self.balances: AmericanExpressSingleCardsBalanceManager = AmericanExpressSingleCardsBalanceManager(self)

    def get_cards(self) -> CardAccountList:
        return self.cards.get_cards()

    def get_card_details(
            self, card_account_id: str
    ) -> CardAccountDetails:
        return self.cards.get_card_details(card_account_id)

    def get_balances(
            self, card_account_id: str,
            date_from: Optional[date] = None,
            value_date_from: Optional[date] = None
    ) -> CardBalanceList:
        return self.balances.get_balances(card_account_id, date_from, value_date_from)

    def get_transactions(
            self,
            card_account_id: str,
            date_from: Optional[date] = None,
            date_to: Optional[date] = None,
            value_date_from: Optional[date] = None,
            value_date_to: Optional[date] = None,
            booking_status: BookingStatus = BookingStatus.BOOKED,
            delta_list: bool = False,
    ) -> CardAccountTransactionReport:
        return self.transactions.get_transactions(
            card_account_id,
            date_from,
            date_to,
            value_date_from,
            value_date_to,
            booking_status,
            delta_list
        )

    @property
    def svc(self) -> AmericanExpressSingleCardsService:
        return self._svc

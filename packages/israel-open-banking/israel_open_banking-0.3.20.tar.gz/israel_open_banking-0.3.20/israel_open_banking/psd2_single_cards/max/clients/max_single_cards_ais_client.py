from __future__ import annotations

from israel_open_banking.core.ais import BookingStatus
from israel_open_banking.core.ais.single_cards.models import CardAccountList, CardAccountDetails, CardBalanceList, \
    CardAccountTransactionReport
from israel_open_banking.psd2_single_cards.max.clients.max_single_cards_account_manager import \
    MaxSingleCardsManager
from israel_open_banking.psd2_single_cards.max.clients.max_single_cards_balance_manager import \
    MaxSingleCardsBalanceManager
from israel_open_banking.psd2_single_cards.max.clients.max_single_cards_transaction_manager import \
    MaxSingleCardsTransactionManager
from israel_open_banking.psd2_single_cards.max.services.max_single_cards_bank_service import MaxSingleCardsService

"""Max‑Bank concrete implementation of the PSD2 AIS abstraction layer.

This file wires the bank‑specific HTTP wrapper (``MaxBankService``)
into the generic AIS interfaces so the rest of the application can stay
vendor‑agnostic.

All network exceptions are captured and remapped to domain‑specific AIS
exceptions defined in ``single_cards.core.ais.exceptions``.
"""

from datetime import date
from typing import Optional

from israel_open_banking.core.ais.single_cards import (AISSingleCardsBaseClient)


class MaxAISSingleCardsClient(AISSingleCardsBaseClient):
    """PSD2‑compliant AIS adapter for Max Bank."""

    def __init__(self, service: MaxSingleCardsService) -> None:
        super().__init__(client=None)  # We do not use a generic OpenBankingClient
        self._svc: MaxSingleCardsService = service

        # plug‑in concrete managers
        self.cards: MaxSingleCardsManager = MaxSingleCardsManager(self)
        self.transactions: MaxSingleCardsTransactionManager = MaxSingleCardsTransactionManager(self)
        self.balances: MaxSingleCardsBalanceManager = MaxSingleCardsBalanceManager(self)

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
    def svc(self) -> MaxSingleCardsService:
        return self._svc

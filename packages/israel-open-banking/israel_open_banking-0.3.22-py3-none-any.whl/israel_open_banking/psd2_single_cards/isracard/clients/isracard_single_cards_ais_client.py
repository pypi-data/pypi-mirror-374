from __future__ import annotations

from israel_open_banking.core.ais import BookingStatus
from israel_open_banking.core.ais.single_cards.models import CardAccountList, CardAccountDetails, CardBalanceList, \
    CardAccountTransactionReport
from israel_open_banking.psd2_single_cards.isracard.clients.isracard_single_cards_account_manager import \
    IsracardSingleCardsManager
from israel_open_banking.psd2_single_cards.isracard.clients.isracard_single_cards_balance_manager import \
    IsracardSingleCardsBalanceManager
from israel_open_banking.psd2_single_cards.isracard.clients.isracard_single_cards_transaction_manager import \
    IsracardSingleCardsTransactionManager
from israel_open_banking.psd2_single_cards.isracard.services.isracard_single_cards_bank_service import IsracardSingleCardsService

"""Isracard‑Bank concrete implementation of the PSD2 AIS abstraction layer.

This file wires the bank‑specific HTTP wrapper (``IsracardBankService``)
into the generic AIS interfaces so the rest of the application can stay
vendor‑agnostic.

All network exceptions are captured and remapped to domain‑specific AIS
exceptions defined in ``single_cards.core.ais.exceptions``.
"""

from datetime import date
from typing import Optional

from israel_open_banking.core.ais.single_cards import (AISSingleCardsBaseClient)


class IsracardAISSingleCardsClient(AISSingleCardsBaseClient):
    """PSD2‑compliant AIS adapter for Isracard Bank."""

    def __init__(self, service: IsracardSingleCardsService) -> None:
        super().__init__(client=None)  # We do not use a generic OpenBankingClient
        self._svc: IsracardSingleCardsService = service

        # plug‑in concrete managers
        self.cards: IsracardSingleCardsManager = IsracardSingleCardsManager(self)
        self.transactions: IsracardSingleCardsTransactionManager = IsracardSingleCardsTransactionManager(self)
        self.balances: IsracardSingleCardsBalanceManager = IsracardSingleCardsBalanceManager(self)

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
    def svc(self) -> IsracardSingleCardsService:
        return self._svc

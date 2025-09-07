from __future__ import annotations

from israel_open_banking.core.ais import BookingStatus
from israel_open_banking.core.ais.single_cards.models import CardAccountList, CardAccountDetails, CardBalanceList, \
    CardAccountTransactionReport
from israel_open_banking.psd2_single_cards.cal.clients.cal_single_cards_account_manager import \
    CalSingleCardsManager
from israel_open_banking.psd2_single_cards.cal.clients.cal_single_cards_balance_manager import \
    CalSingleCardsBalanceManager
from israel_open_banking.psd2_single_cards.cal.clients.cal_single_cards_transaction_manager import \
    CalSingleCardsTransactionManager
from israel_open_banking.psd2_single_cards.cal.services.cal_single_cards_bank_service import CalSingleCardsService

"""Cal‑Bank concrete implementation of the PSD2 AIS abstraction layer.

This file wires the bank‑specific HTTP wrapper (``CalBankService``)
into the generic AIS interfaces so the rest of the application can stay
vendor‑agnostic.

All network exceptions are captured and remapped to domain‑specific AIS
exceptions defined in ``single_cards.core.ais.exceptions``.
"""

from datetime import date
from typing import Optional

from israel_open_banking.core.ais.single_cards import (AISSingleCardsBaseClient)


class CalAISSingleCardsClient(AISSingleCardsBaseClient):
    """PSD2‑compliant AIS adapter for Cal Bank."""

    def __init__(self, service: CalSingleCardsService) -> None:
        super().__init__(client=None)  # We do not use a generic OpenBankingClient
        self._svc: CalSingleCardsService = service

        # plug‑in concrete managers
        self.cards: CalSingleCardsManager = CalSingleCardsManager(self)
        self.transactions: CalSingleCardsTransactionManager = CalSingleCardsTransactionManager(self)
        self.balances: CalSingleCardsBalanceManager = CalSingleCardsBalanceManager(self)

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
    def svc(self) -> CalSingleCardsService:
        return self._svc

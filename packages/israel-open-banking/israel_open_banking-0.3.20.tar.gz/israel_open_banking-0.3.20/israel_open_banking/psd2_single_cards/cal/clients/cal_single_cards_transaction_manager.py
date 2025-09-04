from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Optional

from israel_open_banking.core.ais import BookingStatus
from israel_open_banking.core.ais.single_cards import AISSingleCardsTransactionManager, \
    AISTransactionSingleCardsException
from israel_open_banking.core.ais.single_cards.models import CardAccountTransactionReport
from israel_open_banking.core.exceptions import raise_from_response

if TYPE_CHECKING:
    from israel_open_banking.psd2_single_cards.cal.clients.cal_single_cards_ais_client import CalAISSingleCardsClient


class CalSingleCardsTransactionManager(AISSingleCardsTransactionManager):
    def __init__(self, ais_client: CalAISSingleCardsClient) -> None:  # noqa: D401
        super().__init__(ais_client)
        self.ais_client: CalAISSingleCardsClient = ais_client

    # --------------------------------------------------------------------- #

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
        resp = self.ais_client.svc.get_transactions(
            card_account_id,
            date_from,
            date_to,
            value_date_from,
            value_date_to,
            booking_status,
            delta_list
        )
        if resp.status_code >= 400:
            raise_from_response(resp, AISTransactionSingleCardsException)
        return CardAccountTransactionReport.model_validate_json(resp.text)

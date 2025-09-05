from __future__ import annotations

import json
from datetime import date
from typing import TYPE_CHECKING, Optional

from israel_open_banking.core.ais import BookingStatus
from israel_open_banking.core.ais.single_cards import AISSingleCardsTransactionManager, \
    AISTransactionSingleCardsException
from israel_open_banking.core.ais.single_cards.models import CardAccountTransactionReport
from israel_open_banking.core.exceptions import raise_from_response

if TYPE_CHECKING:
    from israel_open_banking.psd2_single_cards.isracard.clients.isracard_single_cards_ais_client import \
        IsracardAISSingleCardsClient


class IsracardSingleCardsTransactionManager(AISSingleCardsTransactionManager):
    def __init__(self, ais_client: IsracardAISSingleCardsClient) -> None:  # noqa: D401
        super().__init__(ais_client)
        self.ais_client: IsracardAISSingleCardsClient = ais_client

    # --------------------------------------------------------------------- #

    import json
    from typing import Optional
    from datetime import date
    # from your_module import BookingStatus, AISTransactionSingleCardsException, CardAccountTransactionReport

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
            delta_list,
        )
        if resp.status_code >= 400:
            raise_from_response(resp, AISTransactionSingleCardsException)

        # TODO: Remove this once the API is fixed
        # Parse the FULL payload
        payload = json.loads(resp.text)

        # Normalize field typos inside booked & pending, if present
        card_tx = payload.get("cardTransactions") or {}
        self.normalize_transaction_fields(card_tx.get("booked") or [])
        self.normalize_transaction_fields(card_tx.get("pending") or [])

        # Validate the WHOLE payload against the top-level model
        return CardAccountTransactionReport.model_validate(payload)
        # return CardAccountTransactionReport.model_validate_json(resp.text)


    def normalize_transaction_fields(self, transactions: list[dict]) -> None:
        if not isinstance(transactions, list):
            return
        for tx in transactions:
            addr = tx.get("cardAcceptorAddress")
            if isinstance(addr, dict) and "buildingnNumber" in addr:
                addr["buildingNumber"] = addr.pop("buildingnNumber")



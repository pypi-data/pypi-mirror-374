from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Optional

from israel_open_banking.core.ais.single_cards import AISSingleCardsBalanceManager
from israel_open_banking.core.ais.single_cards.exceptions import AISBalanceSingleCardsException
from israel_open_banking.core.ais.single_cards.models import CardBalanceList
from israel_open_banking.core.exceptions import raise_from_response

if TYPE_CHECKING:
    from israel_open_banking.psd2_single_cards.american_express.clients.american_express_single_cards_ais_client import AmericanExpressAISSingleCardsClient


class AmericanExpressSingleCardsBalanceManager(AISSingleCardsBalanceManager):
    """Handles /accounts/{id}/balances endpoints for AmericanExpress."""

    def __init__(self, ais_client: AmericanExpressAISSingleCardsClient) -> None:
        super().__init__(ais_client)
        self.ais_client: AmericanExpressAISSingleCardsClient = ais_client

    # --------------------------------------------------------------------- #

    def get_balances(self, card_account_id: str,
                     date_from: Optional[date] = None,
                     value_date_from: Optional[date] = None
                     ) -> CardBalanceList:
        resp = self.ais_client.svc.get_balances(card_account_id, date_from=date_from, value_date_from=value_date_from)
        if resp.status_code >= 400:
            raise_from_response(resp, AISBalanceSingleCardsException)
        return CardBalanceList.model_validate_json(resp.text)

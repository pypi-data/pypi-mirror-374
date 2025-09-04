from typing import TYPE_CHECKING

from israel_open_banking.core.ais.single_cards import AISSingleCardsManager, AISAccountSingleCardsException
from israel_open_banking.core.ais.single_cards.models import CardAccountList, CardAccountDetails
from israel_open_banking.core.exceptions import raise_from_response

if TYPE_CHECKING:
    from israel_open_banking.psd2_single_cards.isracard.clients.isracard_single_cards_ais_client import \
        IsracardAISSingleCardsClient


class IsracardSingleCardsManager(AISSingleCardsManager):
    def __init__(self, ais_client: "IsracardAISSingleCardsClient") -> None:
        super().__init__(ais_client)
        self.ais_client: "IsracardAISSingleCardsClient" = ais_client

    def get_cards(self) -> CardAccountList:
        resp = self.ais_client.svc.get_cards()
        if resp.status_code >= 400:
            raise_from_response(resp, AISAccountSingleCardsException)
        return CardAccountList.model_validate_json(resp.text)

    def get_card_details(
            self, card_account_id: str
    ) -> CardAccountDetails:
        resp = self.ais_client.svc.get_card_details(card_account_id)
        if resp.status_code >= 400:
            raise_from_response(resp, AISAccountSingleCardsException)
        return CardAccountDetails.model_validate(resp.json()["card"])

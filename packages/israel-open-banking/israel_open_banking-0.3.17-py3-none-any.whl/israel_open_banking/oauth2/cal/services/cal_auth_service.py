import requests

from israel_open_banking.config import get_config

config = get_config()

from israel_open_banking.core.ssl_adapter import send_post_request


class CalAuthService:
    def __init__(self, refresh_token: str, token_endpoint: str) -> None:
        self.refresh_token = refresh_token
        self.token_endpoint = token_endpoint

        self.qwac_cert = config.SHAVVE_QWAC_CERT_PEM_PATH
        self.qwac_key = config.SHAVVE_QWAC_KEY_PATH
        self.qwac_pw = config.SHAVVE_QWAC_KEY_PW

        self.ca_cert = config.CAL_CA_CERT_PATH

    def refresh_access_token(self) -> requests.Response:
        body = (f'grant_type=refresh_token'
                f'&refresh_token={self.refresh_token}'
                f'&client_id={config.OPEN_BANKING_CLIENT_ID}')

        return send_post_request(
            self.token_endpoint,
            {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body,
            self.qwac_cert,
            self.qwac_key,
            self.qwac_pw,
            self.ca_cert
        )

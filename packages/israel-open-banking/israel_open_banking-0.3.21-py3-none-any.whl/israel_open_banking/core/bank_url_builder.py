from israel_open_banking.core import BaseModel


class BankUrlBuilder(BaseModel):
    api_base_url: str

    def build_url(self, endpoint: str) -> str:
        return f"{self.api_base_url}/{endpoint.strip('/')}"

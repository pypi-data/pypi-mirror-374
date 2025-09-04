from pydantic_settings import BaseSettings

from israel_open_banking.core.exceptions import ValidationError


class Config(BaseSettings):
    # Base API Configuration
    OPEN_BANKING_API_BASE_URL: str
    OPEN_BANKING_CLIENT_ID: str
    OPEN_BANKING_CLIENT_SECRET: str
    OPEN_BANKING_REDIRECT_URI: str

    # API Settings
    OPEN_BANKING_API_TIMEOUT: int
    OPEN_BANKING_API_RETRY_ATTEMPTS: int

    # Logging Configuration
    OPEN_BANKING_LOG_LEVEL: str
    OPEN_BANKING_LOG_FORMAT: str

    # Development Settings
    OPEN_BANKING_DEBUG: bool
    OPEN_BANKING_MOCK_RESPONSES: bool

    TPP_REDIRECT_URI: str

    # Discount Configuration
    DISCOUNT_CA_CERT_PATH: str
    DISCOUNT_API_URL: str
    DISCOUNT_SAVINGS_AND_LOANS_API_URL: str
    DISCOUNT_SECURITIES_API_URL: str

    # Leumi Configuration
    LEUMI_CA_CERT_PATH: str
    LEUMI_API_URL: str
    LEUMI_SAVINGS_AND_LOANS_API_URL: str
    LEUMI_SECURITIES_API_URL: str

    # Mizrahi Configuration
    MIZRAHI_CA_CERT_PATH: str
    MIZRAHI_API_URL: str
    MIZRAHI_SAVINGS_AND_LOANS_API_URL: str
    MIZRAHI_SECURITIES_API_URL: str

    # Pepper Configuration
    PEPPER_CA_CERT_PATH: str
    PEPPER_API_URL: str
    PEPPER_SAVINGS_AND_LOANS_API_URL: str
    PEPPER_SECURITIES_API_URL: str

    # Poalim Configuration
    POALIM_CA_CERT_PATH: str
    POALIM_API_URL: str
    POALIM_SAVINGS_AND_LOANS_API_URL: str
    POALIM_SECURITIES_API_URL: str

    # Yahav Configuration
    YAHAV_CA_CERT_PATH: str
    YAHAV_API_URL: str
    YAHAV_SAVINGS_AND_LOANS_API_URL: str
    YAHAV_SECURITIES_API_URL: str

    # --------------------------------- Single Cards Configuration ---------------------------------

    # Cal Configuration
    CAL_CA_CERT_PATH: str
    CAL_API_URL: str
    CAL_LOANS_API_URL: str

    # Meitav Configuration
    MEITAV_CA_CERT_PATH: str
    MEITAV_SAVINGS_AND_LOANS_API_URL: str

    # Fibi Configuration
    FIBI_API_URL: str
    FIBI_CA_CERT_PATH: str
    FIBI_SAVINGS_AND_LOANS_API_URL: str
    FIBI_SECURITIES_API_URL: str

    # Isracard Configuration
    ISRACARD_API_URL: str
    ISRACARD_CA_CERT_PATH: str
    ISRACARD_LOANS_API_URL: str

    # Mercantile Configuration
    MERCANTILE_CA_CERT_PATH: str
    MERCANTILE_SAVINGS_AND_LOANS_API_URL: str
    MERCANTILE_API_URL: str
    MERCANTILE_SECURITIES_API_URL: str

    # One Zero Configuration
    ONE_ZERO_CA_CERT_PATH: str
    ONE_ZERO_API_URL: str

    # American Express Configuration
    AMERICAN_EXPRESS_API_URL: str
    AMERICAN_EXPRESS_CA_CERT_PATH: str
    AMERICAN_EXPRESS_LOANS_API_URL: str

    # Max Configuration
    MAX_CA_CERT_PATH: str
    MAX_API_URL: str
    MAX_LOANS_API_URL: str

    # Bit Configuration
    BIT_API_URL: str
    BIT_CA_CERT_PATH: str
    BIT_SAVINGS_API_URL: str

    # Open banking
    SHAVVE_QSEAL_KEY_PW: str
    SHAVVE_QSEAL_KEY_PATH: str
    SHAVVE_QSEAL_CERT_PEM_PATH: str

    SHAVVE_QWAC_KEY_PW: str
    SHAVVE_QWAC_KEY_PATH: str
    SHAVVE_QWAC_CERT_PEM_PATH: str


_config_instance: Config | None = None


def get_config() -> Config:
    global _config_instance
    if _config_instance is None:
        try:
            _config_instance = Config()
        except ValidationError as e:
            raise RuntimeError("Missing or invalid environment configuration") from e
    return _config_instance

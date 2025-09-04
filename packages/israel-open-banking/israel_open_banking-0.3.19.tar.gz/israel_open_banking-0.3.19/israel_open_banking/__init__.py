"""
Israel Open Banking SDK

An open-source SDK for Israeli Open Banking APIs, providing connectors for
multiple suppliers including credit cards, banks, and other financial institutions.
"""

__version__ = "0.1.0"
__author__ = "Shavve"
__email__ = "admin@shavve.io"

from israel_open_banking.core.client import OpenBankingClient
from israel_open_banking.core.config import OpenBankingConfig
from israel_open_banking.core.exceptions import OpenBankingException

__all__ = [
    "OpenBankingClient",
    "OpenBankingConfig",
    "OpenBankingException",
    "__version__",
]

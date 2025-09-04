"""
PSD2 AIS Enums.

This module contains all the enums used in the PSD2 Account Information Services
based on the Berlin Group NextGenPSD2 Framework v1.3.14 specification.
"""

from enum import Enum

class InterestType(str, Enum):
    """Interest type enumeration."""

    FIXD = "FIXD"  # Fixed interest rate
    INDE = "INDE"  # Indexed interest rate
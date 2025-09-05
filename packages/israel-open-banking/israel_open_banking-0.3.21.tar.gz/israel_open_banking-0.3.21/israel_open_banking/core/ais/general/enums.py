"""
PSD2 AIS Enums.

This module contains all the enums used in the PSD2 Account Information Services
based on the Berlin Group NextGenPSD2 Framework v1.3.14 specification.
"""

from enum import Enum


class AccountStatus(str, Enum):
    """Account status enumeration."""

    ENABLED = "enabled"
    DELETED = "deleted"
    BLOCKED = "blocked"


class AccountUsage(str, Enum):
    """Account usage enumeration."""

    PRIV = "PRIV"  # Private personal account
    ORGA = "ORGA"  # Professional account


class AuthenticationType(str, Enum):
    """Authentication type enumeration."""

    SMS_OTP = "SMS_OTP"  # SMS OTP
    CHIP_OTP = "CHIP_OTP"  # Chip card OTP
    PHOTO_OTP = "PHOTO_OTP"  # QR code OTP
    PUSH_OTP = "PUSH_OTP"  # Push OTP to app
    SMTP_OTP = "SMTP_OTP"  # Email OTP


class BookingStatus(str, Enum):
    """Booking status enumeration."""

    BOOKED = "booked"  # Booked transactions
    PENDING = "pending"  # Pending transactions
    BOTH = "both"  # Both booked and pending
    INFORMATION = "information"  # Information only
    ALL = "all"  # All transactions, including information only


class CashAccountType(str, Enum):
    """Cash account type enumeration."""

    CACC = "CACC"  # Current account
    CASH = "CASH"  # Cash account
    CHAR = "CHAR"  # Charges account
    CISH = "CISH"  # Commission account
    COMM = "COMM"  # Commission account
    CPAC = "CPAC"  # Cash payment account
    LLSV = "LLSV"  # Limited liquidity savings account
    LOAN = "LOAN"  # Loan account
    MGLD = "MGLD"  # Margin lending account
    MOMA = "MOMA"  # Money market account
    NREX = "NREX"  # Non-resident external account
    ODFT = "ODFT"  # Overdraft account
    ONDP = "ONDP"  # Overnight deposit account
    OTHR = "OTHR"  # Other account
    SACC = "SACC"  # Settlement account
    SLRY = "SLRY"  # Salary account
    SVGS = "SVGS"  # Savings account
    TAXE = "TAXE"  # Tax account
    TRAN = "TRAN"  # Transaction account
    TRAS = "TRAS"  # Treasury account
    VACC = "VACC"  # Vacation account
    WEAL = "WEAL"  # Wealth management account
    SCTS = "SCTS"  # Securities account


class ConsentStatus(str, Enum):
    """Consent status enumeration."""

    RECEIVED = "received"  # Consent received but not authorized
    REJECTED = "rejected"  # Consent rejected
    VALID = "valid"  # Consent valid and active
    REVOKED_BY_PSU = "revokedByPsu"  # Consent revoked by PSU
    EXPIRED = "expired"  # Consent expired
    TERMINATED_BY_TPP = "terminatedByTpp"  # Consent terminated by TPP
    PARTIALLY_AUTHORIZED = "partiallyAuthorised"  # Partially authorized


class TransactionStatus(str, Enum):
    """Transaction status enumeration based on ISO 20022."""

    ACCC = "ACCC"  # AcceptedSettlementCompleted
    ACCP = "ACCP"  # AcceptedCustomerProfile
    ACSC = "ACSC"  # AcceptedSettlementCompleted
    ACSP = "ACSP"  # AcceptedSettlementInProcess
    ACTC = "ACTC"  # AcceptedTechnicalValidation
    ACWC = "ACWC"  # AcceptedWithChange
    ACWP = "ACWP"  # AcceptedWithoutPosting
    RCVD = "RCVD"  # Received
    PDNG = "PDNG"  # Pending
    RJCT = "RJCT"  # Rejected
    CANC = "CANC"  # Cancelled
    ACFC = "ACFC"  # AcceptedFundsChecked
    PATC = "PATC"  # PartiallyAcceptedTechnical
    PART = "PART"  # PartiallyAccepted


class BalanceType(str, Enum):
    """Balance type enumeration."""

    CLOSING_BOOKED = "closingBooked"  # Closing booked balance
    EXPECTED = "expected"  # Expected balance
    AUTHORISED = "authorised"  # Authorised balance
    OPENING_BOOKED = "openingBooked"  # Opening booked balance
    INTERIM_AVAILABLE = "interimAvailable"  # Interim available balance
    FORWARD_AVAILABLE = "forwardAvailable"  # Forward available balance
    CLOSING_AVAILABLE = "closingAvailable"  # Closing available balance
    INTERIM_BOOKED = "interimBooked"  # Interim booked balance
    FORWARD_BOOKED = "forwardBooked"  # Forward booked balance
    PREVIOUSLY_CLOSED_BOOKED = (
        "previouslyClosedBooked"  # Previously closed booked balance
    )
    CLOSING_CLEARED = "closingCleared"  # Closing cleared balance
    INTERIM_CLEARED = "interimCleared"  # Interim cleared balance
    OPENING_CLEARED = "openingCleared"  # Opening cleared balance
    UNKNOWN = "unknown"  # Unknown balance type


class FrequencyCode(str, Enum):
    """Frequency code enumeration."""

    DAILY = "Daily"
    WEEKLY = "Weekly"
    EVERYTWOWEEKS = "EveryTwoWeeks"
    MONTHLY = "Monthly"
    EVERYTWOMONTHS = "EveryTwoMonths"
    QUARTERLY = "Quarterly"
    SEMIANNUAL = "SemiAnnual"
    ANNUAL = "Annual"
    MONTHLYVARIABLE = "MonthlyVariable"


class DayOfExecution(int, Enum):
    """Day of execution enumeration."""

    DAY_1 = 1
    DAY_2 = 2
    DAY_3 = 3
    DAY_4 = 4
    DAY_5 = 5
    DAY_6 = 6
    DAY_7 = 7
    DAY_8 = 8
    DAY_9 = 9
    DAY_10 = 10
    DAY_11 = 11
    DAY_12 = 12
    DAY_13 = 13
    DAY_14 = 14
    DAY_15 = 15
    DAY_16 = 16
    DAY_17 = 17
    DAY_18 = 18
    DAY_19 = 19
    DAY_20 = 20
    DAY_21 = 21
    DAY_22 = 22
    DAY_23 = 23
    DAY_24 = 24
    DAY_25 = 25
    DAY_26 = 26
    DAY_27 = 27
    DAY_28 = 28


class ExecutionRule(str, Enum):
    """Execution rule enumeration."""

    FOLLOWING = "following"  # Following business day
    PRECEDING = "preceding"  # Preceding business day


class TppMessageCategory(str, Enum):
    """TPP message category enumeration."""

    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class DebitAccounting(str, Enum):
    """Debit accounting enumeration."""

    TRUE = "true"
    FALSE = "false"


class ChequeTypeCode(str, Enum):
    """Cheque type code enumeration."""

    CCHQ = "CCHQ"  # Customer cheque
    CCCH = "CCCH"  # Customer counter cheque
    BCHQ = "BCHQ"  # Bank cheque
    DRFT = "DRFT"  # Draft
    ELDR = "ELDR"  # Electronic draft


class ChequeDepositStatus(str, Enum):
    """Cheque deposit status enumeration."""

    DEPOSITED = "deposited"
    IN_PROCESS = "inProcess"
    RETURNED = "returned"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    COMPLETED = "completed"


class PurposeCode(str, Enum):
    """Purpose code enumeration."""

    # Common purpose codes (ISO 20022)
    CASH = "CASH"  # Cash management
    COLL = "COLL"  # Collection
    CORT = "CORT"  # Treasury payment
    CPKC = "CPKC"  # Card bulk clearing
    DCRD = "DCRD"  # Credit card payment
    DIVI = "DIVI"  # Dividend
    DVPM = "DVPM"  # Delayed payment
    EDU = "EDU"  # Education
    ESTX = "ESTX"  # Estate tax
    GOVT = "GOVT"  # Government payment
    HEDG = "HEDG"  # Hedging
    INTC = "INTC"  # Intra-company payment
    INTE = "INTE"  # Interest
    LBRI = "LBRI"  # Labor insurance
    LIFI = "LIFI"  # Life insurance
    LOAN = "LOAN"  # Loan
    LOAR = "LOAR"  # Loan repayment
    PENO = "PENO"  # Pension payment
    PENS = "PENS"  # Pension
    SALA = "SALA"  # Salary payment
    SECU = "SECU"  # Securities
    SSBE = "SSBE"  # Social security benefit
    SUPP = "SUPP"  # Supplier payment
    TAXS = "TAXS"  # Tax payment
    TRAD = "TRAD"  # Trade
    TREA = "TREA"  # Treasury
    VATX = "VATX"  # VAT payment
    HPAY = "HPAY"  # Home payment
    INSU = "INSU"  # Insurance premium
    INVS = "INVS"  # Investment
    PROP = "PROP"  # Property
    RENT = "RENT"  # Rent
    SUBS = "SUBS"  # Subscription
    UTIL = "UTIL"  # Utility payment


class Aspsp(str, Enum):
    DISCOUNT = 'DISCOUNT'
    POALIM = 'POALIM'
    LEUMI = 'LEUMI'
    MIZRAHI = 'MIZRAHI'
    PEPPER = 'PEPPER'
    YAHAV = 'YAHAV'
    CAL = 'CAL'
    MEITAV = 'MEITAV'
    ONE_ZERO = 'ONE_ZERO'
    MASSAD = 'MASSAD',
    FIBI_OTZAR = 'FIBI_OTZAR',
    FIBI_UBANK = 'FIBI_UBANK',
    FIBI_BNL = 'FIBI_BNL',
    FIBI_PAGI = 'FIBI_PAGI',
    ISRACARD = 'ISRACARD'
    MERCANTILE = 'MERCANTILE'
    AMEX = 'AMEX'
    MAX = 'MAX'
    BIT = 'BIT'

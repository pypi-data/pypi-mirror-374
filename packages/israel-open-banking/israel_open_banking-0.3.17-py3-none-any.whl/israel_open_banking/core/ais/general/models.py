"""
PSD2 AIS Models.

This module contains all the Pydantic models used in the PSD2 Account Information Services
based on the Berlin Group NextGenPSD2 Framework v1.3.14 specification.
"""

from datetime import date, datetime
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, AliasChoices, model_validator

from .enums import (
    AccountStatus,
    AccountUsage,
    AuthenticationType,
    BalanceType,
    CashAccountType,
    ConsentStatus,
    TppMessageCategory,
)


class HrefType(BaseModel):
    """Href type for links."""

    model_config = ConfigDict(extra="forbid")

    href: str = Field(..., description="Href for the link")


class Links(BaseModel):
    """Links model for navigation."""

    model_config = ConfigDict(extra="allow")

    accounts: HrefType | None = Field(None, description="Link to account")
    account: HrefType | None = Field(None, description="Link to account")
    loan_account: HrefType | None = Field(None, alias="loanAccount")
    balances: HrefType | None = Field(None, description="Link to balances")
    transactions: HrefType | None = Field(None, description="Link to transactions")
    transaction_details: HrefType | None = Field(
        None, alias="transactionDetails", description="Link to transaction details"
    )
    card_account: HrefType | None = Field(
        None, alias="cardAccount", description="Link to card account"
    )
    card_transactions: HrefType | None = Field(
        None, alias="cardTransactions", description="Link to card transactions"
    )
    first: HrefType | None = Field(None, description="Link to first page")
    next: HrefType | None = Field(None, description="Link to next page")
    previous: HrefType | None = Field(None, description="Link to previous page")
    last: HrefType | None = Field(None, description="Link to last page")
    download: HrefType | None = Field(None, description="Link to download")
    start_authorisation: HrefType | None = Field(
        None, alias="startAuthorisation", description="Link to start authorization"
    )
    start_authorisation_with_psu_authentication: HrefType | None = Field(
        None,
        alias="startAuthorisationWithPsuAuthentication",
        description="Link to start authorization with PSU authentication",
    )
    start_authorisation_with_authentication_method_selection: HrefType | None = Field(
        None,
        alias="startAuthorisationWithAuthenticationMethodSelection",
        description="Link to start authorization with authentication method selection",
    )
    start_authorisation_with_transaction_authorisation: HrefType | None = Field(
        None,
        alias="startAuthorisationWithTransactionAuthorisation",
        description="Link to start authorization with transaction authorization",
    )
    start_authorisation_with_psu_identification: HrefType | None = Field(
        None,
        alias="startAuthorisationWithPsuIdentification",
        description="Link to start authorization with PSU identification",
    )
    start_authorisation_with_psu_data: HrefType | None = Field(
        None,
        alias="startAuthorisationWithPsuData",
        description="Link to start authorization with PSU data",
    )
    select_authentication_method: HrefType | None = Field(
        None,
        alias="selectAuthenticationMethod",
        description="Link to select authentication method",
    )
    authorise_transaction: HrefType | None = Field(
        None, alias="authoriseTransaction", description="Link to authorize transaction"
    )
    sca_status: HrefType | None = Field(
        None, alias="scaStatus", description="Link to SCA status"
    )
    update_psu_authentication: HrefType | None = Field(
        None,
        alias="updatePsuAuthentication",
        description="Link to update PSU authentication",
    )
    update_additional_psu_authentication: HrefType | None = Field(
        None,
        alias="updateAdditionalPsuAuthentication",
        description="Link to update additional PSU authentication",
    )
    update_psu_identification: HrefType | None = Field(
        None,
        alias="updatePsuIdentification",
        description="Link to update PSU identification",
    )
    update_additional_psu_identification: HrefType | None = Field(
        None,
        alias="updateAdditionalPsuIdentification",
        description="Link to update additional PSU identification",
    )
    update_psu_data: HrefType | None = Field(
        None, alias="updatePsuData", description="Link to update PSU data"
    )
    update_additional_psu_data: HrefType | None = Field(
        None,
        alias="updateAdditionalPsuData",
        description="Link to update additional PSU data",
    )
    status: HrefType | None = Field(None, description="Link to status")
    account_report: HrefType | None = Field(
        None, alias="accountReport", description="Link to account report"
    )
    card_account_report: HrefType | None = Field(
        None, alias="cardAccountReport", description="Link to card account report"
    )


class TppMessage(BaseModel):
    """TPP message model."""

    model_config = ConfigDict(extra="forbid")

    category: TppMessageCategory = Field(..., description="Message category")
    code: str = Field(..., description="Message code")
    path: str | None = Field(None, description="Message path")
    text: str | None = Field(None, description="Message text")


class Amount(BaseModel):
    """Amount model."""

    model_config = ConfigDict(extra="forbid")

    currency: str = Field(..., description="Currency code (ISO 4217)")
    amount: str = Field(..., description="Amount as string")

    @field_validator("amount", mode="before")
    def validate_and_parse_amount(cls, v):
        """
        Ensure the value can be parsed to a number.
        If it is numeric, store it as an integer string.
        """
        try:
            if v == "":
                return ""
            # Try integer parsing first
            num = int(float(v))
        except (ValueError, TypeError):
            raise ValueError(f"Invalid amount: {v!r}. Must be numeric.")

        return str(num)


class ExchangeRate(BaseModel):
    """Exchange rate model."""

    model_config = ConfigDict(extra="forbid")

    source_currency: str = Field(
        ..., alias="sourceCurrency", description="Source currency"
    )
    target_currency: str = Field(
        ..., alias="targetCurrency", description="Target currency"
    )
    exchange_rate: str = Field(..., alias="exchangeRate", description="Exchange rate")
    contract_identification: str | None = Field(
        None, alias="contractIdentification", description="Contract identification"
    )
    quotation_date: datetime | None = Field(
        None, alias="quotationDate", description="Quotation date"
    )
    requested_currency: str | None = Field(
        None, alias="requestedCurrency", description="Requested currency"
    )
    unit_currency: str | None = Field(
        None, alias="unitCurrency", description="Unit currency"
    )


class ExchangeRateList(BaseModel):
    """Exchange rate list model."""

    model_config = ConfigDict(extra="forbid")

    exchange_rate: list[ExchangeRate] = Field(
        ..., alias="exchangeRate", description="List of exchange rates"
    )


class Address(BaseModel):
    """Address model."""

    model_config = ConfigDict(extra="forbid")

    street_name: str | None = Field(None, alias="streetName", description="Street name")
    building_number: str | None = Field(
        None, alias="buildingNumber", description="Building number"
    )
    town_name: str | None = Field(None, alias="townName", description="Town name")
    post_code: str | None = Field(None, alias="postCode", description="Post code")
    country: str = Field(..., description="Country code in ISO 3166-1 alpha-2 format", alias="country",
                         pattern=r'^[A-Z]{2}$')
    city: str | None = Field(None, description="City name")


class BankTransactionCode(BaseModel):
    """Bank transaction code model."""

    model_config = ConfigDict(extra="forbid")

    domain: str | None = Field(None, description="Domain code")
    family: str | None = Field(None, description="Family code")
    sub_family: str | None = Field(
        None, alias="subFamily", description="Sub-family code"
    )


class AccountReference(BaseModel):
    """Account reference model."""

    model_config = ConfigDict(extra="allow")

    iban: str | None = Field(None, description="IBAN")
    bban: str | None = Field(None, description="BBAN")
    pan: str | None = Field(None, description="PAN")
    masked_pan: str | None = Field(None, alias="maskedPan", description="Masked PAN")
    msisdn: str | None = Field(None, description="MSISDN")
    currency: str | None = Field(None, description="Currency code")
    cash_account_type: CashAccountType | None = Field(None, alias="cashAccountType", description="Cash account type")


class AccountOwner(BaseModel):
    """Account owner model."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., description="Account owner name", max_length=70)
    role: str | None = Field(None, description="Owner role", max_length=35)


class Balance(BaseModel):
    """Balance model."""

    model_config = ConfigDict(extra="forbid")

    balance_amount: Amount = Field(
        ..., alias="balanceAmount", description="Balance amount"
    )
    balance_type: BalanceType = Field(
        ..., alias="balanceType", description="Balance type"
    )
    credit_limit_included: bool | None = Field(
        None, alias="creditLimitIncluded", description="Credit limit included"
    )
    last_change_date_time: datetime | None = Field(
        None, alias="lastChangeDateTime", description="Last change date time"
    )
    reference_date: date | None = Field(
        None, alias="referenceDate", description="Reference date"
    )
    last_committed_transaction: str | None = Field(
        None, alias="lastCommittedTransaction", description="Last committed transaction"
    )


class BalanceList(BaseModel):
    """Balance list model."""

    model_config = ConfigDict(extra="forbid")

    account: Optional['AccountDetails'] = Field(None, alias="account", description="Account details")
    balances: List[Balance] = Field(..., description="List of balances")


class AccountDetails(BaseModel):
    """Account details model."""

    model_config = ConfigDict(extra="forbid")

    resource_id: str | None = Field(None, alias="resourceId", description="Resource ID")
    iban: str | None = Field(None, description="IBAN")
    bban: str | None = Field(None, description="BBAN")
    msisdn: str | None = Field(None, description="MSISDN")
    currency: str | None = Field(None, description="Currency code")
    owner_name: str | None = Field(
        None, alias="ownerName", description="Owner name", max_length=140
    )
    owner_names: list[AccountOwner] | None = Field(
        None, alias="ownerNames", description="List of owner names"
    )
    psu_name: str | None = Field(
        None, alias="psuName", description="PSU name", max_length=140
    )
    name: str | None = Field(None, description="Account name", max_length=70)
    display_name: str | None = Field(
        None, alias="displayName", description="Display name", max_length=70
    )
    product: str | None = Field(None, description="Product name", max_length=35)
    cash_account_type: CashAccountType | None = Field(
        None, validation_alias=AliasChoices("cashAccountType", "cashaccounttype"), description="Cash account type"
    )
    status: AccountStatus | None = Field(None, description="Account status")
    bic: str | None = Field(None, description="BIC")
    linked_accounts: str | None = Field(
        None, alias="linkedAccounts", description="Linked accounts", max_length=70
    )
    usage: AccountUsage | None = Field(None, description="Account usage")
    details: str | None = Field(None, description="Account details", max_length=500)
    balances: List[Balance] | None = Field(None, description="Account balances")
    links: Links | None = Field(None, alias="_links", description="Navigation links")

    @model_validator(mode="before")
    def unwrap_account_envelope(cls, values):
        """
        Allow passing either the raw account object OR the whole response
        that wraps it under 'account'.
        """
        if isinstance(values, dict) and "account" in values and isinstance(values["account"], dict):
            return values["account"]
        return values


class AccountList(BaseModel):
    """Account list model."""

    model_config = ConfigDict(extra="forbid")

    accounts: List[AccountDetails] = Field(..., description="List of accounts")


class Transaction(BaseModel):
    """Transaction model."""

    model_config = ConfigDict(extra="forbid")

    transaction_id: str | None = Field(
        None, alias="transactionId", description="Transaction ID"
    )
    entry_reference: str | None = Field(
        None, alias="entryReference", description="Entry reference"
    )
    end_to_end_id: str | None = Field(
        None, alias="endToEndId", description="End to end ID", max_length=35
    )
    batch_indicator: bool | None = Field(
        None, alias="batchIndicator", description="Batch indicator"
    )
    batch_number_of_transactions: int | None = Field(
        None,
        alias="batchNumberOfTransactions",
        description="Batch number of transactions",
    )
    mandate_id: str | None = Field(
        None, alias="mandateId", description="Mandate ID", max_length=35
    )
    check_id: str | None = Field(
        None, alias="checkId", description="Check ID", max_length=35
    )
    creditor_id: str | None = Field(None, alias="creditorId", description="Creditor ID")
    booking_date: date | None = Field(
        None, alias="bookingDate", description="Booking date"
    )
    value_date: date | None = Field(None, alias="valueDate", description="Value date")
    transaction_amount: Amount = Field(
        ..., alias="transactionAmount", description="Transaction amount"
    )
    currency_exchange: list[ExchangeRate] | None = Field(
        None, alias="currencyExchange", description="Currency exchange"
    )
    creditor_name: str | None = Field(
        None, alias="creditorName", description="Creditor name", max_length=70
    )
    creditor_account: AccountReference | None = Field(
        None, alias="creditorAccount", description="Creditor account"
    )
    creditor_agent: str | None = Field(
        None, alias="creditorAgent", description="Creditor agent"
    )
    ultimate_creditor: str | None = Field(
        None, alias="ultimateCreditor", description="Ultimate creditor", max_length=70
    )
    debtor_name: str | None = Field(
        None, alias="debtorName", description="Debtor name", max_length=70
    )
    debtor_account: AccountReference | None = Field(
        None, alias="debtorAccount", description="Debtor account"
    )
    debtor_agent: str | None = Field(
        None, alias="debtorAgent", description="Debtor agent"
    )
    ultimate_debtor: str | None = Field(
        None, alias="ultimateDebtor", description="Ultimate debtor", max_length=70
    )
    remittance_information_unstructured: str | None = Field(
        None,
        alias="remittanceInformationUnstructured",
        description="Unstructured remittance information",
        max_length=140,
    )
    remittance_information_unstructured_array: list[str] | None = Field(
        None,
        alias="remittanceInformationUnstructuredArray",
        description="Array of unstructured remittance information",
    )
    remittance_information_structured: str | None = Field(
        None,
        alias="remittanceInformationStructured",
        description="Structured remittance information",
        max_length=140,
    )
    remittance_information_structured_array: list[str] | None = Field(
        None,
        alias="remittanceInformationStructuredArray",
        description="Array of structured remittance information",
    )
    additional_information: str | None = Field(
        None,
        alias="additionalInformation",
        description="Additional information",
        max_length=500,
    )
    additional_information_structured: str | None = Field(
        None,
        alias="additionalInformationStructured",
        description="Structured additional information",
        max_length=140,
    )
    purpose_code: str | None = Field(
        None, alias="purposeCode", description="Purpose code"
    )
    bank_transaction_code: BankTransactionCode | None = Field(
        None, alias="bankTransactionCode", description="Bank transaction code"
    )
    proprietary_bank_transaction_code: str | None = Field(
        None,
        alias="proprietaryBankTransactionCode",
        description="Proprietary bank transaction code",
        max_length=35,
    )
    balance_after_transaction: Balance | None = Field(
        None, alias="balanceAfterTransaction", description="Balance after transaction"
    )
    links: Links | None = Field(None, alias="_links", description="Navigation links")


class TransactionList(BaseModel):
    """Transaction list model."""

    model_config = ConfigDict(extra="forbid")

    transactions: List['TransactionDetails'] = Field(..., description="List of transactions")


class TransactionDetails(BaseModel):
    """Transaction details model."""

    model_config = ConfigDict(extra="forbid")

    transaction_details: Transaction = Field(
        ..., alias="transactionDetails", description="Transaction details"
    )


class CardTransaction(BaseModel):
    """Card transaction model."""

    model_config = ConfigDict(extra="forbid")

    card_transaction_id: str | None = Field(
        None,
        alias="cardTransactionId",
        description="Card transaction ID",
        max_length=35,
    )
    terminal_id: str | None = Field(
        None, alias="terminalId", description="Terminal ID", max_length=35
    )
    transaction_date: date | None = Field(
        None, alias="transactionDate", description="Transaction date"
    )
    acceptor_transaction_date_time: datetime | None = Field(
        None,
        alias="acceptorTransactionDateTime",
        description="Acceptor transaction date time",
    )
    booking_date: date | None = Field(
        None, alias="bookingDate", description="Booking date"
    )
    value_date: date | None = Field(None, alias="valueDate", description="Value date")
    transaction_amount: Amount = Field(
        ..., alias="transactionAmount", description="Transaction amount"
    )
    grand_total_amount: Amount | None = Field(
        None, alias="grandTotalAmount", description="Grand total amount"
    )
    currency_exchange: ExchangeRateList | None = Field(
        None, alias="currencyExchange", description="Currency exchange"
    )
    original_amount: Amount | None = Field(
        None, alias="originalAmount", description="Original amount"
    )
    markup_fee: Amount | None = Field(None, alias="markupFee", description="Markup fee")
    markup_fee_percentage: str | None = Field(
        None, alias="markupFeePercentage", description="Markup fee percentage"
    )
    card_acceptor_id: str | None = Field(
        None, alias="cardAcceptorId", description="Card acceptor ID", max_length=35
    )
    card_acceptor_name: str | None = Field(
        None, alias="cardAcceptorName", description="Card acceptor name", max_length=70
    )
    card_acceptor_address: Address | None = Field(
        None, alias="cardAcceptorAddress", description="Card acceptor address"
    )
    card_acceptor_phone: str | None = Field(
        None,
        alias="cardAcceptorPhone",
        description="Card acceptor phone",
        max_length=35,
    )
    merchant_category_code: str | None = Field(
        None,
        alias="merchantCategoryCode",
        description="Merchant category code",
        max_length=4,
    )
    masked_pan: str | None = Field(
        None, alias="maskedPAN", description="Masked PAN", max_length=35
    )
    transaction_details: str | None = Field(
        None,
        alias="transactionDetails",
        description="Transaction details",
        max_length=1000,
    )
    invoiced: bool | None = Field(None, description="Invoiced")
    proprietary_bank_transaction_code: str | None = Field(
        None,
        alias="proprietaryBankTransactionCode",
        description="Proprietary bank transaction code",
        max_length=35,
    )


class AuthenticationObject(BaseModel):
    """Authentication object model."""

    model_config = ConfigDict(extra="forbid")

    authentication_type: AuthenticationType = Field(
        ..., alias="authenticationType", description="Authentication type"
    )
    authentication_version: str | None = Field(
        None, alias="authenticationVersion", description="Authentication version"
    )
    authentication_method_id: str = Field(
        ...,
        alias="authenticationMethodId",
        description="Authentication method ID",
        max_length=35,
    )
    name: str | None = Field(None, description="Authentication method name")
    explanation: str | None = Field(
        None, description="Authentication method explanation"
    )


class ChallengeData(BaseModel):
    """Challenge data model."""

    model_config = ConfigDict(extra="forbid")

    image: str | None = Field(None, description="Challenge image (Base64)")
    data: list[str] | None = Field(None, description="Challenge data")
    image_link: str | None = Field(None, alias="imageLink", description="Image link")
    otp_max_length: int | None = Field(
        None, alias="otpMaxLength", description="OTP max length"
    )
    otp_format: str | None = Field(None, alias="otpFormat", description="OTP format")
    additional_information: str | None = Field(
        None, alias="additionalInformation", description="Additional information"
    )


class ScaMethods(BaseModel):
    """SCA methods model."""

    model_config = ConfigDict(extra="forbid")

    sca_methods: list[AuthenticationObject] = Field(
        ..., alias="scaMethods", description="List of SCA methods"
    )


class ConsentAccess(BaseModel):
    """Consent access model."""

    model_config = ConfigDict(extra="forbid")

    all_psd2: str | None = Field(None, alias="allPsd2", description="All PSD2 access")
    available_accounts: str | None = Field(
        None, alias="availableAccounts", description="Available accounts"
    )
    available_accounts_with_balance: str | None = Field(
        None,
        alias="availableAccountsWithBalance",
        description="Available accounts with balance",
    )
    all_psd2_with_balance: str | None = Field(
        None, alias="allPsd2WithBalance", description="All PSD2 with balance"
    )


class ConsentAccountAccess(BaseModel):
    """Consent account access model."""

    model_config = ConfigDict(extra="forbid")

    accounts: list[AccountReference] | None = Field(
        None, description="List of accounts"
    )
    balances: list[AccountReference] | None = Field(
        None, description="List of balances"
    )
    transactions: list[AccountReference] | None = Field(
        None, description="List of transactions"
    )
    additional_information: dict[str, Any] | None = Field(
        None, alias="additionalInformation", description="Additional information"
    )


class ConsentCardAccountAccess(BaseModel):
    """Consent card account access model."""

    model_config = ConfigDict(extra="forbid")

    card_accounts: list[AccountReference] | None = Field(
        None, alias="cardAccounts", description="List of card accounts"
    )
    card_transactions: list[AccountReference] | None = Field(
        None, alias="cardTransactions", description="List of card transactions"
    )
    additional_information: dict[str, Any] | None = Field(
        None, alias="additionalInformation", description="Additional information"
    )


class Consent(BaseModel):
    """Consent model."""

    model_config = ConfigDict(extra="forbid")

    access: ConsentAccess = Field(..., description="Consent access")
    recurring_indicator: bool = Field(
        ..., alias="recurringIndicator", description="Recurring indicator"
    )
    valid_until: date = Field(..., alias="validUntil", description="Valid until date")
    frequency_per_day: int = Field(
        ..., alias="frequencyPerDay", description="Frequency per day"
    )
    last_action_date: date | None = Field(
        None, alias="lastActionDate", description="Last action date"
    )
    consent_status: ConsentStatus = Field(
        ..., alias="consentStatus", description="Consent status"
    )
    card_number: str | None = Field(None, alias="cardNumber", description="Card number")
    expiration_date: date | None = Field(
        None, alias="expirationDate", description="Expiration date"
    )
    card_information: str | None = Field(
        None, alias="cardInformation", description="Card information"
    )
    registration_information: str | None = Field(
        None, alias="registrationInformation", description="Registration information"
    )
    status_change_date_time: datetime | None = Field(
        None, alias="statusChangeDateTime", description="Status change date time"
    )
    tpp_redirect_preferred: bool | None = Field(
        None, alias="tppRedirectPreferred", description="TPP redirect preferred"
    )
    accounts: ConsentAccountAccess | None = Field(None, description="Account access")
    card_accounts: ConsentCardAccountAccess | None = Field(
        None, alias="cardAccounts", description="Card account access"
    )
    links: Links | None = Field(None, alias="_links", description="Navigation links")


class ConsentStatusResponse(BaseModel):
    """Consent status response model."""

    model_config = ConfigDict(extra="forbid")

    consent_status: ConsentStatus = Field(
        ..., alias="consentStatus", description="Consent status"
    )


class AccountReport(BaseModel):
    """Account report model."""

    model_config = ConfigDict(extra="allow")

    booked: List[Transaction] | None = Field(None, description="Booked transactions")
    pending: List[Transaction] | None = Field(None, description="Pending transactions")
    information: List[Transaction] | None = Field(None, alias="information",
                                                  description="Information transactions")
    links: Optional[Links] = Field(None, alias="_links", description="Navigation links")


class AccountTransactionReport(BaseModel):
    """Account transaction report model."""
    model_config = ConfigDict(extra="forbid")

    account: Optional[AccountDetails] = Field(None, description="Account details")
    transactions: AccountReport = Field(..., description="Transactions")
    links: Optional[Links] = Field(None, alias="_links", description="Navigation links")

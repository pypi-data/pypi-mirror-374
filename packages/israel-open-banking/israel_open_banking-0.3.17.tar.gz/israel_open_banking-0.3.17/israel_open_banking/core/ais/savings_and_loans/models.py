"""
PSD2 AIS Models.

This module contains all the Pydantic models used in the PSD2 Account Information Services
based on the Berlin Group NextGenPSD2 Framework v1.3.14 specification.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, List, Optional
from israel_open_banking.core.ais.general.models import Amount, Balance, Links, AccountReport, CashAccountType, AccountStatus

from pydantic import BaseModel, ConfigDict, Field

from .enums import (
    InterestType,
)


class SavingBalanceList(BaseModel):
    """Saving balance list model."""

    model_config = ConfigDict(extra="forbid")

    savings_account: 'AccountDetailsSavingsLoans' = Field(..., alias="savingsAccount",
                                                          description="Saving account details")
    balances: List[Balance] = Field(..., description="List of saving balances")


class LoanBalanceList(BaseModel):
    """Loan balance list model."""

    model_config = ConfigDict(extra="forbid")

    loan_account: 'AccountDetailsSavingsLoans' = Field(..., alias="loanAccount",
                                                       description="Loan account details")
    balances: List[Balance] = Field(..., description="List of loan balances")


class AccountDetailsSavingsLoans(BaseModel):
    """Account details savings loans model."""

    model_config = ConfigDict(extra="ignore")

    resource_id: str | None = Field(None, alias="resourceId", description="Resource ID")
    iban: str | None = Field(None, description="IBAN")
    bban: str | None = Field(None, description="BBAN")
    msisdn: str | None = Field(None, description="MSISDN")
    other: Optional['OtherType'] = Field(None, description="Other account identifier")
    currency: str | None = Field(None, description="Currency code")
    owner_name: str | None = Field(
        None, alias="ownerName", description="Owner name", max_length=140
    )
    name: str | None = Field(None, description="Account name", max_length=70)
    display_name: str | None = Field(
        None, alias="displayName", description="Display name", max_length=70
    )
    product: str | None = Field(None, description="Product name", max_length=35)
    cash_account_type: CashAccountType | None = Field(
        None, alias="cashAccountType", description="Cash account type"
    )
    status: AccountStatus | None = Field(None, description="Account status")
    bic: str | None = Field(None, description="BIC")
    interest: List['Interest'] | None = Field(None, description="List of interest rates")
    related_dates: Optional['RelatedDates'] = Field(None, description="Related dates", alias="relatedDates")
    collaterals_involved: bool | None = Field(None, alias="collateralsInvolved", description="Collaterals involved")
    guaratee_involved: bool | None = Field(None, alias="guaranteeInvolved", description="Guarantee involved")
    linked_accounts: str | None = Field(None, alias="linkedAccounts", description="Linked accounts", max_length=70)
    usage: str | None = Field(None, description="Account usage", max_length=4)
    details: str | None = Field(None, description="Account details", max_length=500)
    balances: List[Balance] | None = Field(None, description="Account balances")
    links: Links | None = Field(None, alias="_links", description="Navigation links")


class SavingAccountList(BaseModel):
    """Saving account list model."""

    model_config = ConfigDict(extra="forbid")

    savings_account: List[AccountDetailsSavingsLoans] = Field(..., description="List of saving accounts",
                                                              alias="savingsAccounts")


class LoanAccountList(BaseModel):
    """Loan account list model."""

    model_config = ConfigDict(extra="forbid")

    loan_accounts: List[AccountDetailsSavingsLoans] = Field(..., description="List of loan accounts",
                                                            alias="loanAccounts")


class SavingAccountTransactionReport(BaseModel):
    """Saving account transaction report model."""
    model_config = ConfigDict(extra="forbid")

    savings_account: AccountDetailsSavingsLoans = Field(..., description="Account details savings loans",
                                                        alias="savingsAccount")
    transactions: AccountReport = Field(..., description="Transactions")
    balances: List[Balance] | None = Field(None, description="List of balances")
    links: Links | None = Field(None, alias="_links", description="Navigation links")


class LoanAccountTransactionReport(BaseModel):
    """Loan account transaction report model."""
    model_config = ConfigDict(extra="forbid")

    loan_account: AccountDetailsSavingsLoans = Field(..., description="Account details savings loans",
                                                     alias="loanAccount")
    transactions: AccountReport = Field(..., description="Transactions")
    balances: List[Balance] | None = Field(None, description="List of balances")
    links: Links | None = Field(None, alias="_links", description="Navigation links")


class AmountDependentRate(BaseModel):
    """Used in case of FC index"""
    percentage: str = Field(..., description="Percentage of the rate")
    from_amount: Amount | None = Field(None, description="From amount for the rate", alias="fromAmount")
    to_amount: Amount | None = Field(None, description="To amount for the rate", alias="toAmount")


class Index(BaseModel):
    """Interest index model."""

    model_config = ConfigDict(extra="forbid")

    index: str | None = Field(None, description="Interest index", max_length=35)
    root_index_value: str | None = Field(None, alias="rootIndexValue", description="Root index value", max_length=35)
    exchange_rate: AmountDependentRate | None = Field(None, alias="exchangeRate",
                                                      description="Exchange rate for the index")
    additional_information: str | None = Field(None, alias="additionalInformation",
                                               description="Additional information about the index")


class Interest(BaseModel):
    """Interest model."""

    model_config = ConfigDict(extra="forbid")

    type: InterestType | None = Field(None, description="Interest type")
    related_indices: List[Index] | None = Field(None, alias="relatedIndices", description="List of related indices")
    rate: List[AmountDependentRate] = Field(..., description="List of interest rates")
    from_date_time: str | None = Field(None, alias="fromDateTime",
                                       description="From date and time for the interest rate")
    to_date_time: str | None = Field(None, alias="toDateTime", description="To date and time for the interest rate")
    change_mechanism: str | None = Field(None, alias="changeMechanism",
                                        description="Change mechanism for the interest rate")


class RelatedDates(BaseModel):
    """Related dates model."""
    model_config = ConfigDict(extra="forbid")

    contract_start_date: str | None = Field(None, alias="contractStartDate", description="Contract start date")
    contract_end_date: str | None = Field(None, alias="contractEndDate", description="Contract end date")
    contract_availability_date: str | None = Field(None, alias="contractAvailabilityDate",
                                                   description="Contract availability date")


class OtherType(BaseModel):
    # TODO: schame for leumi bank and scheme for meitav (maybe more) need to check what fields are needed
    """Other type model for account identification."""
    model_config = ConfigDict(extra="forbid")

    identification: str = Field(..., description="Other account identification")
    scheme_name_code: str | None = Field(None, alias="schemeNameCode", description="Scheme name code")
    scheme_name_proprietary: str | None = Field(
        None, alias="schemeNameProprietary", description="Scheme name proprietary"
    )
    schema_name_code: str | None = Field(
        None, alias="schemaNameCode", description="Schema name code"
    )
    schema_name_proprietary: str | None = Field(
        None, alias="schemaNameProprietary", description="Schema name proprietary"
    )
    issuer: str | None = Field(None, description="Issuer of the account identification")




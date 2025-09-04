"""
PSD2 AIS Models.

This module contains all the Pydantic models used in the PSD2 Account Information Services
based on the Berlin Group NextGenPSD2 Framework v1.3.14 specification.
"""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from israel_open_banking.core.ais.general.models import Amount, Balance, AccountStatus, HrefType, AccountReference, \
    Links, ExchangeRateList, Address, ExchangeRate


class CardBalanceList(BaseModel):
    """Saving balance list model."""

    model_config = ConfigDict(extra="forbid")

    card: AccountReference = Field(..., description="Saving account details")
    balances: List[Balance] = Field(..., description="List of saving balances")


class CardAccountDetails(BaseModel):
    """Details of a card or card-account."""
    model_config = ConfigDict(extra="forbid")

    resource_id: Optional[str] = Field(None, alias="resourceId")
    masked_pan: str = Field(..., alias="maskedPan", max_length=35)
    currency: str | None = Field(None, description="Currency code")
    owner_name: Optional[str] = Field(None, alias="ownerName", max_length=140)
    name: Optional[str] = Field(None, max_length=70)
    display_name: Optional[str] = Field(None, alias="displayName", max_length=70)
    product: Optional[str] = Field(None, max_length=35)
    status: Optional[AccountStatus] = None
    usage: Optional[str] = Field(
        None,
        description="PRIV (private) or ORGA (professional)",
        pattern="^(PRIV|ORGA)$",
        max_length=4,
    )
    details: Optional[str] = Field(None, max_length=1000)
    credit_limit: Optional[Amount] = Field(None, alias="creditLimit")
    balances: List[Balance] | None = Field(None, description="Cards balances")
    links: Optional[LinksAccountDetails] = Field(None, alias="_links")


class LinksAccountDetails(BaseModel):
    """Links returned inside a card / card-account details payload."""
    model_config = ConfigDict(extra="forbid")

    balances: Optional[HrefType] = Field(None, description="Link to balances")
    transactions: Optional[HrefType] = Field(None, description="Link to transactions")
    card: Optional[HrefType] = Field(None, description="Link to card details")
    card_transactions: Optional[HrefType] = Field(None, description="Link to card transactions",
                                                  alias="cardTransactions")


class CardAccountList(BaseModel):
    """List of cards or card-accounts."""
    model_config = ConfigDict(extra="forbid")
    cards: List[CardAccountDetails] = Field(..., description="List of cards or card-accounts")


class LinksCardAccountReport(BaseModel):
    """Links block inside a card-account report."""
    model_config = ConfigDict(extra="allow")  # allows unknown relation names

    card_account: Optional[HrefType] = Field(None, alias="cardAccount")
    card: Optional[HrefType] = Field(None, description="Link to card details")
    first: Optional[HrefType] = Field(None, description="Link to first page of transactions", )
    next: Optional[HrefType] = Field(None, description="Link to next page of transactions")
    previous: Optional[HrefType] = Field(None, description="Link to previous page of transactions")
    last: Optional[HrefType] = Field(None, description="Link to last page of transactions")


class CardTransaction(BaseModel):
    """Single card-transaction line item."""
    model_config = ConfigDict(extra="allow")

    card_transaction_id: Optional[str] = Field(None, alias="cardTransactionId")
    terminal_id: Optional[str] = Field(None, alias="terminalId")
    transaction_date: Optional[str] = Field(None, alias="transactionDate")
    acceptor_transaction_date_time: Optional[str] = Field(None, alias="acceptorTransactionDateTime")
    booking_date: Optional[str] = Field(None, alias="bookingDate")
    value_date: Optional[str] = Field(None, alias="valueDate")
    transaction_amount: Amount = Field(..., alias="transactionAmount")
    grand_total_amount: Optional[Amount] = Field(None, alias="grandTotalAmount")
    currency_exchange: Optional[list[ExchangeRate]] = Field(None, alias="currencyExchange")
    original_amount: Optional[Amount] = Field(None, alias="originalAmount")
    markup_fee: Optional[Amount] = Field(None, alias="markupFee")
    markup_fee_percentage: Optional[str] = Field(None, alias="markupFeePercentage")
    card_acceptor_id: Optional[str] = Field(None, alias="cardAcceptorId")
    card_acceptor_name: Optional[str] = Field(None, alias="cardAcceptorName")
    card_acceptor_address: Optional[Address] = Field(None, alias="cardAcceptorAddress")
    card_acceptor_phone: Optional[str] = Field(None, alias="cardAcceptorPhone")
    merchant_category_code: Optional[str] = Field(None, alias="merchantCategoryCode", max_length=4, min_length=4)
    masked_pan: Optional[str] = Field(None, alias="maskedPAN", max_length=35)
    transaction_details: Optional[str] = Field(None, alias="transactionDetails")
    invoiced: Optional[bool] = Field(None, description="Whether the transaction is invoiced")
    proprietary_bank_transaction_code: Optional[str] = Field(None, alias="proprietaryBankTransactionCode")


class CardAccountReport(BaseModel):
    """Report object holding booked / pending card transactions plus nav links."""
    model_config = ConfigDict(extra="allow")

    booked: List[CardTransaction] = Field(None, description="List of booked card transactions")
    pending: List[CardTransaction] = Field(None, description="List of pending card transactions")
    links: LinksCardAccountReport = Field(None, alias="_links")


class CardAccountTransactionReport(BaseModel):
    """Card account transaction report."""
    model_config = ConfigDict(extra="allow")

    card: AccountReference = Field(..., description="Card account details")
    balances: Optional[List[Balance]] = Field(None, description="List of card balances")
    card_transactions: CardAccountReport = Field(..., alias="cardTransactions", description="Card transactions report")
    links: Optional[Links] = Field(None, alias="_links")

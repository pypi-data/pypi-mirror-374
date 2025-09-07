from datetime import datetime, date
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict, model_validator, field_validator

from israel_open_banking.core.ais import Amount, BalanceType, HrefType, AccountReference, CashAccountType, AccountStatus
from israel_open_banking.core.ais.savings_and_loans.models import OtherType
from israel_open_banking.core.ais.securities.enums import SecuritiesBalanceTypeCode, SecuritiesOrderSide, \
    TypeOfOrderCode, OrderTimeLimitCode, OrderStatusCode, SecuritiesFeeTypeCode


class SecuritiesAccountReference(AccountReference):
    model_config = ConfigDict(extra="forbid")

    other: Optional[OtherType] = None


class LinksList(BaseModel):
    """Pagination links commonly used in list endpoints."""
    model_config = ConfigDict(extra="forbid")

    first: Optional[HrefType] = Field(None, description="Link to the first page of results")
    next: Optional[HrefType] = Field(None, description="Link to the next page of results")
    previous: Optional[HrefType] = Field(None, description="Link to the previous page of results")
    last: Optional[HrefType] = Field(None, description="Link to the last page of results")
    download: Optional[HrefType] = Field(None,
                                         description="Link to download the resource in a specific format (e.g., CSV, PDF)")


class LinksAll(BaseModel):
    """A superset of possible links (_linksAll)."""
    model_config = ConfigDict(extra="forbid")

    # SCA / auth related
    sca_redirect: Optional[HrefType] = Field(None, alias="scaRedirect")
    sca_oauth: Optional[HrefType] = Field(None, alias="scaOAuth")
    confirmation: Optional[HrefType] = Field(None, alias="confirmation")

    # Generic resource links
    self_: Optional[HrefType] = Field(None, alias="self")
    status: Optional[HrefType] = Field(None, alias="status")
    sca_status: Optional[HrefType] = Field(None, alias="scaStatus")

    # Account-ish
    account: Optional[HrefType] = Field(None, description="Link to the account resource")
    balances: Optional[HrefType] = Field(None, description="Link to the balances of the account")
    positions: Optional[HrefType] = Field(None, alias="positions", description="Link to the positions of the account")
    orders: Optional[HrefType] = Field(None, description="Link to the orders of the account")
    transactions: Optional[HrefType] = Field(None, description="Link to the transactions of the account")

    # Cards (included for completeness across NextGen specs)
    card_account: Optional[HrefType] = Field(None, alias="cardAccount")
    card_transactions: Optional[HrefType] = Field(None, alias="cardTransactions")

    # Details
    transaction_details: Optional[HrefType] = Field(None, alias="transactionDetails")
    order_details: Optional[HrefType] = Field(None, alias="orderDetails")

    # Relationships
    related_orders: Optional[List[HrefType]] = Field(None, alias="relatedOrders")
    related_transactions: Optional[List[HrefType]] = Field(None, alias="relatedTransactions")

    # Pagination / downloads
    first: Optional[HrefType] = Field(None, description="Link to the first page of results")
    next: Optional[HrefType] = Field(None, description="Link to the next page of results")
    previous: Optional[HrefType] = Field(None, description="Link to the previous page of results")
    last: Optional[HrefType] = Field(None, description="Link to the last page of results")
    download: Optional[HrefType] = Field(None,
                                         description="Link to download the resource in a specific format (e.g., CSV, PDF)")


class BalanceSecurities(BaseModel):
    model_config = ConfigDict(extra="forbid")

    balance_amount: Amount = Field(..., alias="balanceAmount", description="Balance amount")
    balance_type: BalanceType = Field(..., alias="balanceType", description="Type of balance")
    last_change_date_time: Optional[datetime] = Field(None, alias="lastChangeDateTime",
                                                      description="Last change date and time")
    reference_date: Optional[date] = Field(None, alias="referenceDate", description="Reference date for the balance")
    reference_date_time: Optional[datetime] = Field(None, alias="referenceDateTime",
                                                    description="Reference date and time for the balance")
    last_committed_transaction: Optional[str] = Field(None, alias="lastCommittedTransaction",
                                                      description="Last committed transaction ID")


class SecuritiesAccountFeeRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: Optional[Amount] = None
    percentage: Optional[str] = Field(None, description="Percentage fee as a string (e.g., '0.5%')",
                                      pattern=r"^-?[0-9]{1,20}(\.[0-9]{0,19})?$")
    from_base_amount: Optional[Amount] = Field(None, alias="fromBaseAmount",
                                               description="Base amount from which the fee applies")
    to_base_amount: Optional[Amount] = Field(None, alias="toBaseAmount",
                                             description="Base amount to which the fee applies")
    minimum_amount: Optional[Amount] = Field(None, alias="minimumAmount", description="Minimum fee amount")
    maximum_amount: Optional[Amount] = Field(None, alias="maximumAmount", description="Maximum fee amount")


class SecuritiesAccountFee(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type_code: Optional[SecuritiesFeeTypeCode] = Field(None, alias="typeCode")
    type_proprietary: Optional[str] = Field(None, alias="typeProprietary")
    fee_rules: List[SecuritiesAccountFeeRule] = Field(..., alias="feeRules")
    applicable_from: Optional[datetime] = Field(None, alias="applicableFrom")
    applicable_to: Optional[datetime] = Field(None, alias="applicableTo")
    additional_information: Optional[str] = Field(None, alias="additionalInformation", max_length=500)


class LinksSecuritiesAccount(BaseModel):
    """Links available from a psd2_securities-account details payload."""
    model_config = ConfigDict(extra="allow")

    positions: Optional[HrefType] = Field(None, description="Link to positions")
    orders: Optional[HrefType] = Field(None, description="Link to orders")
    transactions: Optional[HrefType] = Field(None, description="Link to transactions")
    securities_account: Optional[HrefType] = Field(None, alias="securitiesAccount")


class SecuritiesAccountDetails(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Required basic fields (resource id + display/name fields)
    resource_id: str = Field(..., alias="resourceId")
    iban: Optional[str] = Field(None, description="International Bank Account Number (IBAN)")
    bban: Optional[str] = Field(None, description="Basic Bank Account Number (BBAN)")
    msisdn: Optional[str] = Field(None, alias="msisdn",
                                  description="Mobile Station International Subscriber Directory Number")
    other: Optional[OtherType] = Field(None, description="Other account identification details")
    currency: Optional[str] = Field(None, description="Currency code")
    owner_name: Optional[str] = Field(None, alias="ownerName", max_length=140)
    name: Optional[str] = Field(None, max_length=70, description="Account name")
    display_name: Optional[str] = Field(None, alias="displayName", max_length=70, description="Display name")
    product: Optional[str] = Field(None, max_length=70, description="Product name")
    cash_account_type: CashAccountType = Field(..., alias="cashAccountType")
    status: Optional[AccountStatus] = Field(None, description="Account status")

    # Account reference details
    bic: Optional[str] = Field(None, description="BIC (Bank Identifier Code)",
                               pattern=r"^[A-Z]{6}[A-Z2-9][A-NP-Z0-9](?:[A-Z0-9]{3})?$")
    linked_accounts: Optional[str] = Field(None, alias="linkedAccounts")
    usage: Optional[str] = Field(None, description="Account usage (PRIV for private, ORGA for professional)")
    details: Optional[str] = Field(None, max_length=500, description="Account details")
    balances: Optional[List[BalanceSecurities]] = Field(None, description="List of account balances")
    tariffs: Optional[str] = Field(None, description="List of applicable fees", max_length=1000)
    applicable_fees: Optional[List[SecuritiesAccountFee]] = Field(None, alias="applicableFees")

    links: Optional[LinksSecuritiesAccount] = Field(None, alias="_links")


class SecuritiesAccountList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    securities_accounts: List[SecuritiesAccountDetails] = Field(..., alias="securitiesAccounts")


class EvaluatedAmount(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: Amount
    evaluation_date_time: Optional[datetime] = Field(None, alias="evaluationDateTime")
    evaluation_date: Optional[date] = Field(None, alias="evaluationDate")

    @model_validator(mode="before")
    def hoist_evaluation_date(cls, values):
        """
        If `evaluationDate` or `evaluationDateTime` is inside `amount`,
        move it to the top-level fields.
        """
        if isinstance(values, dict):
            amt = values.get("amount")
            if isinstance(amt, dict):
                # Move evaluationDateTime if present
                if "evaluationDateTime" in amt and "evaluationDateTime" not in values:
                    values["evaluationDateTime"] = amt.pop("evaluationDateTime")
                # Move evaluationDate if present
                if "evaluationDate" in amt and "evaluationDate" not in values:
                    values["evaluationDate"] = amt.pop("evaluationDate")
                # Put updated amount back
                values["amount"] = amt
        return values


class AccruedInterest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    days_accrued: Optional[float] = Field(None, alias="daysAccrued")
    amounts: Optional[List[Amount]] = None


class ReportExchangeRate(BaseModel):
    """Minimal placeholder – extend if your ASPSP populates detailed fields."""
    model_config = ConfigDict(extra="forbid")

    source_currency: Optional[str] = Field(None, alias="sourceCurrency", pattern=r"^[A-Z]{3}$",
                                           description="Currency code")
    exchange_rate: Optional[str] = Field(None, alias="exchangeRate")
    unit_currency: Optional[str] = Field(None, alias="unitCurrency", pattern=r"^[A-Z]{3}$",
                                         description="Currency code of the unit")
    target_currency: Optional[str] = Field(None, alias="targetCurrency", pattern=r"^[A-Z]{3}$",
                                           description="Currency code")
    quotation_date: Optional[date] = Field(None, alias="quotationDate")
    contractIdentification: Optional[str] = Field(None, alias="contractIdentification")


class OtherFinancialInstrumentIdentification(BaseModel):
    model_config = ConfigDict(extra="forbid")

    identification: Optional[str] = Field(None, description="Other identification of the financial instrument",
                                          max_length=35)
    suffix: Optional[str] = Field(None, description="Suffix of the identification", alias="suffix", max_length=16)
    type_code: Optional[str] = Field(None, alias="typeCode")
    type_proprietary: Optional[str] = Field(None, alias="typeProprietary",
                                            description="Proprietary type of the identification", max_length=35)


class EvaluatedPrice(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: Optional[Amount] = None
    percentage: Optional[str] = Field(None, description="Percentage as a string (e.g., '0.5%')",
                                      pattern=r"^-?[0-9]{1,20}(\.[0-9]{0,19})?$")
    price_date_time: Optional[datetime] = Field(None, alias="priceDateTime")
    price_date: Optional[date] = Field(None, alias="priceDate")
    price_type: Optional[str] = Field(None, alias="priceType")
    source_of_price: Optional[str] = Field(None, alias="sourceOfPrice")
    description: Optional[str] = Field(None, max_length=500, description="Description of the price", )
    exchange_rates: Optional[List[ReportExchangeRate]] = Field(None, alias="exchangeRates")


class FinancialInstrument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    isin: Optional[str] = Field(None, alias="isin", description="International Securities Identification Number",
                                pattern=r"^[A-Z0-9]{12}$")
    other: Optional[OtherFinancialInstrumentIdentification] = Field(None, alias="other",
                                                                    description="Other identification")
    name: Optional[str] = Field(None, max_length=70, description="Name of the financial instrument")
    normalised_price: Optional[EvaluatedPrice] = Field(None, alias="normalisedPrice",
                                                       description="Normalised price of the financial instrument")

    @model_validator(mode="before")
    def hoist_exchange_rates_into_normalised_price(cls, v):
        """
        If API sends `exchangeRates` at the top level of the instrument,
        move them into normalisedPrice.exchangeRates to keep schema consistent.
        Always ensure it's a list.
        """
        if isinstance(v, dict):
            top_exch = None
            if "exchangeRates" in v:
                top_exch = v.pop("exchangeRates")

            if top_exch is not None:
                # Ensure it's a list (wrap single objects or None)
                if not isinstance(top_exch, list):
                    top_exch = [top_exch] if top_exch is not None else []

                # Ensure we have a dict for normalisedPrice
                np = v.get("normalisedPrice") or v.get("normalizedPrice") or {}
                if not isinstance(np, dict):
                    np = {}

                # Only set if not already present
                np.setdefault("exchangeRates", top_exch)
                v["normalisedPrice"] = np  # normalize key for the field alias

        return v


class MarketIdentification(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mic: Optional[str] = Field(None, alias="mic", description="Market Identifier Code (MIC)", max_length=4)
    market_identifier_proprietary: Optional[str] = Field(None, alias="marketIdentifierProprietary", max_length=35)


class SecuritiesRelatedFee(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type_code: Optional[SecuritiesFeeTypeCode] = Field(None, alias="typeCode", description="Type of fee")
    type_proprietary: Optional[str] = Field(None, alias="typeProprietary")
    amount: Amount = Field(..., description="Amount of the fee")
    links: Optional[LinksAll] = Field(None, alias="_links")


class SecuritiesRelatedDateOrTime(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str = Field(..., description="Type of date or time (e.g., 'settlement', 'trade')")
    date_only: Optional[date] = Field(None, description="Date related to the transaction or position", alias="date")
    date_and_time: Optional[datetime] = Field(None, description="Date and time related to the transaction or position")


class SecuritiesPosition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    financial_instrument: FinancialInstrument = Field(..., alias="financialInstrument")
    units_number: Optional[float] = Field(None, alias="unitsNumber")
    units_nominal: Optional[Amount] = Field(None, alias="unitsNominal")
    external_identifier: Optional[str] = Field(None, alias="externalIdentifier", max_length=35)
    safekeeping_place: Optional[str] = Field(None, alias="safekeepingPlace",
                                             pattern=r"^[A-Z]{6}[A-Z2-9][A-NP-Z0-9](?:[A-Z0-9]{3})?$")
    safekeeping_country: Optional[str] = Field(None, alias="safekeepingCountry", pattern=r"^[A-Z]{2}$")
    balance_type: Optional[SecuritiesBalanceTypeCode] = Field(None, alias="balanceType", description="Type of balance")
    average_buying_price: Optional[Amount] = Field(None, alias="averageBuyingPrice",
                                                   description="Average buying price of the position")
    average_selling_price: Optional[Amount] = Field(None, alias="averageSellingPrice",
                                                    description="Average selling price of the position")
    total_buying_price: Optional[Amount] = Field(None, alias="totalBuyingPrice",
                                                 description="Total buying price of the position")
    estimated_current_value: Optional[EvaluatedAmount] = Field(None, alias="estimatedCurrentValue")
    accrued_interest: Optional[AccruedInterest] = Field(None, alias="accruedInterest")
    currency_exchange: Optional[List[ReportExchangeRate]] = Field(None, alias="currencyExchange")
    details: Optional[str] = Field(None, description="Details about the position", max_length=500)


class SecuritiesTransaction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    transaction_id: Optional[str] = Field(None, alias="transactionId")
    entry_reference: Optional[str] = Field(None, alias="entryReference",
                                           description="Entry reference for the transaction", max_length=35)
    relevant_dates: List[SecuritiesRelatedDateOrTime] = Field(..., alias="relevantDates")
    financial_instrument: FinancialInstrument = Field(..., alias="financialInstrument")
    order_id: Optional[str] = Field(None, alias="orderId")
    units_number: Optional[float] = Field(None, alias="unitsNumber")
    units_nominal: Optional[Amount] = Field(None, alias="unitsNominal")
    transaction_type_code: Optional[str] = Field(None, alias="transactionTypeCode")
    transaction_type_proprietary: Optional[str] = Field(None, alias="transactionTypeProprietary", max_length=35)
    place_of_trade: Optional[MarketIdentification] = Field(None, alias="placeOfTrade")
    amount_includes_fees: bool = Field(..., alias="amountIncludesFees")
    amount_includes_taxes: bool = Field(..., alias="amountIncludesTaxes")
    transaction_amount: Optional[Amount] = Field(None, alias="transactionAmount")
    related_fees: Optional[List[SecuritiesRelatedFee]] = Field(None, alias="relatedFees")
    currency_exchange: Optional[List[ReportExchangeRate]] = Field(None, alias="currencyExchange")
    reversal_indicator: Optional[bool] = Field(None, alias="reversalIndicator")
    reversed_transaction_id: Optional[str] = Field(None, alias="reversedTransactionId")
    units_number_before_tx: Optional[float] = Field(None, alias="unitsNumberBeforeTx")
    units_nominal_before_tx: Optional[Amount] = Field(None, alias="unitsNominalBeforeTx")
    units_number_after_tx: Optional[float] = Field(None, alias="unitsNumberAfterTx")
    units_nominal_after_after_tx: Optional[Amount] = Field(None, alias="unitsNominalAfterAfterTx")
    accrued_interest: Optional[AccruedInterest] = Field(None, alias="accruedInterest")
    details: Optional[str] = Field(None, description="Details about the transaction", max_length=500)
    links: Optional[LinksAll] = Field(None, alias="_links")


class SecuritiesOrder(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order_id: Optional[str] = Field(None, alias="orderId")
    side: SecuritiesOrderSide = Field(..., alias="side", description="Order side")
    financial_instrument: FinancialInstrument = Field(..., alias="financialInstrument")
    units_number_order: Optional[float] = Field(None, alias="unitsNumberOrder")
    units_nominal_order: Optional[Amount] = Field(None, alias="unitsNominalOrder")
    units_number_display: Optional[float] = Field(None, alias="unitsNumberDisplay")
    units_nominal_display: Optional[Amount] = Field(None, alias="unitsNominalDisplay")
    place_of_trade: Optional[MarketIdentification] = Field(None, alias="placeOfTrade")
    limit_price_amount: Optional[Amount] = Field(None, alias="limitPriceAmount")
    limit_price_percent: Optional[str] = Field(None, alias="limitPricePercent",
                                               pattern=r"^-?[0-9]{1,20}(\.[0-9]{0,19})?$")
    stop_price_amount: Optional[Amount] = Field(None, alias="stopPriceAmount")
    stop_price_percent: Optional[str] = Field(None, alias="stopPricePercent",
                                              pattern=r"^-?[0-9]{1,20}(\.[0-9]{0,19})?$")
    trading_session_indicator: Optional[str] = Field(None, alias="tradingSessionIndicator")
    types_of_order: Optional[List[TypeOfOrderCode]] = Field(None, alias="typesOfOrder")
    time_in_force: Optional[OrderTimeLimitCode] = Field(None, alias="timeInForce")
    expiry_date: Optional[date] = Field(None, alias="expiryDate")
    expiry_date_time: Optional[datetime] = Field(None, alias="expiryDateTime")
    related_cash_account: Optional[AccountReference] = Field(None, alias="relatedCashAccount")
    order_split: Optional[bool] = Field(None, alias="orderSplit")
    order_modifyable: Optional[bool] = Field(None, alias="orderModifyable")
    order_status: OrderStatusCode = Field(..., alias="orderStatus")
    details: Optional[str] = Field(None, description="Details about the order", max_length=500)
    links: Optional[LinksAll] = Field(None, alias="_links")

    @field_validator("side", "time_in_force", "order_status", mode="before")
    def lower_first_letter(cls, v):
        if isinstance(v, str) and v:
            return v[0].lower() + v[1:]
        return v

    @model_validator(mode="before")
    def normalize_type_of_order(cls, values):
        # If `typeOfOrder` exists, normalize and move to `typesOfOrder` as a list
        if isinstance(values, dict) and "typeOfOrder" in values:
            raw = values.pop("typeOfOrder")
            if raw is None:
                values["typesOfOrder"] = []
            elif isinstance(raw, list):
                values["typesOfOrder"] = [
                    (s[0].lower() + s[1:]) if isinstance(s, str) and s else s
                    for s in raw
                ]
            elif isinstance(raw, str) and raw:
                values["typesOfOrder"] = [(raw[0].lower() + raw[1:])]
        return values


class SecuritiesAccountPositionsWrapper(BaseModel):
    model_config = ConfigDict(extra="forbid")

    securities_account: SecuritiesAccountReference = Field(..., alias="securitiesAccount")
    report_date_time: Optional[datetime] = Field(None, alias="reportDateTime")
    balances: Optional[List[BalanceSecurities]] = None
    position_list: List[SecuritiesPosition] = Field(..., alias="positionList")


class SecuritiesTransactionsWrapper(BaseModel):
    model_config = ConfigDict(extra="forbid")

    securities_account: SecuritiesAccountReference = Field(..., alias="securitiesAccount")
    transactions: List[SecuritiesTransaction] = Field(default_factory=list, alias="transactions")
    links: Optional[LinksList] = Field(None, alias="_links")

    @model_validator(mode="before")
    def fix_payload(cls, v):
        if not isinstance(v, dict):
            return v

        # API bug: plural -> singular
        if "securitiesAccounts" in v and "securitiesAccount" not in v:
            v["securitiesAccount"] = v.pop("securitiesAccounts")

        # Hoist nested transactions: securitiesAccount.transactions -> top-level transactions
        sa = v.get("securitiesAccount")
        if isinstance(sa, dict) and "transactions" in sa and "transactions" not in v:
            v["transactions"] = sa.pop("transactions") or []

        return v


class SecuritiesOrdersWrapper(BaseModel):
    model_config = ConfigDict(extra="forbid")

    securities_account: Optional[SecuritiesAccountReference] = Field(None, alias="securitiesAccount")
    orders: List[SecuritiesOrder] = Field(default_factory=list, alias="orders")
    links: Optional[LinksList] = Field(None, alias="_links")

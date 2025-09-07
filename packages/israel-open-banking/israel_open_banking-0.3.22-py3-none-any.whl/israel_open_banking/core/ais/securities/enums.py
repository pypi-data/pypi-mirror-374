from enum import Enum


class SecuritiesBalanceTypeCode(str, Enum):
    """ISO 20022 SecuritiesBalanceTypeV2Code – modeled as a free string for brevity."""
    AVAI = "AVAI"  # Available
    AWAS = "AWAS"  # AvailableWithNoAdditionalStatus
    BTRA = "BTRA"  # BeingTransferred
    BLOK = "BLOK"  # Blocked
    BLOV = "BLOV"  # BlockedAuthenticity
    BLCA = "BLCA"  # BlockedCorporateAction
    BLTA = "BLTA"  # BlockedTrading
    BORR = "BORR"  # Borrowed
    COLI = "COLI"  # CollateralIn
    COLO = "COLO"  # CollateralOut
    MARG = "MARG"  # DerivativesMargin
    DRAW = "DRAW"  # Drawn
    COLA = "COLA"  # EligibleForCollateralPurposes
    TRAN = "TRAN"  # InTransshipment
    ISSU = "ISSU"  # Issued
    DIRT = "DIRT"  # NonTaxExempt
    LOAN = "LOAN"  # OnLoan
    REGO = "REGO"  # OnRegistration
    BODE = "BODE"  # PendingBorrowedDelivery
    BORE = "BORE"  # PendingBorrowedReceipt
    PEDA = "PEDA"  # PendingCorporateActionDelivery
    PECA = "PECA"  # PendingCorporateActionReceipt
    PEND = "PEND"  # Pending
    PDMT = "PDMT"  # PendingDeliveryMatchedBalance
    PDUM = "PDUM"  # PendingDeliveryUnmatchedBalance
    LODE = "LODE"  # PendingOnLoanDelivery
    LORE = "LORE"  # PendingOnLoanReceipt
    PENR = "PENR"  # PendingReceipt
    PRMT = "PRMT"  # PendingReceiptMatchedBalance
    PRUM = "PRUM"  # PendingReceiptUnmatchedBalance
    PLED = "PLED"  # Pledged
    QUAS = "QUAS"  # QuasiIssued
    NOMI = "NOMI"  # Registered
    RSTR = "RSTR"  # Restricted
    SPOS = "SPOS"  # StreetPosition
    CLEN = "CLEN"  # TaxExempt
    OTHR = "OTHR"  # Unclassified
    UNRG = "UNRG"  # Unregistered
    WDOC = "WDOC"  # WaitingDocumentation


class SecuritiesOrderSide(str, Enum):
    buy = "buy"
    sell = "sell"
    subscription = "subscription"
    redemption = "redemption"


class TypeOfOrderCode(str, Enum):
    allOrNone = "allOrNone"
    buyContraShortExempt = "buyContraShortExempt"
    buyContraShort = "buyContraShort"
    buyMinus = "buyMinus"
    carefully = "carefully"
    combinationOrder = "combinationOrder"
    discretionary = "discretionary"
    doNotIncrease = "doNotIncrease"
    doNotReduce = "doNotReduce"
    icebergOrder = "icebergOrder"
    limitWith = "limitWith"
    limitWithout = "limitWithout"
    limitOrder = "limitOrder"
    atMarket = "atMarket"
    marketNotHeld = "marketNotHeld"
    marketToLimitOrder = "marketToLimitOrder"
    marketUntilTouched = "marketUntilTouched"
    notHeld = "notHeld"
    orderLie = "orderLie"
    stopLimit = "stopLimit"
    stopOrder = "stopOrder"
    stopLoss = "stopLoss"
    sellPlus = "sellPlus"
    sellShortExempt = "sellShortExempt"
    sellShort = "sellShort"


class TradingSessionTypeCode(str, Enum):
    auctions = "auctions"
    continuous = "continuous"


class OrderTimeLimitCode(str, Enum):
    day = "day"
    goodTillCancel = "goodTillCancel"
    atTheOpening = "atTheOpening"
    immediateOrCancel = "immediateOrCancel"
    fillOrKill = "fillOrKill"
    fillAndKill = "fillAndKill"
    goodTillCrossing = "goodTillCrossing"
    goodTillDate = "goodTillDate"
    atTheClose = "atTheClose"
    goodThroughCrossing = "goodThroughCrossing"
    atCrossing = "atCrossing"
    goodForTime = "goodForTime"
    goodForAuction = "goodForAuction"
    goodForMonth = "goodForMonth"


class OrderStatusCode(str, Enum):
    unknown = "unknown"
    new = "new"
    partiallyFilled = "partiallyFilled"
    filled = "filled"
    doneForDay = "doneForDay"
    canceled = "canceled"
    replaced = "replaced"
    pendingCancel = "pendingCancel"
    stopped = "stopped"
    rejected = "rejected"
    suspended = "suspended"
    pendingNew = "pendingNew"
    calculated = "calculated"
    expired = "expired"
    acceptedForBidding = "acceptedForBidding"
    pendingReplace = "pendingReplace"


class SecuritiesFeeTypeCode(str, Enum):
    transactionFee = "transactionFee"
    brokerageFee = "brokerageFee"
    managementFee = "managementFee"
    courtage = "courtage"
    custodyFee = "custodyFee"
    exchangeRate = "exchangeRate"
    thirdPartyFee = "thirdPartyFee"
    otherFee = "otherFee"

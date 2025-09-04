from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, RootModel


class AccountResponse(BaseModel):
    currencyCode: str = Field(..., description="ISO 4217", max_length=3, min_length=3)
    id: int


class DividendCashAction(str, Enum):
    REINVEST = "REINVEST"
    TO_ACCOUNT_CASH = "TO_ACCOUNT_CASH"


class AccountBucketDetailedResponse(BaseModel):
    creationDate: datetime
    dividendCashAction: DividendCashAction
    endDate: Optional[datetime] = None
    goal: Optional[float] = None
    icon: Optional[str] = None
    id: int
    initialInvestment: Optional[float] = None
    instrumentShares: Optional[Dict[str, float]] = None
    name: Optional[str] = None
    publicUrl: Optional[str] = None


class InstrumentIssueName(str, Enum):
    DELISTED = "DELISTED"
    SUSPENDED = "SUSPENDED"
    NO_LONGER_TRADABLE = "NO_LONGER_TRADABLE"
    MAX_POSITION_SIZE_REACHED = "MAX_POSITION_SIZE_REACHED"
    APPROACHING_MAX_POSITION_SIZE = "APPROACHING_MAX_POSITION_SIZE"
    COMPLEX_INSTRUMENT_APP_TEST_REQUIRED = "COMPLEX_INSTRUMENT_APP_TEST_REQUIRED"
    PRICE_TOO_LOW = "PRICE_TOO_LOW"


class InstrumentIssueSeverity(str, Enum):
    IRREVERSIBLE = "IRREVERSIBLE"
    REVERSIBLE = "REVERSIBLE"
    INFORMATIVE = "INFORMATIVE"


class InstrumentIssue(BaseModel):
    name: InstrumentIssueName
    severity: InstrumentIssueSeverity


class InvestmentResult(BaseModel):
    priceAvgInvestedValue: Optional[float] = None
    priceAvgResult: Optional[float] = None
    priceAvgResultCoef: Optional[float] = None
    priceAvgValue: Optional[float] = None


class AccountBucketInstrumentResult(BaseModel):
    currentShare: Optional[float] = None
    expectedShare: Optional[float] = None
    issues: Optional[List[InstrumentIssue]] = None
    ownedQuantity: Optional[float] = None
    result: Optional[InvestmentResult] = None
    ticker: Optional[str] = None


class AccountBucketInstrumentsDetailedResponse(BaseModel):
    instruments: Optional[List[AccountBucketInstrumentResult]] = None
    settings: Optional[AccountBucketDetailedResponse] = None


class DividendDetails(BaseModel):
    gained: Optional[float] = None
    inCash: Optional[float] = None
    reinvested: Optional[float] = None


class AccountBucketResultResponseStatus(str, Enum):
    AHEAD = "AHEAD"
    ON_TRACK = "ON_TRACK"
    BEHIND = "BEHIND"


class AccountBucketResultResponse(BaseModel):
    cash: Optional[float] = Field(
        None, description="Amount of money put into the pie in account currency"
    )
    dividendDetails: Optional[DividendDetails] = None
    id: int
    progress: Optional[float] = Field(
        None, description="Progress of the pie based on the set goal", example=0.5
    )
    result: Optional[InvestmentResult] = None
    status: Optional[AccountBucketResultResponseStatus] = Field(
        None, description="Status of the pie based on the set goal"
    )


class CashResponse(BaseModel):
    blocked: Optional[float] = None
    free: Optional[float] = None
    invested: Optional[float] = None
    pieCash: Optional[float] = Field(None, description="Invested cash in pies")
    ppl: Optional[float] = None
    result: Optional[float] = None
    total: Optional[float] = None


class DuplicateBucketRequest(BaseModel):
    icon: Optional[str] = None
    name: Optional[str] = None


class EnqueuedReportResponse(BaseModel):
    reportId: int


class TimeEventType(str, Enum):
    OPEN = "OPEN"
    CLOSE = "CLOSE"
    BREAK_START = "BREAK_START"
    BREAK_END = "BREAK_END"
    PRE_MARKET_OPEN = "PRE_MARKET_OPEN"
    AFTER_HOURS_OPEN = "AFTER_HOURS_OPEN"
    AFTER_HOURS_CLOSE = "AFTER_HOURS_CLOSE"
    OVERNIGHT_OPEN = "OVERNIGHT_OPEN"


class TimeEvent(BaseModel):
    date: datetime
    type: TimeEventType


class WorkingSchedule(BaseModel):
    id: int
    timeEvents: Optional[List[TimeEvent]] = None


class Exchange(BaseModel):
    id: int
    name: Optional[str] = None
    workingSchedules: Optional[List[WorkingSchedule]] = None


class HistoricalOrderExecutor(str, Enum):
    API = "API"
    IOS = "IOS"
    ANDROID = "ANDROID"
    WEB = "WEB"
    SYSTEM = "SYSTEM"
    AUTOINVEST = "AUTOINVEST"


class HistoricalOrderFillType(str, Enum):
    TOTV = "TOTV"
    OTC = "OTC"
    STOCK_SPLIT = "STOCK_SPLIT"
    STOCK_DISTRIBUTION = "STOCK_DISTRIBUTION"
    FOP = "FOP"
    FOP_CORRECTION = "FOP_CORRECTION"
    CUSTOM_STOCK_DISTRIBUTION = "CUSTOM_STOCK_DISTRIBUTION"
    EQUITY_RIGHTS = "EQUITY_RIGHTS"


class HistoricalOrderStatus(str, Enum):
    LOCAL = "LOCAL"
    UNCONFIRMED = "UNCONFIRMED"
    CONFIRMED = "CONFIRMED"
    NEW = "NEW"
    CANCELLING = "CANCELLING"
    CANCELLED = "CANCELLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    REJECTED = "REJECTED"
    REPLACING = "REPLACING"
    REPLACED = "REPLACED"


class HistoricalOrderTimeValidity(str, Enum):
    DAY = "DAY"
    GOOD_TILL_CANCEL = "GOOD_TILL_CANCEL"


class HistoricalOrderType(str, Enum):
    LIMIT = "LIMIT"
    STOP = "STOP"
    MARKET = "MARKET"
    STOP_LIMIT = "STOP_LIMIT"


class TaxName(str, Enum):
    COMMISSION_TURNOVER = "COMMISSION_TURNOVER"
    CURRENCY_CONVERSION_FEE = "CURRENCY_CONVERSION_FEE"
    FINRA_FEE = "FINRA_FEE"
    FRENCH_TRANSACTION_TAX = "FRENCH_TRANSACTION_TAX"
    PTM_LEVY = "PTM_LEVY"
    STAMP_DUTY = "STAMP_DUTY"
    STAMP_DUTY_RESERVE_TAX = "STAMP_DUTY_RESERVE_TAX"
    TRANSACTION_FEE = "TRANSACTION_FEE"


class Tax(BaseModel):
    fillId: Optional[str] = None
    name: Optional[TaxName] = None
    quantity: Optional[float] = None
    timeCharged: Optional[datetime] = None


class HistoricalOrder(BaseModel):
    dateCreated: Optional[datetime] = None
    dateExecuted: Optional[datetime] = None
    dateModified: Optional[datetime] = None
    executor: Optional[HistoricalOrderExecutor] = None
    fillCost: Optional[float] = Field(None, description="In the instrument currency")
    fillId: Optional[int] = None
    fillPrice: Optional[float] = Field(None, description="In the instrument currency")
    fillResult: Optional[float] = None
    fillType: Optional[HistoricalOrderFillType] = None
    filledQuantity: Optional[float] = Field(
        None, description="Applicable to quantity orders"
    )
    filledValue: Optional[float] = Field(None, description="Applicable to value orders")
    id: int
    limitPrice: Optional[float] = Field(None, description="Applicable to limit orders")
    orderedQuantity: Optional[float] = Field(
        None, description="Applicable to quantity orders"
    )
    orderedValue: Optional[float] = Field(
        None, description="Applicable to value orders"
    )
    parentOrder: Optional[int] = None
    status: Optional[HistoricalOrderStatus] = None
    stopPrice: Optional[float] = Field(None, description="Applicable to stop orders")
    taxes: Optional[List[Tax]] = None
    ticker: Optional[str] = None
    timeValidity: Optional[HistoricalOrderTimeValidity] = Field(
        None, description="Applicable to stop, limit and stopLimit orders"
    )
    type: Optional[HistoricalOrderType] = None


class HistoryDividendItem(BaseModel):
    amount: Optional[float] = Field(None, description="In account currency")
    amountInEuro: Optional[float] = None
    grossAmountPerShare: Optional[float] = Field(
        None, description="In instrument currency"
    )
    paidOn: Optional[datetime] = None
    quantity: Optional[float] = None
    reference: Optional[str] = None
    ticker: Optional[str] = None
    type: Optional[str] = None


class HistoryTransactionItemType(str, Enum):
    WITHDRAW = "WITHDRAW"
    DEPOSIT = "DEPOSIT"
    FEE = "FEE"
    TRANSFER = "TRANSFER"


class HistoryTransactionItem(BaseModel):
    amount: Optional[float] = Field(None, description="In the account currency")
    dateTime: Optional[datetime] = None
    reference: Optional[str] = Field(None, description="ID")
    type: Optional[HistoryTransactionItemType] = None


class LimitRequestTimeValidity(str, Enum):
    DAY = "DAY"
    GOOD_TILL_CANCEL = "GOOD_TILL_CANCEL"


class LimitRequest(BaseModel):
    limitPrice: float = Field(..., example=100.23)
    quantity: float = Field(..., example=0.1)
    ticker: str = Field(..., example="AAPL_US_EQ")
    timeValidity: LimitRequestTimeValidity = Field(
        ..., description="Expiration", example="DAY"
    )


class MarketRequest(BaseModel):
    quantity: float = Field(..., example=0.1)
    ticker: str = Field(..., example="AAPL_US_EQ")


class OrderStatus(str, Enum):
    LOCAL = "LOCAL"
    UNCONFIRMED = "UNCONFIRMED"
    CONFIRMED = "CONFIRMED"
    NEW = "NEW"
    CANCELLING = "CANCELLING"
    CANCELLED = "CANCELLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    REJECTED = "REJECTED"
    REPLACING = "REPLACING"
    REPLACED = "REPLACED"


class OrderStrategy(str, Enum):
    QUANTITY = "QUANTITY"
    VALUE = "VALUE"


class OrderType(str, Enum):
    LIMIT = "LIMIT"
    STOP = "STOP"
    MARKET = "MARKET"
    STOP_LIMIT = "STOP_LIMIT"


class Order(BaseModel):
    creationTime: Optional[datetime] = None
    filledQuantity: Optional[float] = Field(
        None, description="Applicable to quantity orders"
    )
    filledValue: Optional[float] = Field(None, description="Applicable to value orders")
    id: int
    limitPrice: Optional[float] = Field(
        None, description="Applicable to LIMIT and STOP_LIMIT orders"
    )
    quantity: Optional[float] = Field(None, description="Applicable to quantity orders")
    status: Optional[OrderStatus] = None
    stopPrice: Optional[float] = Field(
        None, description="Applicable to STOP and STOP_LIMIT orders"
    )
    strategy: Optional[OrderStrategy] = None
    ticker: Optional[str] = Field(
        None,
        description="Unique instrument identifier. Get from the /instruments endpoint",
        example="AAPL_US_EQ",
    )
    type: Optional[OrderType] = None
    value: Optional[float] = Field(None, description="Applicable to value orders")


class PieRequestDividendCashAction(str, Enum):
    REINVEST = "REINVEST"
    TO_ACCOUNT_CASH = "TO_ACCOUNT_CASH"


class PieRequest(BaseModel):
    dividendCashAction: Optional[PieRequestDividendCashAction] = None
    endDate: Optional[datetime] = None
    goal: Optional[float] = Field(
        None, description="Total desired value of the pie in account currency"
    )
    icon: Optional[str] = None
    instrumentShares: Optional[Dict[str, float]] = Field(
        None, example={"AAPL_US_EQ": 0.5, "MSFT_US_EQ": 0.5}
    )
    name: Optional[str] = None


class PlaceOrderErrorCode(str, Enum):
    SellingEquityNotOwned = "SellingEquityNotOwned"
    CantLegalyTradeException = "CantLegalyTradeException"
    InsufficientResources = "InsufficientResources"
    InsufficientValueForStocksSell = "InsufficientValueForStocksSell"
    TargetPriceTooFar = "TargetPriceTooFar"
    TargetPriceTooClose = "TargetPriceTooClose"
    NotEligibleForISA = "NotEligibleForISA"
    ShareLendingAgreementNotAccepted = "ShareLendingAgreementNotAccepted"
    InstrumentNotFound = "InstrumentNotFound"
    MaxEquityBuyQuantityExceeded = "MaxEquityBuyQuantityExceeded"
    MaxEquitySellQuantityExceeded = "MaxEquitySellQuantityExceeded"
    LimitPriceMissing = "LimitPriceMissing"
    StopPriceMissing = "StopPriceMissing"
    TickerMissing = "TickerMissing"
    QuantityMissing = "QuantityMissing"
    MaxQuantityExceeded = "MaxQuantityExceeded"
    InvalidValue = "InvalidValue"
    InsufficientFreeForStocksException = "InsufficientFreeForStocksException"
    MinValueExceeded = "MinValueExceeded"
    MinQuantityExceeded = "MinQuantityExceeded"
    PriceTooFar = "PriceTooFar"
    UNDEFINED = "UNDEFINED"
    NotAvailableForRealMoneyAccounts = "NotAvailableForRealMoneyAccounts"


class PlaceOrderError(BaseModel):
    clarification: Optional[str] = None
    code: Optional[PlaceOrderErrorCode] = None


class PositionFrontend(str, Enum):
    API = "API"
    IOS = "IOS"
    ANDROID = "ANDROID"
    WEB = "WEB"
    SYSTEM = "SYSTEM"
    AUTOINVEST = "AUTOINVEST"


class Position(BaseModel):
    averagePrice: Optional[float] = None
    currentPrice: Optional[float] = None
    frontend: Optional[PositionFrontend] = Field(None, description="Origin")
    fxPpl: Optional[float] = Field(
        None,
        description="Forex movement impact, only applies to positions with instrument currency that differs from the accounts'",
    )
    initialFillDate: Optional[datetime] = None
    maxBuy: Optional[float] = Field(
        None, description="Additional quantity that can be bought"
    )
    maxSell: Optional[float] = Field(None, description="Quantity that can be sold")
    pieQuantity: Optional[float] = Field(None, description="Invested in pies")
    ppl: Optional[float] = None
    quantity: Optional[float] = None
    ticker: Optional[str] = Field(
        None, description="Unique instrument identifier", example="AAPL_US_EQ"
    )


class PositionRequest(BaseModel):
    ticker: Optional[str] = None


class ReportDataIncluded(BaseModel):
    includeDividends: Optional[bool] = None
    includeInterest: Optional[bool] = None
    includeOrders: Optional[bool] = None
    includeTransactions: Optional[bool] = None


class PublicReportRequest(BaseModel):
    dataIncluded: Optional[ReportDataIncluded] = None
    timeFrom: Optional[datetime] = None
    timeTo: Optional[datetime] = None


class ReportResponseStatus(str, Enum):
    Queued = "Queued"
    Processing = "Processing"
    Running = "Running"
    Canceled = "Canceled"
    Failed = "Failed"
    Finished = "Finished"


class ReportResponse(BaseModel):
    dataIncluded: Optional[ReportDataIncluded] = None
    downloadLink: Optional[str] = None
    reportId: int
    status: Optional[ReportResponseStatus] = None
    timeFrom: Optional[datetime] = None
    timeTo: Optional[datetime] = None


class StopLimitRequestTimeValidity(str, Enum):
    DAY = "DAY"
    GOOD_TILL_CANCEL = "GOOD_TILL_CANCEL"


class StopLimitRequest(BaseModel):
    limitPrice: float = Field(..., example=100.23)
    quantity: float = Field(..., example=0.1)
    stopPrice: float = Field(..., example=100.23)
    ticker: str = Field(..., example="AAPL_US_EQ")
    timeValidity: StopLimitRequestTimeValidity = Field(
        ..., description="Expiration", example="DAY"
    )


class StopRequestTimeValidity(str, Enum):
    DAY = "DAY"
    GOOD_TILL_CANCEL = "GOOD_TILL_CANCEL"


class StopRequest(BaseModel):
    quantity: float = Field(..., example=0.1)
    stopPrice: float = Field(..., example=100.23)
    ticker: str = Field(..., example="AAPL_US_EQ")
    timeValidity: StopRequestTimeValidity = Field(
        ..., description="Expiration", example="DAY"
    )


class TradeableInstrumentType(str, Enum):
    CRYPTOCURRENCY = "CRYPTOCURRENCY"
    ETF = "ETF"
    FOREX = "FOREX"
    FUTURES = "FUTURES"
    INDEX = "INDEX"
    STOCK = "STOCK"
    WARRANT = "WARRANT"
    CRYPTO = "CRYPTO"
    CVR = "CVR"
    CORPACT = "CORPACT"


class TradeableInstrument(BaseModel):
    addedOn: Optional[datetime] = Field(None, description="On the platform since")
    currencyCode: str = Field(
        ..., description="ISO 4217", max_length=3, min_length=3, example="USD"
    )
    isin: Optional[str] = None
    maxOpenQuantity: Optional[float] = None
    name: Optional[str] = None
    shortName: Optional[str] = None
    ticker: str = Field(..., description="Unique identifier", example="AAPL_US_EQ")
    type: TradeableInstrumentType = Field(..., example="ETF")
    workingScheduleId: Optional[int] = Field(
        None, description="Get items in the /exchanges endpoint"
    )


class InstrumentListResponse(RootModel[list[TradeableInstrument]]):
    pass


class FetchAllPiesResponse(RootModel[list[AccountBucketResultResponse]]):
    pass


class ExchangeResponse(RootModel[list[Exchange]]):
    pass


class FetchAPieResponse(RootModel[list[AccountBucketInstrumentsDetailedResponse]]):
    pass


class FetchAllEquityOrdersResponse(RootModel[list[Order]]):
    pass


class PositionResponse(RootModel[list[Position]]):
    pass


class PaginatedResponseHistoricalOrderResponse(BaseModel):
    items: Optional[List[HistoricalOrder]] = None
    nextPagePath: Optional[str] = None


class PaginatedResponseHistoryDividendItemResponse(BaseModel):
    items: Optional[List[HistoryDividendItem]] = None
    nextPagePath: Optional[str] = None


class PaginatedResponseHistoryTransactionItemResponse(BaseModel):
    items: Optional[List[HistoryTransactionItem]] = None
    nextPagePath: Optional[str] = None

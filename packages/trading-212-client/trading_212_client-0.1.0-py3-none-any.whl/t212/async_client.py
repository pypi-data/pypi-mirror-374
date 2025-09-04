from typing import TypeVar

from t212.exceptions import not_implemented_api_field
from t212.models import (
    AccountResponse,
    CashResponse,
    ExchangeResponse,
    InstrumentListResponse,
    FetchAllPiesResponse,
    FetchAPieResponse,
    FetchAllEquityOrdersResponse,
    PaginatedResponseHistoricalOrderResponse,
    PaginatedResponseHistoryDividendItemResponse,
    PaginatedResponseHistoryTransactionItemResponse,
    PositionResponse,
    LimitRequestTimeValidity,
    Order,
)

import aiohttp

from t212 import config

T = TypeVar("T")


class AsyncTrading212Client:
    client: aiohttp.ClientSession | None = None
    base_url: str = f"https://{config.T212_ENVIRONMENT}.trading212.com/api/v0/equity"
    headers: dict[str, str] = {
        "Authorization": config.T212_API_KEY,
        "Content-Type": "application/json",
    }

    @classmethod
    def init_client(cls) -> aiohttp.ClientSession:
        if cls.client is None:
            cls.client = aiohttp.ClientSession(
                timeout=aiohttp.client.ClientTimeout(total=10)
            )
        return cls.client

    @classmethod
    async def close_client(cls) -> None:
        if cls.client is not None:
            await cls.client.close()
            cls.client = None

    @classmethod
    async def get(
        cls, url_suffix: str, params: dict[str | str] | None, response_type: type[T]
    ):
        client = cls.init_client()
        url = f"{cls.base_url}/{url_suffix}"

        async with client.get(f"{url}", params=params, headers=cls.headers) as response:
            response.raise_for_status()
            return response_type.model_validate(await response.json())

    @classmethod
    async def post(
        cls, url_suffix: str, data: dict[str | str] | None, response_type: type[T]
    ):
        client = cls.init_client()
        url = f"{cls.base_url}/{url_suffix}"

        async with client.post(f"{url}", json=data, headers=cls.headers) as response:
            response.raise_for_status()
            return response_type.model_validate(await response.json())

    @classmethod
    async def exchange_list(cls) -> ExchangeResponse:
        url = "metadata/exchanges"
        return await cls.get(url, None, ExchangeResponse)

    @classmethod
    async def instrument_list(cls) -> InstrumentListResponse:
        url = "metadata/instruments"
        return await cls.get(url, None, InstrumentListResponse)

    @classmethod
    async def fetch_all_pies(cls) -> FetchAllPiesResponse:
        url = "pies"
        return await cls.get(url, None, FetchAllPiesResponse)

    @classmethod
    async def fetch_a_pie(cls, pie_id: int) -> FetchAPieResponse:
        url = f"pies/{pie_id}"
        return await cls.get(url, None, FetchAPieResponse)

    @classmethod
    async def fetch_all_equity_orders(cls) -> FetchAllEquityOrdersResponse:
        url = "orders"
        return await cls.get(url, None, FetchAllEquityOrdersResponse)

    @classmethod
    async def fetch_by_id(cls, order_id: int):
        url = f"orders/{order_id}"
        return await cls.get(url, None, FetchAllEquityOrdersResponse)

    @classmethod
    async def fetch_account_cash(cls) -> CashResponse:
        url = "account/cash"
        return await cls.get(url, None, CashResponse)

    @classmethod
    async def fetch_account_metadata(cls) -> AccountResponse:
        url = "account/info"
        return await cls.get(url, None, AccountResponse)

    @classmethod
    async def fetch_all_open_positions(cls) -> PositionResponse:
        url = "portfolio"
        return await cls.get(url, None, PositionResponse)

    @classmethod
    async def fetch_open_position_by_id(cls, position_id: int) -> PositionResponse:
        url = f"portfoloi/{position_id}"
        return await cls.get(url, None, PositionResponse)

    @classmethod
    async def historical_order_data(
        cls, cursor: int, ticker: str, limit: int = 20
    ) -> PaginatedResponseHistoricalOrderResponse:
        url = "history/orders"
        params = {"cursor": cursor, "ticker": ticker, "limit": limit}
        return await cls.get(url, params, PaginatedResponseHistoricalOrderResponse)

    @classmethod
    async def paid_out_dividends(
        cls, cursor: int, ticker: str, limit: int = 20
    ) -> PaginatedResponseHistoryDividendItemResponse:
        url = "history/orders"
        params = {"cursor": cursor, "ticker": ticker, "limit": limit}
        return await cls.get(url, params, PaginatedResponseHistoryDividendItemResponse)

    @classmethod
    async def transactions_list(
        cls, cursor: int, ticker: str, limit: int = 20
    ) -> PaginatedResponseHistoryTransactionItemResponse:
        url = "history/orders"
        params = {"cursor": cursor, "ticker": ticker, "limit": limit}
        return await cls.get(
            url, params, PaginatedResponseHistoryTransactionItemResponse
        )

    @classmethod
    async def search_position_by_ticker(
        cls,
        ticker: str,
    ) -> PaginatedResponseHistoryTransactionItemResponse:
        """Returns 500"""
        url = "portfolio/ticker"
        params = {"ticker": ticker}
        return await cls.post(
            url, params, PaginatedResponseHistoryTransactionItemResponse
        )

    @classmethod
    async def place_limit_order(
        cls,
        limit_price: float,
        quantity: float,
        ticker: str,
        time_validity: LimitRequestTimeValidity,
    ) -> Order:
        """Returns 403 forbidden"""
        url = "orders/limit"
        json_data = {
            "limitPrice": limit_price,
            "quantity": quantity,
            "ticker": ticker,
            "timeValidity": time_validity,
        }
        return await cls.post(url, json_data, Order)

    @classmethod
    @not_implemented_api_field
    async def place_market_order(
        cls,
        quantity: float,
        ticker: str,
    ) -> Order:
        """Returns 403 forbidden"""
        url = "orders/market"
        json_data = {
            "quantity": quantity,
            "ticker": ticker,
        }
        return await cls.post(url, json_data, Order)

    @classmethod
    @not_implemented_api_field
    async def place_stop_order(
        cls,
        limit_price: float,
        quantity: float,
        ticker: str,
        time_validity: LimitRequestTimeValidity,
    ) -> Order:
        """Returns 403 forbidden"""
        url = "orders/stop"
        json_data = {
            "limitPrice": limit_price,
            "quantity": quantity,
            "ticker": ticker,
            "timeValidity": time_validity,
        }
        return await cls.post(url, json_data, Order)

    @classmethod
    @not_implemented_api_field
    async def place_stop_limit_order(
        cls,
        limit_price: float,
        quantity: float,
        stop_price: float,
        ticker: str,
        time_validity: LimitRequestTimeValidity,
    ) -> Order:
        """Returns 403 forbidden"""
        url = "orders/stop"
        json_data = {
            "limitPrice": limit_price,
            "quantity": quantity,
            "stop_price": stop_price,
            "ticker": ticker,
            "timeValidity": time_validity,
        }
        return await cls.post(url, json_data, Order)


if __name__ == "__main__":
    import asyncio

    print(
        asyncio.run(
            AsyncTrading212Client.place_limit_order(
                0.1, 0.1, "AAPL_US_EQ", LimitRequestTimeValidity.DAY
            )
        )
    )
    asyncio.run(AsyncTrading212Client.close_client())

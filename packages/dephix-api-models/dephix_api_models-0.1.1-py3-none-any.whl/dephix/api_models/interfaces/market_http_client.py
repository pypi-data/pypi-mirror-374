from abc import ABC, abstractmethod
from logging import Logger
from typing import Any

from ..models import (
    FundingRate,
    InstrumentsInfo,
    KlineCandle,
    ShortKlineData,
    PlaceOrderResult
)


class MarketHttpClient(ABC):
    """
    Abstract class for HTTP clients of trading APIs
    """
    
    def __init__(self, logger: Logger) -> None:
        """
        Initialize HTTP client
        
        Args:
            logger: Logger instance
        """
        self.logger: Logger = logger

    def __enter__(self) -> 'MarketHttpClient':
        """
        Enter context manager.
        Initializes HTTP connection.

        Returns:
            MarketHttpClient: client instance
        """
        self.logger.debug("Initializing HTTP client")
        return self.connect()

    def __exit__(self, exc_type: type | None, exc_val: Exception | None, exc_tb: Any) -> None:
        """
        Exit context manager.
        Handles HTTP connection cleanup.

        Args:
            exc_type: Exception type, if an exception occurred
            exc_val: Exception value, if an exception occurred
            exc_tb: Exception traceback, if an exception occurred
        """
        if exc_type is not None:
            self.logger.error(f"Exception occurred: {exc_type.__name__}: {exc_val}")
        
        self.disconnect()

    @abstractmethod
    def connect(self) -> 'MarketHttpClient':
        """
        Connect to API
        
        Returns:
            MarketHttpClient: client instance
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """
        Disconnect from API
        """
        pass

    @abstractmethod
    def get_server_time(self) -> int:
        """
        Get server time
        
        Returns:
            int: server time in milliseconds
        """
        pass

    @abstractmethod
    def get_kline(
            self,
            symbol: str,
            interval: str = "15",
            category: str = "linear",
            start: int | None = None,
            end: int | None = None,
            limit: int = 200
    ) -> list[KlineCandle]:
        """
        Get kline (candlestick) data
        
        Args:
            symbol: Trading symbol
            interval: Kline interval 1,3,5,15,30,60,120,240,360,720,D,W,M
            category: Kline category (linear/spot/inverse)
            start: Start time in milliseconds
            end: End time in milliseconds
            limit: Number of klines to retrieve

        Returns:
            List[KlineCandle]: List of klines
        """
        pass

    @abstractmethod
    def get_mark_price_kline(
            self,
            symbol: str,
            interval: str = "15",
            category: str = "linear",
            start: int | None = None,
            end: int | None = None,
            limit: int = 200
    ) -> list[ShortKlineData]:
        """
        Get mark price kline data

        Args:
            symbol: Trading symbol
            interval: Kline interval 1,3,5,15,30...
            category: Kline category (linear/inverse)
            start: Start time in milliseconds
            end: End time in milliseconds
            limit: Number of klines to retrieve [1, 1000]

        Returns:
            List[ShortKlineData]: List of mark price klines
        """
        pass

    @abstractmethod
    def get_index_price_kline(
            self,
            symbol: str,
            interval: str = "15",
            category: str = "linear",
            start: int | None = None,
            end: int | None = None,
            limit: int = 200
    ) -> list[ShortKlineData]:
        """
        Get index price kline data

        Args:
            symbol: Trading symbol
            interval: Kline interval 1,3,5,15,30...
            category: Kline category (linear/inverse)
            start: Start time in milliseconds
            end: End time in milliseconds
            limit: Number of klines to retrieve [1, 1000]

        Returns:
            List[ShortKlineData]: List of index price klines
        """
        pass

    @abstractmethod
    def place_order(
            self,
            symbol: str,
            category: str = "linear",
            side: str = "buy",
            orderType: str = "market",
            quantity: float = 0.0,
            price: float = 0.0
    ) -> PlaceOrderResult:
        """
        Place an order
        
        Args:
            symbol: Trading symbol
            category: Category (linear/spot/inverse)
            side: Side (buy/sell)
            orderType: Order type (market/limit)
            quantity: Quantity
            price: Price

        Returns:
            PlaceOrderResult: Order placement result
        """
        pass

    @abstractmethod
    def get_instruments_info(
            self,
            symbol: str,
            category: str = "linear",
    ) -> InstrumentsInfo:
        """
        Get instruments info

        Args:
            symbol: Trading symbol
            category: Category (linear/inverse/spot/option)

        Returns:
            InstrumentsInfo: Instruments information
        """
        pass

    @abstractmethod
    def get_funding_rate_history(
            self,
            symbol: str,
            category: str = "linear",
            start: int | None = None,
            end: int | None = None,
            limit: int = 200
    ) -> list[FundingRate]:
        """
        Get funding rate history

        Args:
            symbol: Trading symbol
            category: Category (linear/inverse)
            start: Start time in milliseconds
            end: End time in milliseconds
            limit: Number of records to retrieve [1, 1000]

        Returns:
            List[FundingRate]: List of funding rate history
        """
        pass

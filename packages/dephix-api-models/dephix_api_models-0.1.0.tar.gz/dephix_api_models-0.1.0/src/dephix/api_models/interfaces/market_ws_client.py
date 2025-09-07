from abc import ABC, abstractmethod
from typing import Any, Callable
from logging import Logger


class MarketWsClient(ABC):
    """
    Abstract class for WebSocket clients of trading APIs
    """
    
    def __init__(self, logger: Logger) -> None:
        """
        Initialize WebSocket client
        
        Args:
            logger: Logger instance
        """
        self.logger: Logger = logger

    def __enter__(self) -> 'MarketWsClient':
        """
        Enter context manager.
        Initializes WebSocket connection.

        Returns:
            MarketWsClient: client instance
        """
        self.logger.debug("Initializing WebSocket client")
        return self.connect()

    def __exit__(self, exc_type: type | None, exc_val: Exception | None, exc_tb: Any) -> None:
        """
        Exit context manager.
        Handles WebSocket connection cleanup.

        Args:
            exc_type: Exception type, if an exception occurred
            exc_val: Exception value, if an exception occurred
            exc_tb: Exception traceback, if an exception occurred
        """
        if exc_type is not None:
            self.logger.error(f"Exception occurred: {exc_type.__name__}: {exc_val}")
        
        self.disconnect()

    @abstractmethod
    def connect(self) -> 'MarketWsClient':
        """
        Connect to WebSocket API
        
        Returns:
            MarketWsClient: client instance
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """
        Disconnect from WebSocket API
        """
        pass

    @abstractmethod
    def subscribe(self, topic: str, callback: Callable[[dict[str, Any]], None]) -> None:
        """
        Subscribe to a topic
        
        Args:
            topic: Topic name to subscribe to
            callback: Callback function to handle data
        """
        pass

    @abstractmethod
    def unsubscribe(self, topic: str) -> None:
        """
        Unsubscribe from a topic
        
        Args:
            topic: Topic name to unsubscribe from
        """
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check connection state
        
        Returns:
            bool: True if connection is active, False otherwise
        """
        pass

    @abstractmethod
    def send_message(self, message: dict[str, Any]) -> None:
        """
        Send a message via WebSocket
        
        Args:
            message: Dictionary with data to send
        """
        pass

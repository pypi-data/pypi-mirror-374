"""
Models and interfaces for trading APIs.

Contains Pydantic models and abstract interfaces for working with trading APIs.
"""

from . import models
from . import interfaces

from .models import (
    FundingRate,
    LotSizeFilter,
    InstrumentsInfo,
    KlineCandle,
    ShortKlineData,
    PlaceOrderResult
)

from .interfaces import (
    MarketHttpClient,
    MarketWsClient
)

__all__ = [
    "FundingRate",
    "LotSizeFilter",
    "InstrumentsInfo", 
    "KlineCandle",
    "ShortKlineData",
    "PlaceOrderResult",
    
    "MarketHttpClient",
    "MarketWsClient",
    
    "models",
    "interfaces",
]

from pydantic import BaseModel


class KlineCandle(BaseModel):
    startTime: str
    openPrice: str
    highPrice: str
    lowPrice: str
    closePrice: str
    volume: str
    turnover: str


class ShortKlineData(BaseModel):
    startTime: str
    openPrice: str
    highPrice: str
    lowPrice: str
    closePrice: str

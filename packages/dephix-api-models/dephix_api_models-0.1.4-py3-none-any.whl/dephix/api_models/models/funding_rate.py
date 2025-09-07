from pydantic import BaseModel


class FundingRate(BaseModel):
    symbol: str
    fundingRate: float
    fundingRateTimestamp: int

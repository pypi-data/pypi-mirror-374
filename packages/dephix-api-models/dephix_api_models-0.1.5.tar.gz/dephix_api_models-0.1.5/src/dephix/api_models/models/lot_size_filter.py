from pydantic import BaseModel


class LotSizeFilter(BaseModel):
    basePrecision: float
    quotePrecision: float
    minOrderQty: float
    maxOrderQty: float
    minOrderAmt: float
    maxOrderAmt: float

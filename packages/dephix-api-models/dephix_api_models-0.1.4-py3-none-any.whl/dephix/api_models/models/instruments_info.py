from pydantic import BaseModel
from .lot_size_filter import LotSizeFilter


class InstrumentsInfo(BaseModel):
    baseCoin: str
    quoteCoin: str
    status: str
    lotSizeFilter: LotSizeFilter

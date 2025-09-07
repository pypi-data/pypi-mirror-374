from pydantic import BaseModel


class PlaceOrderResult(BaseModel):
    orderId: str
    orderLinkId: str

from app.core.enums import CurrencyEnum
from pydantic import BaseModel
from decimal import Decimal


class ResponseUserBalanceModel(BaseModel):
    currency: CurrencyEnum
    amount: Decimal

    model_config = {"from_attributes": True}

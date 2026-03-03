from decimal import Decimal

from pydantic import BaseModel

from app.core.enums import CurrencyEnum


class ResponseUserBalanceModel(BaseModel):
    currency: CurrencyEnum
    amount: Decimal

    model_config = {"from_attributes": True}

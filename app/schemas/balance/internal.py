from decimal import Decimal

from pydantic import BaseModel, model_validator

from app.core.enums import CurrencyEnum
from app.core.exceptions import InvalidUserIdException, NegativeBalanceException


class UserBalanceModel(BaseModel):
    id: int
    user_id: int
    currency: CurrencyEnum
    amount: Decimal

    @model_validator(mode="after")
    def validate_fields(self):
        if self.amount < 0:
            raise NegativeBalanceException("Balance must be >= 0")

        if self.user_id is not None and self.user_id <= 0:
            raise InvalidUserIdException()

        return self

    model_config = {"from_attributes": True}

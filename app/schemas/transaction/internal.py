from datetime import datetime
from app.core.enums import TransactionTypeEnum, TransactionStatusEnum, CurrencyEnum
from pydantic import BaseModel, model_validator
from decimal import Decimal
from app.core.exceptions import NegativeBalanceException, InvalidUserIdException


class TransactionModel(BaseModel):
    id: int
    user_id: int
    currency: CurrencyEnum
    amount: Decimal
    status: TransactionStatusEnum
    type: TransactionTypeEnum
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="after")
    def validate_fields(self):
        if self.amount < 0:
            raise NegativeBalanceException("Balance must be >= 0")

        if self.user_id is not None and self.user_id <= 0:
            raise InvalidUserIdException()

        return self

    model_config = {"from_attributes": True}

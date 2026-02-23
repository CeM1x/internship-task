from decimal import Decimal

from pydantic import BaseModel

from app.core.enums import CurrencyEnum, TransactionTypeEnum


class RequestTransactionModel(BaseModel):
    currency: CurrencyEnum
    amount: Decimal
    type: TransactionTypeEnum

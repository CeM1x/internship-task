from app.core.enums import CurrencyEnum, TransactionTypeEnum
from pydantic import BaseModel
from decimal import Decimal


class RequestTransactionModel(BaseModel):
    currency: CurrencyEnum
    amount: Decimal
    type: TransactionTypeEnum

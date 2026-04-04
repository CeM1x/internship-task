from decimal import Decimal

from pydantic import BaseModel, Field

from app.core.enums import CurrencyEnum, TransactionTypeEnum


class RequestTransactionModel(BaseModel):
    currency: CurrencyEnum
    amount: Decimal
    type: TransactionTypeEnum


class RequestDepositModel(BaseModel):
    user_id: int
    currency: CurrencyEnum
    amount: Decimal


class RequestWithdrawModel(BaseModel):
    user_id: int
    currency: CurrencyEnum
    amount: Decimal

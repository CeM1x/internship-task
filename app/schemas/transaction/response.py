from decimal import Decimal

from pydantic import BaseModel

from app.schemas.transaction.internal import TransactionModel


class TransactionWithBalance(BaseModel):
    transaction: TransactionModel
    balance: Decimal

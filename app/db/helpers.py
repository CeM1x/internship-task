from app.core.enums import TransactionStatusEnum, TransactionTypeEnum
from app.models.transaction import Transaction

NOT_ROLLBACKED = Transaction.status != TransactionStatusEnum.ROLLBACKED
IS_DEPOSIT = Transaction.type == TransactionTypeEnum.DEPOSIT
IS_WITHDRAW = Transaction.type == TransactionTypeEnum.WITHDRAW


def between_dates(column, dt_gt, dt_lt):
    return (column >= dt_gt) & (column < dt_lt)

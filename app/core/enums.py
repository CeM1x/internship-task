from enum import StrEnum


class CurrencyEnum(StrEnum):
    USD = "USD"
    EUR = "EUR"
    AUD = "AUD"
    CAD = "CAD"
    ARS = "ARS"
    PLN = "PLN"
    BTC = "BTC"
    ETH = "ETH"
    DOGE = "DOGE"
    USDT = "USDT"


class UserStatusEnum(StrEnum):
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"
    ROLLBACKED = "ROLLBACKED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class TransactionStatusEnum(StrEnum):
    processed = "PROCESSED"
    roll_backed = "ROLLBACKED"


class TransactionTypeEnum(StrEnum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"
    TRANSFER_IN = "TRANSFER_IN"
    TRANSFER_OUT = "TRANSFER_OUT"
    REFUND = "REFUND"

from decimal import Decimal
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
    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"
    DELETED = "DELETED"


class TransactionStatusEnum(StrEnum):
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"
    ROLLBACKED = "ROLLBACKED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class TransactionTypeEnum(StrEnum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"
    TRANSFER_IN = "TRANSFER_IN"
    TRANSFER_OUT = "TRANSFER_OUT"
    REFUND = "REFUND"


EXCHANGE_RATES_TO_USD = {
    CurrencyEnum.USD: Decimal("1"),
    CurrencyEnum.EUR: Decimal("0.9342"),
    CurrencyEnum.AUD: Decimal("0.5447"),
    CurrencyEnum.CAD: Decimal("0.6162"),
    CurrencyEnum.ARS: Decimal("0.0009"),
    CurrencyEnum.PLN: Decimal("0.2343"),
    CurrencyEnum.BTC: Decimal("100000.0"),
    CurrencyEnum.ETH: Decimal("3557.3476"),
    CurrencyEnum.DOGE: Decimal("0.3627"),
    CurrencyEnum.USDT: Decimal("0.9709"),
}

from decimal import Decimal

from pydantic import BaseModel

from app.core.enums import CurrencyEnum


class CurrencyRates(BaseModel):
    rates: dict[CurrencyEnum, Decimal]

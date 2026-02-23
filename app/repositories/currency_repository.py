from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import EXCHANGE_RATES_TO_USD


class CurrencyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def convert_to_usd(self, currency: str, amount: Decimal):
        """Конвертация суммы в USD"""
        return (amount or 0) * EXCHANGE_RATES_TO_USD[currency]

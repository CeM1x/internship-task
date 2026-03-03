from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.helpers import (
    IS_DEPOSIT,
    IS_WITHDRAW,
    NOT_ROLLBACKED,
    between_dates,
)
from app.models.transaction import Transaction
from app.repositories.currency_repository import CurrencyRepository


class TransactionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.currency = CurrencyRepository(session)

    async def get_transactions_count(self, dt_gt: date, dt_lt: date):
        q = select(func.count(Transaction.id)).where(
            between_dates(Transaction.created_at, dt_gt, dt_lt),
        )
        return await self.session.scalar(q)

    async def get_not_rollbacked_transactions_count(self, dt_gt: date, dt_lt: date):
        q = select(func.count(Transaction.id)).where(
            between_dates(Transaction.created_at, dt_gt, dt_lt), NOT_ROLLBACKED
        )
        return await self.session.scalar(q)

    async def sum_by_currency(self, dt_gt, dt_lt, *filters):
        """Сумма транзакций по валютам с учётом фильтров"""

        async with self.session.begin():
            q = (
                select(Transaction.currency, func.sum(Transaction.amount))
                .where(between_dates(Transaction.created_at, dt_gt, dt_lt), *filters)
                .group_by(Transaction.currency)
                .with_for_update()
            )
            rows = (await self.session.execute(q)).all()

            result = {}
            for currency, amount in rows:
                result[currency] = amount or Decimal("0")

            return result.items()

    async def get_not_rollbacked_deposit_amount_in_USD(self, dt_gt: date, dt_lt: date):
        rows = await self.sum_by_currency(dt_gt, dt_lt, IS_DEPOSIT, NOT_ROLLBACKED)

        return sum(self.currency.convert_to_usd(currency, amount) for currency, amount in rows)

    async def get_not_rollbacked_withdraw_amount(self, dt_gt: date, dt_lt: date):
        rows = await self.sum_by_currency(dt_gt, dt_lt, IS_WITHDRAW, NOT_ROLLBACKED)

        return sum(self.currency.convert_to_usd(currency, amount) for currency, amount in rows)

from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.enums import CurrencyEnum, TransactionStatusEnum, TransactionTypeEnum
from app.db.helpers import (
    IS_DEPOSIT,
    IS_WITHDRAW,
    NOT_ROLLBACKED,
    between_dates,
)
from app.models.balance import UserBalance
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
        q = (
            select(Transaction.currency, func.sum(Transaction.amount))
            .where(between_dates(Transaction.created_at, dt_gt, dt_lt), *filters)
            .group_by(Transaction.currency)
        )
        rows = (await self.session.execute(q)).all()

        result = {}
        for currency, amount in rows:
            result[currency] = amount or Decimal("0")

        return result.items()

    async def get_not_rollbacked_deposit_amount_in_USD(self, dt_gt: date, dt_lt: date):
        rows = await self.sum_by_currency(dt_gt, dt_lt, IS_DEPOSIT, NOT_ROLLBACKED)

        return sum(self.currency.convert_to_usd(currency, amount) for currency, amount in rows)

    async def get_not_rollbacked_withdraw_amount_in_USD(self, dt_gt: date, dt_lt: date):
        rows = await self.sum_by_currency(dt_gt, dt_lt, IS_WITHDRAW, NOT_ROLLBACKED)
        return sum(abs(self.currency.convert_to_usd(currency, amount)) for currency, amount in rows)

    async def get_transactions_list_by_user_id(self, user_id: Optional[int] = None):
        q = (
            select(Transaction)
            .options(selectinload(Transaction.user))
            .order_by(Transaction.created_at.desc())
        )

        if user_id is not None:
            q = q.where(Transaction.user_id == user_id)

        result = await self.session.execute(q)
        return result.scalars().all()

    async def create_transaction(
        self,
        user_id: int,
        currency: CurrencyEnum,
        amount: Decimal,
        status: TransactionStatusEnum,
        tx_type: TransactionTypeEnum,
    ) -> Transaction:
        result = await self.session.execute(
            insert(Transaction)
            .values(
                user_id=user_id,
                currency=currency,
                amount=amount,
                status=status,
                type=tx_type,
                created_at=datetime.now(UTC),
            )
            .returning(Transaction)
        )
        return result.scalar_one()

    async def get_transaction_by_id(self, transaction_id: int) -> Transaction | None:
        result = await self.session.execute(select(Transaction).where(Transaction.id == transaction_id))
        return result.scalar_one_or_none()

    async def mark_transaction_rollbacked(self, transaction_id: int) -> Transaction:
        result = await self.session.execute(
            update(Transaction)
            .where(Transaction.id == transaction_id)
            .values(status=TransactionStatusEnum.ROLLBACKED)
            .returning(Transaction)
        )
        return result.scalar_one()

    async def get_user_balances(self, user_id: int):
        q = select(UserBalance).where(UserBalance.user_id == user_id)
        result = await self.session.execute(q)
        return result.scalars().all()

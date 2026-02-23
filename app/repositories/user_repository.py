from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.helpers import (
    IS_DEPOSIT,
    NOT_ROLLBACKED,
    between_dates,
)
from app.models.transaction import Transaction
from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_registered_users_count(self, dt_gt: date, dt_lt: date):
        q = select(func.count(User.id)).where(between_dates(User.created_at, dt_gt, dt_lt))
        return await self.session.scalar(q)

    async def get_registered_and_deposit_users_count(self, dt_gt: date, dt_lt: date):
        q = (
            select(func.count(func.distinct(User.id)))
            .join(Transaction, Transaction.user_id == User.id)
            .where(
                between_dates(User.created_at, dt_gt, dt_lt),
                between_dates(Transaction.created_at, dt_gt, dt_lt),
                IS_DEPOSIT,
            )
        )
        return await self.session.scalar(q)

    async def get_registered_and_not_rollbacked_deposit_users_count(self, dt_gt: date, dt_lt: date):
        q = (
            select(func.count(func.distinct(User.id)))
            .join(Transaction, Transaction.user_id == User.id)
            .where(
                between_dates(User.created_at, dt_gt, dt_lt),
                between_dates(Transaction.created_at, dt_gt, dt_lt),
                IS_DEPOSIT,
                NOT_ROLLBACKED,
            )
        )
        return await self.session.scalar(q)

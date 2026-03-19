from collections.abc import Sequence
from datetime import date
from typing import Optional

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.enums import UserStatusEnum
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

    async def get_users_by_filter(
        self, user_id: Optional[int] = None, email: Optional[str] = None, status: Optional[str] = None
    ) -> Sequence[User]:
        q = select(User).options(selectinload(User.balances)).order_by(User.created_at.desc())
        if user_id is not None:
            q = q.where(User.id == user_id)
        if email is not None:
            q = q.where(User.email == email)
        if status is not None:
            q = q.where(User.status == UserStatusEnum(status))

        result = await self.session.execute(q)
        return result.scalars().all()

    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email).options(selectinload(User.balances))
        )
        return result.scalar_one_or_none()

    async def create_user(self, email: str) -> User:
        user = User(email=email, status=UserStatusEnum.ACTIVE)
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_user_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(
            select(User).where(User.id == user_id).options(selectinload(User.balances))
        )
        return result.scalar_one_or_none()

    async def update_status(self, user_id: int, fields: dict) -> User:
        await self.session.execute(update(User).where(User.id == user_id).values(**fields))

        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one()

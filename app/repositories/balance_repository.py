from decimal import Decimal
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import CurrencyEnum
from app.models.balance import UserBalance


class BalanceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_balance_for_user(self, user_id: int) -> list[UserBalance]:
        result = await self.session.execute(select(UserBalance).where(UserBalance.user_id == user_id))
        return result.scalars().all()

    async def create_balance(self, user_id: int, currency: CurrencyEnum, amount: Decimal):
        balance = UserBalance(user_id=user_id, currency=currency, amount=amount)
        self.session.add(balance)
        await self.session.flush()
        return balance

    async def get_balance_for_user_with_currency(
        self, user_id: int, currency: CurrencyEnum
    ) -> Optional[UserBalance]:
        result = await self.session.execute(
            select(UserBalance).where(UserBalance.user_id == user_id, UserBalance.currency == currency)
        )
        return result.scalar_one_or_none()

    async def update_balance(self, balance_id: int, new_amount: Decimal) -> None:
        await self.session.execute(
            update(UserBalance).where(UserBalance.id == balance_id).values(amount=new_amount)
        )

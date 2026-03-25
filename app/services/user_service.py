from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import CurrencyEnum, UserStatusEnum
from app.core.exceptions import (
    BadRequestDataException,
    UserAlreadyActiveException,
    UserAlreadyBlockedException,
    UserAlreadyExistsException,
    UserNotExistsException,
)
from app.repositories.balance_repository import BalanceRepository
from app.repositories.user_repository import UserRepository
from app.schemas.balance.response import ResponseUserBalanceModel
from app.schemas.user.request import RequestUserModel, RequestUserUpdateModel
from app.schemas.user.response import ResponseUserModel


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.users = UserRepository(session)
        self.balances = BalanceRepository(session)

    async def get_users_list(
        self, user_id: Optional[int] = None, email: Optional[str] = None, status: Optional[str] = None
    ) -> list[ResponseUserModel]:
        db_users = await self.users.get_users_by_filter(
            user_id=user_id,
            email=email,
            status=status,
        )

        results: list[ResponseUserModel] = []

        for user in db_users:
            balances_data = sorted(
                [
                    ResponseUserBalanceModel(
                        currency=b.currency,
                        amount=b.amount,
                    )
                    for b in user.balances
                ],
                key=lambda x: x.currency.value,
            )

            results.append(
                ResponseUserModel(
                    id=user.id,
                    email=user.email,
                    status=UserStatusEnum(user.status),
                    created_at=user.created_at,
                    balances=balances_data,
                )
            )

        return results

    async def create_user(self, data: RequestUserModel) -> ResponseUserModel:
        email = data.email.strip().replace(" ", "")
        if not email:
            raise BadRequestDataException("Email can't consist entirely of spaces")

        existing = await self.users.get_user_by_email(email)
        if existing:
            raise UserAlreadyExistsException(f"User with email {email} already exists")

        user = await self.users.create_user(email=email)

        await self.session.commit()

        return ResponseUserModel(
            id=user.id,
            email=user.email,
            status=user.status,
            created_at=user.created_at,
            balances=[ResponseUserBalanceModel(currency=c.value, amount=0) for c in CurrencyEnum],
        )

    async def update_user(self, user_id: int, data: RequestUserUpdateModel) -> ResponseUserModel:
        if user_id < 0:
            raise BadRequestDataException("Unprocessable data in request")

        user = await self.users.get_user_by_id(user_id)
        if not user:
            raise UserNotExistsException(f"User with id `{user_id}` does not exist")

        fields_to_update = {}

        if data.email is not None:
            new_email = data.email.strip().replace(" ", "")
            if not new_email:
                raise BadRequestDataException("Email can't consist entirely of spaces")

            existing = await self.users.get_user_by_email(new_email)
            if existing and existing.id != user_id:
                raise UserAlreadyExistsException(f"User with email {new_email} already exists")

            fields_to_update["email"] = new_email

        if data.status is not None:
            if user.status == data.status:
                if data.status == UserStatusEnum.BLOCKED:
                    raise UserAlreadyBlockedException(f"User {user_id} is already blocked")
                if data.status == UserStatusEnum.ACTIVE:
                    raise UserAlreadyActiveException(f"User {user_id} is already active")

            fields_to_update["status"] = data.status

        if not fields_to_update:
            raise BadRequestDataException("No fields to update")

        updated = await self.users.update_status(user_id, fields_to_update)
        await self.session.commit()
        await self.session.refresh(updated)

        return ResponseUserModel(
            id=updated.id,
            email=updated.email,
            status=updated.status,
            created_at=updated.created_at,
            balances=[
                ResponseUserBalanceModel(currency=b.currency, amount=b.amount) for b in updated.balances
            ],
        )

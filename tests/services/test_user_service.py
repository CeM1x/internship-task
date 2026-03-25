import pytest
from pydantic_core._pydantic_core import ValidationError

from app.core.enums import CurrencyEnum, UserStatusEnum
from app.core.exceptions import (
    BadRequestDataException,
    UserAlreadyActiveException,
    UserAlreadyBlockedException,
    UserAlreadyExistsException,
    UserNotExistsException,
)
from app.schemas.user.request import RequestUserModel, RequestUserUpdateModel
from app.services.user_service import UserService


@pytest.mark.asyncio
async def test_create_user_success(session):
    service = UserService(session)

    data = RequestUserModel(email="  test@example.com  ")

    user = await service.create_user(data)

    assert user.email == "test@example.com"
    assert user.status == UserStatusEnum.ACTIVE
    assert len(user.balances) == len(CurrencyEnum)
    assert all(b.amount == 0 for b in user.balances)


@pytest.mark.asyncio
async def test_create_user_empty_email(session):
    with pytest.raises(ValidationError):
        RequestUserModel(email="   ")


@pytest.mark.asyncio
async def test_create_user_duplicate_email(session):
    service = UserService(session)

    await service.create_user(RequestUserModel(email="test@example.com"))

    with pytest.raises(UserAlreadyExistsException):
        await service.create_user(RequestUserModel(email="test@example.com"))


@pytest.mark.asyncio
async def test_get_users_list(session):
    service = UserService(session)

    # создаём двух пользователей
    await service.create_user(RequestUserModel(email="a@example.com"))
    await service.create_user(RequestUserModel(email="b@example.com"))

    users = await service.get_users_list()

    assert len(users) == 2
    assert {u.email for u in users} == {"a@example.com", "b@example.com"}


@pytest.mark.asyncio
async def test_update_user_email_success(session):
    service = UserService(session)

    user = await service.create_user(RequestUserModel(email="old@example.com"))

    updated = await service.update_user(user_id=user.id, data=RequestUserUpdateModel(email="new@example.com"))

    assert updated.email == "new@example.com"


@pytest.mark.asyncio
async def test_update_user_email_duplicate(session):
    service = UserService(session)

    u1 = await service.create_user(RequestUserModel(email="a@example.com"))
    await service.create_user(RequestUserModel(email="b@example.com"))

    with pytest.raises(UserAlreadyExistsException):
        await service.update_user(user_id=u1.id, data=RequestUserUpdateModel(email="b@example.com"))


@pytest.mark.asyncio
async def test_update_user_status_to_blocked(session):
    service = UserService(session)

    user = await service.create_user(RequestUserModel(email="test@example.com"))

    updated = await service.update_user(
        user_id=user.id, data=RequestUserUpdateModel(status=UserStatusEnum.BLOCKED)
    )

    assert updated.status == UserStatusEnum.BLOCKED


@pytest.mark.asyncio
async def test_update_user_status_already_blocked(session):
    service = UserService(session)

    user = await service.create_user(RequestUserModel(email="test@example.com"))

    # блокируем
    await service.update_user(user_id=user.id, data=RequestUserUpdateModel(status=UserStatusEnum.BLOCKED))

    # повторная попытка
    with pytest.raises(UserAlreadyBlockedException):
        await service.update_user(user_id=user.id, data=RequestUserUpdateModel(status=UserStatusEnum.BLOCKED))


@pytest.mark.asyncio
async def test_update_user_status_already_active(session):
    service = UserService(session)

    user = await service.create_user(RequestUserModel(email="test@example.com"))

    with pytest.raises(UserAlreadyActiveException):
        await service.update_user(user_id=user.id, data=RequestUserUpdateModel(status=UserStatusEnum.ACTIVE))


@pytest.mark.asyncio
async def test_update_user_not_exists(session):
    service = UserService(session)

    with pytest.raises(UserNotExistsException):
        await service.update_user(user_id=999, data=RequestUserUpdateModel(email="x@example.com"))


@pytest.mark.asyncio
async def test_update_user_no_fields(session):
    service = UserService(session)

    user = await service.create_user(RequestUserModel(email="test@example.com"))

    with pytest.raises(BadRequestDataException):
        await service.update_user(user_id=user.id, data=RequestUserUpdateModel())

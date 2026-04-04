from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from app.core.enums import (
    CurrencyEnum,
    TransactionStatusEnum,
    TransactionTypeEnum,
    UserStatusEnum,
)
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.user_repository import UserRepository


@pytest.mark.asyncio
async def test_create_user(session):
    repo = UserRepository(session)

    user = await repo.create_user("test@example.com")

    assert user.id > 0
    assert user.email == "test@example.com"
    assert user.status == UserStatusEnum.ACTIVE


@pytest.mark.asyncio
async def test_get_user_by_email(session):
    repo = UserRepository(session)

    await repo.create_user("a@example.com")
    user = await repo.get_user_by_email("a@example.com")

    assert user is not None
    assert user.email == "a@example.com"


@pytest.mark.asyncio
async def test_get_user_by_id(session):
    repo = UserRepository(session)

    created = await repo.create_user("b@example.com")
    user = await repo.get_user_by_id(created.id)

    assert user is not None
    assert user.id == created.id


@pytest.mark.asyncio
async def test_get_users_by_filter_email(session):
    repo = UserRepository(session)

    await repo.create_user("x@example.com")
    await repo.create_user("y@example.com")

    users = await repo.get_users_by_filter(email="x@example.com")

    assert len(users) == 1
    assert users[0].email == "x@example.com"


@pytest.mark.asyncio
async def test_update_status(session):
    repo = UserRepository(session)

    user = await repo.create_user("test@example.com")

    updated = await repo.update_status(user.id, {"status": UserStatusEnum.BLOCKED})
    await session.commit()
    await session.refresh(updated)

    assert updated.status == UserStatusEnum.BLOCKED


@pytest.mark.asyncio
async def test_get_registered_users_count(session):
    repo = UserRepository(session)

    await repo.create_user("a@example.com")
    await repo.create_user("b@example.com")

    dt_lt = datetime.now(UTC)
    dt_gt = dt_lt - timedelta(days=1)

    count = await repo.get_registered_users_count(dt_gt, dt_lt)

    assert count == 2


@pytest.mark.asyncio
async def test_get_registered_and_deposit_users_count(session):
    users = UserRepository(session)
    tx_repo = TransactionRepository(session)

    user = await users.create_user("test@example.com")

    # создаём депозит
    await tx_repo.create_transaction(
        user_id=user.id,
        currency=CurrencyEnum.USD,
        amount=Decimal("100"),
        status=TransactionStatusEnum.PROCESSED,
        tx_type=TransactionTypeEnum.DEPOSIT,
    )

    dt_lt = datetime.now(UTC)
    dt_gt = dt_lt - timedelta(days=1)

    count = await users.get_registered_and_deposit_users_count(dt_gt, dt_lt)

    assert count == 1


@pytest.mark.asyncio
async def test_get_registered_and_not_rollbacked_deposit_users_count(session):
    users = UserRepository(session)
    tx_repo = TransactionRepository(session)

    user = await users.create_user("test@example.com")

    # депозит
    await tx_repo.create_transaction(
        user_id=user.id,
        currency=CurrencyEnum.USD,
        amount=Decimal("100"),
        status=TransactionStatusEnum.PROCESSED,
        tx_type=TransactionTypeEnum.DEPOSIT,
    )

    # rollback НЕ делаем -> транзакция считается not_rollbacked

    dt_lt = datetime.now(UTC)
    dt_gt = dt_lt - timedelta(days=1)

    count = await users.get_registered_and_not_rollbacked_deposit_users_count(dt_gt, dt_lt)

    assert count == 1

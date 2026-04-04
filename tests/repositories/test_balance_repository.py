from decimal import Decimal

import pytest

from app.core.enums import CurrencyEnum
from app.repositories.balance_repository import BalanceRepository
from app.repositories.user_repository import UserRepository


@pytest.mark.asyncio
async def test_create_balance(session):
    users = UserRepository(session)
    balances = BalanceRepository(session)

    user = await users.create_user("test@example.com")

    balance = await balances.create_balance(user.id, CurrencyEnum.USD, Decimal("100"))

    assert balance.id > 0
    assert balance.user_id == user.id
    assert balance.currency == CurrencyEnum.USD
    assert balance.amount == Decimal("100")


@pytest.mark.asyncio
async def test_get_balance_for_user(session):
    users = UserRepository(session)
    balances = BalanceRepository(session)

    user = await users.create_user("test@example.com")

    await balances.create_balance(user.id, CurrencyEnum.USD, Decimal("100"))
    await balances.create_balance(user.id, CurrencyEnum.EUR, Decimal("50"))

    rows = await balances.get_balance_for_user(user.id)

    assert len(rows) == 2
    assert {b.currency for b in rows} == {CurrencyEnum.USD, CurrencyEnum.EUR}


@pytest.mark.asyncio
async def test_get_balance_for_user_with_currency(session):
    users = UserRepository(session)
    balances = BalanceRepository(session)

    user = await users.create_user("test@example.com")

    await balances.create_balance(user.id, CurrencyEnum.EUR, Decimal("77"))

    balance = await balances.get_balance_for_user_with_currency(user.id, CurrencyEnum.EUR)

    assert balance is not None
    assert balance.amount == Decimal("77")


@pytest.mark.asyncio
async def test_update_balance(session):
    users = UserRepository(session)
    balances = BalanceRepository(session)

    user = await users.create_user("test@example.com")

    balance = await balances.create_balance(user.id, CurrencyEnum.USD, Decimal("10"))

    await balances.update_balance(balance.id, Decimal("999"))
    await session.commit()

    updated = await balances.get_balance_for_user_with_currency(user.id, CurrencyEnum.USD)

    assert updated.amount == Decimal("999")

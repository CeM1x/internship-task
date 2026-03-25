from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from app.core.enums import (
    CurrencyEnum,
    TransactionStatusEnum,
    TransactionTypeEnum,
)
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.user_repository import UserRepository


async def create_user(session, email="test@example.com"):
    repo = UserRepository(session)
    return await repo.create_user(email)


@pytest.mark.asyncio
async def test_create_transaction(session):
    users = UserRepository(session)
    tx_repo = TransactionRepository(session)

    user = await users.create_user("test@example.com")

    tx = await tx_repo.create_transaction(
        user_id=user.id,
        currency=CurrencyEnum.USD,
        amount=Decimal("100"),
        status=TransactionStatusEnum.PROCESSED,
        tx_type=TransactionTypeEnum.DEPOSIT,
    )

    assert tx.id > 0
    assert tx.amount == Decimal("100")
    assert tx.type == TransactionTypeEnum.DEPOSIT


@pytest.mark.asyncio
async def test_get_transaction_by_id(session):
    users = UserRepository(session)
    tx_repo = TransactionRepository(session)

    user = await users.create_user("test@example.com")

    created = await tx_repo.create_transaction(
        user_id=user.id,
        currency=CurrencyEnum.USD,
        amount=Decimal("10"),
        status=TransactionStatusEnum.PROCESSED,
        tx_type=TransactionTypeEnum.DEPOSIT,
    )

    tx = await tx_repo.get_transaction_by_id(created.id)

    assert tx is not None
    assert tx.id == created.id


@pytest.mark.asyncio
async def test_mark_transaction_rollbacked(session):
    users = UserRepository(session)
    tx_repo = TransactionRepository(session)

    user = await users.create_user("test@example.com")

    tx = await tx_repo.create_transaction(
        user_id=user.id,
        currency=CurrencyEnum.USD,
        amount=Decimal("10"),
        status=TransactionStatusEnum.PROCESSED,
        tx_type=TransactionTypeEnum.DEPOSIT,
    )

    updated = await tx_repo.mark_transaction_rollbacked(tx.id)
    await session.commit()
    await session.refresh(updated)

    assert updated.status == TransactionStatusEnum.ROLLBACKED


@pytest.mark.asyncio
async def test_get_transactions_count(session):
    users = UserRepository(session)
    tx_repo = TransactionRepository(session)

    user = await users.create_user("test@example.com")

    await tx_repo.create_transaction(
        user.id, CurrencyEnum.USD, Decimal("10"), TransactionStatusEnum.PROCESSED, TransactionTypeEnum.DEPOSIT
    )

    dt_lt = datetime.now(UTC)
    dt_gt = dt_lt - timedelta(days=1)

    count = await tx_repo.get_transactions_count(dt_gt, dt_lt)

    assert count == 1


@pytest.mark.asyncio
async def test_get_not_rollbacked_transactions_count(session):
    users = UserRepository(session)
    tx_repo = TransactionRepository(session)

    user = await users.create_user("test@example.com")

    # создаём обычную транзакцию
    await tx_repo.create_transaction(
        user.id, CurrencyEnum.USD, Decimal("10"), TransactionStatusEnum.PROCESSED, TransactionTypeEnum.DEPOSIT
    )

    # создаём rollbacked транзакцию
    await tx_repo.create_transaction(
        user.id, CurrencyEnum.USD, Decimal("5"), TransactionStatusEnum.ROLLBACKED, TransactionTypeEnum.DEPOSIT
    )

    dt_lt = datetime.now(UTC)
    dt_gt = dt_lt - timedelta(days=1)

    count = await tx_repo.get_not_rollbacked_transactions_count(dt_gt, dt_lt)

    assert count == 1  # только первая транзакция


@pytest.mark.asyncio
async def test_sum_by_currency(session):
    users = UserRepository(session)
    tx_repo = TransactionRepository(session)

    user = await users.create_user("test@example.com")

    await tx_repo.create_transaction(
        user.id,
        CurrencyEnum.USD,
        Decimal("100"),
        TransactionStatusEnum.PROCESSED,
        TransactionTypeEnum.DEPOSIT,
    )

    await tx_repo.create_transaction(
        user.id, CurrencyEnum.EUR, Decimal("50"), TransactionStatusEnum.PROCESSED, TransactionTypeEnum.DEPOSIT
    )

    dt_lt = datetime.now(UTC)
    dt_gt = dt_lt - timedelta(days=1)

    rows = dict(await tx_repo.sum_by_currency(dt_gt, dt_lt))

    assert rows[CurrencyEnum.USD] == Decimal("100")
    assert rows[CurrencyEnum.EUR] == Decimal("50")


@pytest.mark.asyncio
async def test_get_not_rollbacked_deposit_amount_in_USD(session):
    users = UserRepository(session)
    tx_repo = TransactionRepository(session)

    user = await users.create_user("test@example.com")

    # создаём транзакции
    await tx_repo.create_transaction(
        user.id,
        CurrencyEnum.USD,
        Decimal("100"),
        TransactionStatusEnum.PROCESSED,
        TransactionTypeEnum.DEPOSIT,
    )

    await tx_repo.create_transaction(
        user.id, CurrencyEnum.EUR, Decimal("50"), TransactionStatusEnum.PROCESSED, TransactionTypeEnum.DEPOSIT
    )

    # теперь берём диапазон
    dt_lt = datetime.now(UTC)
    dt_gt = dt_lt - timedelta(days=1)

    total = await tx_repo.get_not_rollbacked_deposit_amount_in_USD(dt_gt, dt_lt)

    from app.core.enums import EXCHANGE_RATES_TO_USD

    expected = Decimal("100") * EXCHANGE_RATES_TO_USD["USD"] + Decimal("50") * EXCHANGE_RATES_TO_USD["EUR"]

    assert total == expected


@pytest.mark.asyncio
async def test_get_not_rollbacked_withdraw_amount(session):
    users = UserRepository(session)
    tx_repo = TransactionRepository(session)

    user = await users.create_user("test@example.com")

    # WITHDRAW транзакции отрицательные
    await tx_repo.create_transaction(
        user.id,
        CurrencyEnum.USD,
        Decimal("-30"),
        TransactionStatusEnum.PROCESSED,
        TransactionTypeEnum.WITHDRAW,
    )

    await tx_repo.create_transaction(
        user.id,
        CurrencyEnum.EUR,
        Decimal("-20"),
        TransactionStatusEnum.PROCESSED,
        TransactionTypeEnum.WITHDRAW,
    )

    dt_lt = datetime.now(UTC)
    dt_gt = dt_lt - timedelta(days=1)

    total = await tx_repo.get_not_rollbacked_withdraw_amount_in_USD(dt_gt, dt_lt)

    from app.core.enums import EXCHANGE_RATES_TO_USD

    expected = abs(Decimal("-30") * EXCHANGE_RATES_TO_USD["USD"]) + abs(
        Decimal("-20") * EXCHANGE_RATES_TO_USD["EUR"]
    )

    assert total == expected


@pytest.mark.asyncio
async def test_get_transactions_list_by_user_id(session):
    users = UserRepository(session)
    tx_repo = TransactionRepository(session)

    user1 = await users.create_user("a@example.com")
    user2 = await users.create_user("b@example.com")

    # транзакции для user1
    await tx_repo.create_transaction(
        user1.id,
        CurrencyEnum.USD,
        Decimal("10"),
        TransactionStatusEnum.PROCESSED,
        TransactionTypeEnum.DEPOSIT,
    )

    # транзакции для user2
    await tx_repo.create_transaction(
        user2.id,
        CurrencyEnum.USD,
        Decimal("20"),
        TransactionStatusEnum.PROCESSED,
        TransactionTypeEnum.DEPOSIT,
    )

    txs = await tx_repo.get_transactions_list_by_user_id(user1.id)

    assert len(txs) == 1
    assert txs[0].user_id == user1.id


@pytest.mark.asyncio
async def test_get_user_balances(session):
    users = UserRepository(session)
    tx_repo = TransactionRepository(session)

    user = await users.create_user("test@example.com")

    # вручную создаём баланс
    from app.repositories.balance_repository import BalanceRepository

    balances = BalanceRepository(session)

    await balances.create_balance(user.id, CurrencyEnum.USD, Decimal("100"))
    await balances.create_balance(user.id, CurrencyEnum.EUR, Decimal("50"))

    rows = await tx_repo.get_user_balances(user.id)

    assert len(rows) == 2
    assert {b.currency for b in rows} == {CurrencyEnum.USD, CurrencyEnum.EUR}

from decimal import Decimal

import pytest

from app.core.enums import CurrencyEnum, TransactionStatusEnum, TransactionTypeEnum, UserStatusEnum
from app.core.exceptions import (
    BadRequestDataException,
    CreateTransactionForBlockedUserException,
    NegativeBalanceException,
    TransactionAlreadyRollbackedException,
    TransactionDoesNotBelongToUserException,
    TransactionNotExistsException,
    UserNotExistsException,
)
from app.models.user import User
from app.schemas.transaction.request import RequestDepositModel, RequestTransactionModel, RequestWithdrawModel
from app.schemas.user.request import RequestUserModel
from app.services.transaction_service import TransactionService


async def create_user_with_balance(
    session, email="test@example.com", currency=CurrencyEnum.USD, amount=Decimal("0")
):
    from app.repositories.balance_repository import BalanceRepository
    from app.services.user_service import UserService

    user_service = UserService(session)
    balance_repo = BalanceRepository(session)

    user = await user_service.create_user(RequestUserModel(email=email))
    balance = await balance_repo.get_balance_for_user_with_currency(user.id, currency)

    if not balance:
        balance = await balance_repo.create_balance(user.id, currency, amount)
    else:
        await balance_repo.update_balance(balance.id, amount)

    await session.commit()
    return user, balance


@pytest.mark.asyncio
async def test_create_transaction_success(session):
    service = TransactionService(session)

    user, balance = await create_user_with_balance(session, amount=Decimal("100"))

    tx = await service.create_transaction(
        user_id=user.id,
        transaction=RequestTransactionModel(
            currency=CurrencyEnum.USD,
            amount=Decimal("50"),
            type=TransactionTypeEnum.DEPOSIT,
        ),
    )

    assert tx.amount == Decimal("50")
    assert tx.type == TransactionTypeEnum.DEPOSIT


@pytest.mark.asyncio
async def test_create_transaction_zero_amount(session):
    service = TransactionService(session)

    user, _ = await create_user_with_balance(session)

    with pytest.raises(BadRequestDataException):
        await service.create_transaction(
            user_id=user.id,
            transaction=RequestTransactionModel(
                currency=CurrencyEnum.USD,
                amount=Decimal("0"),
                type=TransactionTypeEnum.DEPOSIT,
            ),
        )


@pytest.mark.asyncio
async def test_create_transaction_user_not_exists(session):
    service = TransactionService(session)

    with pytest.raises(UserNotExistsException):
        await service.create_transaction(
            user_id=999,
            transaction=RequestTransactionModel(
                currency=CurrencyEnum.USD,
                amount=Decimal("10"),
                type=TransactionTypeEnum.DEPOSIT,
            ),
        )


@pytest.mark.asyncio
async def test_create_transaction_blocked_user(session):
    service = TransactionService(session)

    user, balance = await create_user_with_balance(session)

    db_user = await session.get(User, user.id)
    db_user.status = UserStatusEnum.BLOCKED
    await session.commit()

    with pytest.raises(CreateTransactionForBlockedUserException):
        await service.create_transaction(
            user_id=user.id,
            transaction=RequestTransactionModel(
                currency=CurrencyEnum.USD,
                amount=Decimal("10"),
                type=TransactionTypeEnum.DEPOSIT,
            ),
        )


@pytest.mark.asyncio
async def test_create_transaction_negative_balance(session):
    service = TransactionService(session)

    user, balance = await create_user_with_balance(session, amount=Decimal("5"))

    with pytest.raises(NegativeBalanceException):
        await service.create_transaction(
            user_id=user.id,
            transaction=RequestTransactionModel(
                currency=CurrencyEnum.USD,
                amount=Decimal("-10"),
                type=TransactionTypeEnum.WITHDRAW,
            ),
        )


@pytest.mark.asyncio
async def test_rollback_deposit_success(session):
    service = TransactionService(session)

    user, balance = await create_user_with_balance(session, amount=Decimal("100"))

    tx = await service.create_transaction(
        user_id=user.id,
        transaction=RequestTransactionModel(
            currency=CurrencyEnum.USD,
            amount=Decimal("50"),
            type=TransactionTypeEnum.DEPOSIT,
        ),
    )

    rolled = await service.rollback_transaction(user.id, tx.id)

    assert rolled.status == TransactionStatusEnum.ROLLBACKED


@pytest.mark.asyncio
async def test_rollback_transaction_not_exists(session):
    service = TransactionService(session)

    user, _ = await create_user_with_balance(session)

    with pytest.raises(TransactionNotExistsException):
        await service.rollback_transaction(user.id, 999)


@pytest.mark.asyncio
async def test_rollback_transaction_wrong_user(session):
    service = TransactionService(session)

    user1, _ = await create_user_with_balance(session, email="a@example.com")
    user2, _ = await create_user_with_balance(session, email="b@example.com")

    tx = await service.create_transaction(
        user_id=user1.id,
        transaction=RequestTransactionModel(
            currency=CurrencyEnum.USD,
            amount=Decimal("10"),
            type=TransactionTypeEnum.DEPOSIT,
        ),
    )

    with pytest.raises(TransactionDoesNotBelongToUserException):
        await service.rollback_transaction(user2.id, tx.id)


@pytest.mark.asyncio
async def test_rollback_transaction_already_rollbacked(session):
    service = TransactionService(session)

    user, _ = await create_user_with_balance(session)

    tx = await service.create_transaction(
        user_id=user.id,
        transaction=RequestTransactionModel(
            currency=CurrencyEnum.USD,
            amount=Decimal("10"),
            type=TransactionTypeEnum.DEPOSIT,
        ),
    )

    await service.rollback_transaction(user.id, tx.id)

    with pytest.raises(TransactionAlreadyRollbackedException):
        await service.rollback_transaction(user.id, tx.id)


@pytest.mark.asyncio
async def test_deposit_creates_balance_if_missing(session):
    service = TransactionService(session)

    user, _ = await create_user_with_balance(session, amount=Decimal("0"))

    result = await service.deposit(
        user.id,
        RequestDepositModel(user_id=user.id, currency=CurrencyEnum.USD, amount=Decimal("50")),
    )

    assert result["amount"] == 50.0


@pytest.mark.asyncio
async def test_withdraw_success(session):
    service = TransactionService(session)

    user, _ = await create_user_with_balance(session, amount=Decimal("100"))

    result = await service.withdraw(
        user.id,
        RequestWithdrawModel(user_id=user.id, currency=CurrencyEnum.USD, amount=Decimal("30")),
    )

    assert result["amount"] == 70.0

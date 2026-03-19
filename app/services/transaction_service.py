from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import CurrencyEnum, TransactionStatusEnum, TransactionTypeEnum, UserStatusEnum
from app.core.exceptions import (
    BadRequestDataException,
    CreateTransactionForBlockedUserException,
    NegativeBalanceException,
    TransactionAlreadyRollbackedException,
    TransactionDoesNotBelongToUserException,
    TransactionNotExistsException,
    UpdateTransactionForBlockedUserException,
    UserNotExistsException,
)
from app.repositories.balance_repository import BalanceRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.user_repository import UserRepository
from app.schemas.transaction.internal import TransactionModel
from app.schemas.transaction.request import RequestTransactionModel


class TransactionService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.users = UserRepository(session)
        self.transactions = TransactionRepository(session)
        self.balances = BalanceRepository(session)

    async def get_transaction_list(self, user_id: Optional[int] = None) -> list[TransactionModel]:
        db_transactions = await self.transactions.get_transactions_list_by_user_id(user_id=user_id)

        results: list[TransactionModel] = []

        for transaction in db_transactions:
            results.append(
                TransactionModel(
                    id=transaction.id,
                    user_id=transaction.user_id,
                    currency=transaction.currency,
                    amount=transaction.amount,
                    status=TransactionStatusEnum(transaction.status),
                    type=TransactionTypeEnum(transaction.type),
                    created_at=transaction.created_at,
                )
            )
        return results

    async def create_transaction(
        self, user_id: int, transaction: RequestTransactionModel
    ) -> TransactionModel:
        if user_id < 0:
            raise BadRequestDataException("Unprocessable data in request")

        if transaction.amount == 0:
            raise BadRequestDataException("Transaction can not have zero amount")

        user = await self.users.get_user_by_id(user_id)
        if not user:
            raise UserNotExistsException(f"User with id=`{user_id}` does not exist")

        if user.status != UserStatusEnum.ACTIVE:
            raise CreateTransactionForBlockedUserException(f"User with id=`{user_id}` is blocked")

        balance = await self.balances.get_balance_for_user_with_currency(user_id, transaction.currency)
        if not balance:
            raise BadRequestDataException("Balance for this currency does not exist")

        new_amount = balance.amount + transaction.amount
        if new_amount < 0:
            raise NegativeBalanceException("Negative balance")

        async with self.session.begin():
            await self.balances.update_balance(balance.id, new_amount)
            created_tx = await self.transactions.create_transaction(
                user_id=user_id,
                currency=transaction.currency,
                amount=transaction.amount,
                status=TransactionStatusEnum.PROCESSED,
                type=transaction.type,
            )
        return TransactionModel.model_validate(created_tx)

    async def rollback_transaction(self, user_id: int, transaction_id: int) -> TransactionModel:
        if user_id < 0 or transaction_id < 0:
            raise BadRequestDataException("Unprocessable data in request")

        user = await self.users.get_user_by_id(user_id)
        if not user:
            raise UserNotExistsException(f"User with id=`{user_id}` does not exist")

        transaction = await self.transactions.get_transaction_by_id(transaction_id)

        if not transaction:
            raise TransactionNotExistsException(f"Transaction with id=`{transaction_id}` does not exist")

        if transaction.user_id != user.id:
            raise TransactionDoesNotBelongToUserException(transaction_id, user_id)

        if transaction.status == TransactionStatusEnum.ROLLBACKED:
            raise TransactionAlreadyRollbackedException(transaction_id)

        if user.status == UserStatusEnum.BLOCKED:
            raise UpdateTransactionForBlockedUserException(user_id)

        balance = await self.balances.get_balance_for_user_with_currency(user_id, transaction.currency)
        if not balance:
            raise BadRequestDataException("Balance for this currency does not exist")

        if transaction.amount < 0:
            new_amount = balance.amount + abs(transaction.amount)
        else:
            new_amount = balance.amount - transaction.amount

        if new_amount < 0:
            raise NegativeBalanceException(f"Negative balance: {new_amount}")

        async with self.session.begin():
            await self.balances.update_balance(balance.id, new_amount)
            updated_tx = await self.transactions.mark_transaction_rollbacked(transaction_id)

        return TransactionModel.model_validate(updated_tx)

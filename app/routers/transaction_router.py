from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from app.schemas.transaction.internal import TransactionModel
from app.schemas.transaction.request import RequestTransactionModel
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("", response_model=list[TransactionModel], status_code=status.HTTP_200_OK)
async def get_transactions(user_id: int | None = None, session: AsyncSession = Depends(get_async_session)):
    service = TransactionService(session)
    return await service.get_transaction_list(user_id)


@router.post("/{user_id}/transaction", response_model=TransactionModel, status_code=status.HTTP_200_OK)
async def post_transaction(
    user_id: int, transaction: RequestTransactionModel, session: AsyncSession = Depends(get_async_session)
):
    service = TransactionService(session)
    return await service.create_transaction(user_id, transaction)


@router.patch(
    "/{user_id}/transactions/{transaction_id}",
    response_model=TransactionModel,
    status_code=status.HTTP_200_OK,
)
async def rollback_transaction(
    user_id: int, transaction_id: int, session: AsyncSession = Depends(get_async_session)
):
    service = TransactionService(session)
    return await service.rollback_transaction(user_id, transaction_id)

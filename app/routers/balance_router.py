from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from app.schemas.transaction.request import RequestDepositModel, RequestWithdrawModel
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/balances", tags=["Balances"])


@router.post("/deposit")
async def deposit(data: RequestDepositModel, session: AsyncSession = Depends(get_async_session)):
    service = TransactionService(session)
    return await service.deposit(data.user_id, data)


@router.post("/withdraw")
async def withdraw(data: RequestWithdrawModel, session: AsyncSession = Depends(get_async_session)):
    service = TransactionService(session)
    return await service.withdraw(data.user_id, data)


@router.get("/{user_id}")
async def get_balances(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    service = TransactionService(session)
    return await service.get_user_balances(user_id)

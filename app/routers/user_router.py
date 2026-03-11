from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from app.schemas.user.request import RequestUserModel, RequestUserUpdateModel
from app.schemas.user.response import ResponseUserModel
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[ResponseUserModel], status_code=status.HTTP_200_OK)
async def get_users(
    user_id: int | None = None,
    email: str | None = None,
    user_status: str | None = None,
    session: AsyncSession = Depends(get_async_session),
) -> list[ResponseUserModel]:
    service = UserService(session)
    return await service.get_users_list(user_id=user_id, email=email, status=user_status)


@router.post("", response_model=ResponseUserModel, status_code=status.HTTP_201_CREATED)
async def post_user(
    user: RequestUserModel,
    session: AsyncSession = Depends(get_async_session),
):
    service = UserService(session)
    return await service.create_user(user)


@router.patch("/{user_id}", response_model=ResponseUserModel, status_code=status.HTTP_200_OK)
async def patch_user(
    user_id: int,
    data: RequestUserUpdateModel,
    session: AsyncSession = Depends(get_async_session),
):
    service = UserService(session)
    return await service.update_user(user_id, data)

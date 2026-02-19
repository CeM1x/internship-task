from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.core.enums import UserStatusEnum
from app.schemas.balance.response import ResponseUserBalanceModel


class ResponseUserModel(BaseModel):
    id: int
    email: EmailStr
    status: UserStatusEnum
    created_at: datetime
    balances: list[ResponseUserBalanceModel]

    model_config = {"from_attributes": True}

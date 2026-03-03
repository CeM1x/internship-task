from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.core.enums import UserStatusEnum


class UserModel(BaseModel):
    id: int
    email: EmailStr
    status: UserStatusEnum
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

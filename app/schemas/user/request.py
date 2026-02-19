from pydantic import BaseModel, EmailStr
from app.core.enums import UserStatusEnum


class RequestUserModel(BaseModel):
    email: EmailStr


class RequestUserUpdateModel(BaseModel):
    status: UserStatusEnum

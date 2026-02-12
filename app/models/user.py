from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.db_base import Base, TimestampMixin
from app.core.enums import UserStatusEnum
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy_utils import EmailType
from typing import List


class User(TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(EmailType, unique=True, index=True)
    status: Mapped[UserStatusEnum] = mapped_column(
        PgEnum(UserStatusEnum, name="user_status_enum"),
        default=UserStatusEnum.ACTIVE,
        index=True,
    )

    balances: Mapped[List["UserBalance"]] = relationship(back_populates="user", lazy="selectin")
    transactions: Mapped[List["Transaction"]] = relationship(back_populates="user", lazy="selectin")

from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import EmailType

from app.core.db_base import Base, TimestampMixin
from app.core.enums import UserStatusEnum
from app.models.balance import UserBalance
from app.models.transaction import Transaction


class User(TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(EmailType, unique=True, index=True)
    status: Mapped[UserStatusEnum] = mapped_column(
        PgEnum(UserStatusEnum, name="user_status_enum"),
        default=UserStatusEnum.ACTIVE,
        index=True,
    )

    balances: Mapped[list["UserBalance"]] = relationship(back_populates="user", lazy="selectin")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="user", lazy="selectin")

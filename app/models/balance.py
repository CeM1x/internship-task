from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.core.db_base import Base, TimestampMixin
from app.core.enums import CurrencyEnum
from app.core.exceptions import InvalidUserIdException, NegativeBalanceException


class UserBalance(TimestampMixin, Base):
    __tablename__ = "user_balances"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    currency: Mapped[CurrencyEnum] = mapped_column(
        PgEnum(CurrencyEnum, name="user_balance_currency_enum"), index=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 6), default=0)

    @validates("amount")
    def validate_amount(self, key, value):
        if value < 0:
            raise NegativeBalanceException("Balance must be >= 0")
        return value

    @validates("currency")
    def validate_currency(self, key, value):
        if value not in CurrencyEnum:
            raise ValueError("Invalid currency")
        return value

    @validates("user_id")
    def validate_user_id(self, key, value):
        if value <= 0:
            raise InvalidUserIdException()
        return value

    user: Mapped["User"] = relationship(back_populates="balances", lazy="selectin")

    __table_args__ = (UniqueConstraint("user_id", "currency", name="user_balance_user_currency_unique"),)

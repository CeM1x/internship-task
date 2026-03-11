from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db_base import Base, TimestampMixin
from app.core.enums import CurrencyEnum, TransactionStatusEnum, TransactionTypeEnum


class Transaction(TimestampMixin, Base):
    __tablename__ = "transactions"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    type: Mapped[TransactionTypeEnum] = mapped_column(
        PgEnum(TransactionTypeEnum, name="transaction_type_enum"), index=True
    )
    currency: Mapped[CurrencyEnum] = mapped_column(
        PgEnum(CurrencyEnum, name="transaction_currency_enum"), index=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    status: Mapped[TransactionStatusEnum] = mapped_column(
        PgEnum(TransactionStatusEnum, name="transaction_status_enum"), index=True
    )

    user: Mapped["User"] = relationship(back_populates="transactions", lazy="selectin")

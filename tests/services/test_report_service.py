from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from app.core.enums import CurrencyEnum, TransactionStatusEnum, TransactionTypeEnum
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.user_repository import UserRepository
from app.services.report_service import ReportService


@pytest.mark.asyncio
async def test_report_service_build_week_report(session):
    # Arrange
    report_service = ReportService(session)
    user_repo = UserRepository(session)
    tx_repo = TransactionRepository(session)

    # создаём пользователя
    user = await user_repo.create_user("test@example.com")

    # создаём депозит
    await tx_repo.create_transaction(
        user_id=user.id,
        currency=CurrencyEnum.USD,
        amount=Decimal("100"),
        status=TransactionStatusEnum.PROCESSED,
        tx_type=TransactionTypeEnum.DEPOSIT,
    )

    # создаем вывод
    await tx_repo.create_transaction(
        user_id=user.id,
        currency=CurrencyEnum.USD,
        amount=Decimal("40"),
        status=TransactionStatusEnum.PROCESSED,
        tx_type=TransactionTypeEnum.WITHDRAW,
    )

    # задаём диапазон недели
    week_end = datetime.now(UTC)
    week_start = week_end - timedelta(days=7)

    # Act
    report = await report_service.build_week_report(week_start, week_end)

    # Assert
    assert report.registered_users == 1
    assert report.deposit_users_including_rollbacked == 1
    assert report.deposit_users_without_rollback == 1
    assert report.deposit_amount_usd == Decimal("100")
    assert report.withdraw_amount_usd == Decimal("40")
    assert report.transactions_total == 2
    assert report.transactions_without_rollback == 2

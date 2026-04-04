from decimal import Decimal

import pytest

from app.core.enums import CurrencyEnum, TransactionStatusEnum, TransactionTypeEnum
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.user_repository import UserRepository
from app.services.report_analysis_service import ReportAnalysisService


@pytest.mark.asyncio
async def test_report_analysis_service_build_52_weeks_analysis(session):
    # Arrange
    analysis_service = ReportAnalysisService(session)
    user_repo = UserRepository(session)
    tx_repo = TransactionRepository(session)

    # создаём пользователя и транзакцию в текущей неделе
    user = await user_repo.create_user("test@example.com")

    await tx_repo.create_transaction(
        user_id=user.id,
        currency=CurrencyEnum.USD,
        amount=Decimal("50"),
        status=TransactionStatusEnum.PROCESSED,
        tx_type=TransactionTypeEnum.DEPOSIT,
    )

    # Act
    results = await analysis_service.build_52_weeks_analysis()

    # Assert
    # 1. Должна быть хотя бы одна непустая неделя
    assert len(results) >= 1

    # 2. Первая неделя — текущая (самая свежая)
    first = results[0]
    assert first.deposit_amount_usd == Decimal("50")

    # 3. Все остальные недели должны быть пустыми и отфильтрованы
    # То есть в списке только одна неделя
    assert all(
        r.deposit_amount_usd != 0 or r.withdraw_amount_usd != 0 or r.transactions_total != 0 for r in results
    )

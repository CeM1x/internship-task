from decimal import Decimal

import pytest

from app.core.enums import EXCHANGE_RATES_TO_USD
from app.repositories.currency_repository import CurrencyRepository


@pytest.mark.asyncio
async def test_convert_to_usd_basic(session):
    repo = CurrencyRepository(session)

    amount = Decimal("100")
    usd = repo.convert_to_usd("USD", amount)

    assert usd == amount  # курс USD → USD = 1


@pytest.mark.asyncio
async def test_convert_to_usd_with_rate(session):
    repo = CurrencyRepository(session)

    amount = Decimal("50")
    rate = EXCHANGE_RATES_TO_USD["EUR"]

    usd = repo.convert_to_usd("EUR", amount)

    assert usd == amount * rate


@pytest.mark.asyncio
async def test_convert_to_usd_zero_amount(session):
    repo = CurrencyRepository(session)

    usd = repo.convert_to_usd("USD", Decimal("0"))

    assert usd == 0


@pytest.mark.asyncio
async def test_convert_to_usd_none_amount(session):
    repo = CurrencyRepository(session)

    usd = repo.convert_to_usd("USD", None)

    assert usd == 0  # (amount or 0)

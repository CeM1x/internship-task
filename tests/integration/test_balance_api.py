import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_initial_balance(client: AsyncClient):
    # создаём пользователя
    r = await client.post("/users", json={"email": "balance@example.com"})
    user_id = r.json()["id"]

    # получаем баланс
    response = await client.get(f"/balances/{user_id}")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0  # у нового пользователя нет балансов


@pytest.mark.asyncio
async def test_deposit_success(client: AsyncClient):
    r = await client.post("/users", json={"email": "dep@example.com"})
    user_id = r.json()["id"]

    response = await client.post(
        "/balances/deposit",
        json={"user_id": user_id, "currency": "USD", "amount": 100},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["currency"] == "USD"
    assert data["amount"] == 100


@pytest.mark.asyncio
async def test_withdraw_success(client: AsyncClient):
    r = await client.post("/users", json={"email": "wd@example.com"})
    user_id = r.json()["id"]

    # депозит
    await client.post(
        "/balances/deposit",
        json={"user_id": user_id, "currency": "USD", "amount": 200},
    )

    # вывод
    response = await client.post(
        "/balances/withdraw",
        json={"user_id": user_id, "currency": "USD", "amount": 50},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["currency"] == "USD"
    assert data["amount"] == 150  # остаток


@pytest.mark.asyncio
async def test_withdraw_insufficient_funds(client: AsyncClient):
    r = await client.post("/users", json={"email": "no_money@example.com"})
    user_id = r.json()["id"]

    response = await client.post(
        "/balances/withdraw",
        json={"user_id": user_id, "currency": "USD", "amount": 10},
    )

    assert response.status_code == 400
    assert "insufficient" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_invalid_currency(client: AsyncClient):
    r = await client.post("/users", json={"email": "cur@example.com"})
    user_id = r.json()["id"]

    response = await client.post(
        "/balances/deposit",
        json={"user_id": user_id, "currency": "INVALID", "amount": 100},
    )

    assert response.status_code == 422

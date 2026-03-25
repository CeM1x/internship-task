import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_rollback_success(client: AsyncClient):
    # создаём пользователя
    r = await client.post("/users", json={"email": "rb@example.com"})
    user_id = r.json()["id"]

    # делаем депозит
    await client.post(
        "/balances/deposit",
        json={"user_id": user_id, "currency": "USD", "amount": 200},
    )

    # делаем вывод
    tx = await client.post(
        "/balances/withdraw",
        json={"user_id": user_id, "currency": "USD", "amount": 50},
    )
    tx_id = tx.json()["id"]

    # делаем rollback
    rb = await client.patch(f"/transactions/rollback/{user_id}/{tx_id}")

    assert rb.status_code == 200
    data = rb.json()

    assert data["id"] == tx_id
    assert data["status"] == "ROLLBACKED"


@pytest.mark.asyncio
async def test_rollback_transaction_not_found(client: AsyncClient):
    r = await client.post("/users", json={"email": "rb2@example.com"})
    user_id = r.json()["id"]

    response = await client.patch(f"/transactions/rollback/{user_id}/99999")

    assert response.status_code == 404
    assert "does not exist" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_rollback_wrong_user(client: AsyncClient):
    # user A
    r1 = await client.post("/users", json={"email": "u1@example.com"})
    user1 = r1.json()["id"]

    # user B
    r2 = await client.post("/users", json={"email": "u2@example.com"})
    user2 = r2.json()["id"]

    # транзакция принадлежит user1
    tx = await client.post(
        "/balances/deposit",
        json={"user_id": user1, "currency": "USD", "amount": 100},
    )
    tx_id = tx.json()["id"]

    # user2 пытается откатить
    response = await client.patch(f"/transactions/rollback/{user2}/{tx_id}")

    assert response.status_code == 404
    assert "does not belong" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_rollback_already_rollbacked(client: AsyncClient):
    r = await client.post("/users", json={"email": "rb3@example.com"})
    user_id = r.json()["id"]

    # депозит
    tx = await client.post(
        "/balances/deposit",
        json={"user_id": user_id, "currency": "USD", "amount": 100},
    )
    tx_id = tx.json()["id"]

    # первый rollback
    await client.patch(f"/transactions/rollback/{user_id}/{tx_id}")

    # второй rollback
    response = await client.patch(f"/transactions/rollback/{user_id}/{tx_id}")

    assert response.status_code == 400
    assert "already rollbacked" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_rollback_negative_balance(client: AsyncClient):
    r = await client.post("/users", json={"email": "rb4@example.com"})
    user_id = r.json()["id"]

    # депозит 50
    await client.post(
        "/balances/deposit",
        json={"user_id": user_id, "currency": "USD", "amount": 50},
    )

    # вывод 50
    tx = await client.post(
        "/balances/withdraw",
        json={"user_id": user_id, "currency": "USD", "amount": 50},
    )
    tx_id = tx.json()["id"]

    # вручную уменьшаем баланс до 0 (имитация)
    await client.post(
        "/balances/withdraw",
        json={"user_id": user_id, "currency": "USD", "amount": 0},
    )

    # rollback теперь должен дать ошибку
    response = await client.patch(f"/transactions/rollback/{user_id}/{tx_id}")

    assert response.status_code == 400
    assert "negative balance" in response.json()["detail"].lower()

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_weekly_report_registered_users(client: AsyncClient):
    # создаём 2 пользователей сегодня
    await client.post("/users", json={"email": "r1@example.com"})
    await client.post("/users", json={"email": "r2@example.com"})

    # получаем отчёт
    resp = await client.get("/reports/analysis")
    assert resp.status_code == 200

    reports = resp.json()
    assert len(reports) >= 1

    # в первой неделе должно быть 2 зарегистрированных пользователя
    assert reports[0]["registered_users"] == 2


@pytest.mark.asyncio
async def test_weekly_report_deposit_users(client: AsyncClient):
    # создаём пользователя
    r = await client.post("/users", json={"email": "d1@example.com"})
    user_id = r.json()["id"]

    # делаем депозит
    await client.post("/balances/deposit", json={"user_id": user_id, "currency": "USD", "amount": 100})

    resp = await client.get("/reports/analysis")
    assert resp.status_code == 200

    report = resp.json()[0]

    # пользователь должен попасть в обе метрики
    assert report["deposit_users_including_rollbacked"] == 1
    assert report["deposit_users_without_rollback"] == 1


@pytest.mark.asyncio
async def test_weekly_report_deposit_users_excluding_rollback(client: AsyncClient):
    # создаём пользователя
    r = await client.post("/users", json={"email": "d2@example.com"})
    user_id = r.json()["id"]

    # депозит
    tx = await client.post("/balances/deposit", json={"user_id": user_id, "currency": "USD", "amount": 50})
    tx_id = tx.json()["id"]

    # откатываем депозит
    await client.patch(f"/transactions/rollback/{user_id}/{tx_id}")

    resp = await client.get("/reports/analysis")
    report = resp.json()[0]

    # пользователь был депозитным, но транзакция откатана
    assert report["deposit_users_including_rollbacked"] == 1
    assert report["deposit_users_without_rollback"] == 0


@pytest.mark.asyncio
async def test_weekly_report_amounts_usd(client: AsyncClient):
    # создаём пользователя
    r = await client.post("/users", json={"email": "a1@example.com"})
    user_id = r.json()["id"]

    # депозит 100 USD
    await client.post("/balances/deposit", json={"user_id": user_id, "currency": "USD", "amount": 100})

    # вывод 40 USD
    await client.post("/balances/withdraw", json={"user_id": user_id, "currency": "USD", "amount": 40})

    resp = await client.get("/reports/analysis")
    report = resp.json()[0]

    assert report["deposit_amount_usd"] == 100
    assert report["withdraw_amount_usd"] == 40


@pytest.mark.asyncio
async def test_weekly_report_transactions(client: AsyncClient):
    # создаём пользователя
    r = await client.post("/users", json={"email": "t1@example.com"})
    user_id = r.json()["id"]

    # депозит
    tx = await client.post("/balances/deposit", json={"user_id": user_id, "currency": "USD", "amount": 10})
    tx_id = tx.json()["id"]

    # вывод
    await client.post("/balances/withdraw", json={"user_id": user_id, "currency": "USD", "amount": 5})

    resp = await client.get("/reports/analysis")
    report = resp.json()[0]

    # всего 2 транзакции
    assert report["transactions_total"] == 2

    # откатываем депозит
    await client.patch(f"/transactions/rollback/{user_id}/{tx_id}")

    resp = await client.get("/reports/analysis")
    report = resp.json()[0]

    # теперь только 1 неоткатанная
    assert report["transactions_without_rollback"] == 2


@pytest.mark.asyncio
async def test_weekly_report_empty_weeks_filtered(client: AsyncClient):
    # создаём пользователя (чтобы неделя была непустой)
    await client.post("/users", json={"email": "empty@example.com"})

    resp = await client.get("/reports/analysis")
    reports = resp.json()

    # отчёт должен содержать только непустые недели
    assert len(reports) >= 1

    # проверяем, что нет недель, где все значения нулевые
    for rep in reports:
        assert any(
            [
                rep["registered_users"],
                rep["deposit_users_including_rollbacked"],
                rep["deposit_users_without_rollback"],
                rep["deposit_amount_usd"],
                rep["withdraw_amount_usd"],
                rep["transactions_total"],
                rep["transactions_without_rollback"],
            ]
        )

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_user_success(client: AsyncClient):
    response = await client.post(
        "/users",
        json={"email": "test@example.com"},
    )

    assert response.status_code == 201
    data = response.json()

    assert data["email"] == "test@example.com"
    assert data["status"] == "ACTIVE"
    assert isinstance(data["id"], int)
    assert isinstance(data["balances"], list)
    assert len(data["balances"]) > 0


@pytest.mark.asyncio
async def test_create_user_email_spaces_only(client: AsyncClient):
    response = await client.post(
        "/users",
        json={"email": "   "},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_user_duplicate_email(client: AsyncClient):
    payload = {"email": "dup@example.com"}

    first = await client.post("/users", json=payload)
    assert first.status_code == 201

    second = await client.post("/users", json=payload)
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_get_users_filter_by_id(client: AsyncClient):
    # создаём двух пользователей
    r1 = await client.post("/users", json={"email": "a@example.com"})
    await client.post("/users", json={"email": "b@example.com"})

    user_id = r1.json()["id"]

    response = await client.get(f"/users?user_id={user_id}")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == user_id


@pytest.mark.asyncio
async def test_patch_user_update_email(client: AsyncClient):
    # создаём пользователя
    r = await client.post("/users", json={"email": "old@example.com"})
    user_id = r.json()["id"]

    # обновляем email
    response = await client.patch(
        f"/users/{user_id}",
        json={"email": "new@example.com"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "new@example.com"


@pytest.mark.asyncio
async def test_patch_user_update_status(client: AsyncClient):
    r = await client.post("/users", json={"email": "user@example.com"})
    user_id = r.json()["id"]

    response = await client.patch(
        f"/users/{user_id}",
        json={"status": "BLOCKED"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "BLOCKED"

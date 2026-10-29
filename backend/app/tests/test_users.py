"""Tests for user profile and alerts endpoints."""
import pytest
from httpx import AsyncClient


async def _register_and_login(client: AsyncClient, email: str, password: str = "securepassword1"):
    await client.post("/api/v1/auth/register", json={
        "name": "Test User",
        "email": email,
        "password": password,
    })
    login = await client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return login.json()["access_token"]


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient):
    token = await _register_and_login(client, "user1@example.com")
    resp = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "user1@example.com"
    assert data["is_active"] is True
    assert data["role"] == "user"


@pytest.mark.asyncio
async def test_get_me_unauthenticated(client: AsyncClient):
    resp = await client.get("/api/v1/users/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_list_alerts_empty(client: AsyncClient):
    token = await _register_and_login(client, "user2@example.com")
    resp = await client.get("/api/v1/users/me/alerts", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_list_notifications_empty(client: AsyncClient):
    token = await _register_and_login(client, "user3@example.com")
    resp = await client.get("/api/v1/users/me/notifications", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_categories_empty(client: AsyncClient):
    resp = await client.get("/api/v1/categories")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_deals_empty(client: AsyncClient):
    resp = await client.get("/api/v1/deals")
    assert resp.status_code == 200
    assert resp.json() == []

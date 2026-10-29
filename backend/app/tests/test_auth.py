"""Tests for authentication endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    resp = await client.post("/api/v1/auth/register", json={
        "name": "Alice",
        "email": "alice@example.com",
        "password": "securepassword1",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "alice@example.com"
    assert data["role"] == "user"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    payload = {"name": "Bob", "email": "bob@example.com", "password": "securepassword1"}
    r1 = await client.post("/api/v1/auth/register", json=payload)
    assert r1.status_code == 201
    r2 = await client.post("/api/v1/auth/register", json=payload)
    assert r2.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "name": "Carol",
        "email": "carol@example.com",
        "password": "securepassword1",
    })
    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "carol@example.com", "password": "securepassword1"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "name": "Dave",
        "email": "dave@example.com",
        "password": "correctpassword",
    })
    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "dave@example.com", "password": "wrongpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_me_requires_auth(client: AsyncClient):
    resp = await client.get("/api/v1/users/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_me_with_auth(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "name": "Eve",
        "email": "eve@example.com",
        "password": "securepassword1",
    })
    login = await client.post(
        "/api/v1/auth/login",
        data={"username": "eve@example.com", "password": "securepassword1"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = login.json()["access_token"]
    resp = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "eve@example.com"


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "name": "Frank",
        "email": "frank@example.com",
        "password": "securepassword1",
    })
    login = await client.post(
        "/api/v1/auth/login",
        data={"username": "frank@example.com", "password": "securepassword1"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    refresh_token = login.json()["refresh_token"]
    resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    # New refresh token must be different (rotation).
    assert data["refresh_token"] != refresh_token


@pytest.mark.asyncio
async def test_logout(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "name": "Grace",
        "email": "grace@example.com",
        "password": "securepassword1",
    })
    login = await client.post(
        "/api/v1/auth/login",
        data={"username": "grace@example.com", "password": "securepassword1"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    refresh_token = login.json()["refresh_token"]
    resp = await client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    # Attempt to refresh after logout should fail.
    resp2 = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert resp2.status_code == 401

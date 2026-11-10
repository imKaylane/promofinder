"""
GestãoPro — Testes de Autenticação
Portado/adaptado de: backend/app/tests/test_auth.py (TechDeals AI)
"""
import pytest


def register(client, name="Alice", email="alice@test.com", password="senha1234"):
    return client.post("/api/v1/auth/register", json={"name": name, "email": email, "password": password})


def login(client, email="alice@test.com", password="senha1234"):
    return client.post("/api/v1/auth/login", json={"email": email, "password": password})


def test_register_success(client):
    res = register(client)
    assert res.status_code == 201
    data = res.get_json()
    assert data["email"] == "alice@test.com"
    assert data["role"] == "user"
    assert "id" in data


def test_register_duplicate_email(client):
    register(client, email="dup@test.com")
    res = register(client, name="Dup2", email="dup@test.com")
    assert res.status_code == 409


def test_register_short_password(client):
    res = register(client, email="short@test.com", password="123")
    assert res.status_code == 400


def test_login_success(client):
    register(client, name="Bob", email="bob@test.com")
    res = login(client, "bob@test.com")
    assert res.status_code == 200
    data = res.get_json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    register(client, name="Carol", email="carol@test.com")
    res = login(client, "carol@test.com", "wrongpass")
    assert res.status_code == 401


def test_get_me_requires_auth(client):
    res = client.get("/api/v1/users/me")
    assert res.status_code == 401


def test_get_me_with_auth(client):
    register(client, name="Dave", email="dave@test.com")
    token_res = login(client, "dave@test.com")
    token = token_res.get_json()["access_token"]
    res = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.get_json()["email"] == "dave@test.com"


def test_refresh_token(client):
    register(client, name="Eve", email="eve@test.com")
    login_res = login(client, "eve@test.com")
    old_refresh = login_res.get_json()["refresh_token"]
    res = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert res.status_code == 200
    data = res.get_json()
    assert "access_token" in data
    # Token rotation: new refresh token must differ
    assert data["refresh_token"] != old_refresh


def test_logout(client):
    register(client, name="Frank", email="frank@test.com")
    login_res = login(client, "frank@test.com")
    refresh_token = login_res.get_json()["refresh_token"]
    res = client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token})
    assert res.status_code == 200
    # After logout refresh should fail
    res2 = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert res2.status_code == 401

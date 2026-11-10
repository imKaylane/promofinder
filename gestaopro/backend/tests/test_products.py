"""GestãoPro — Testes de Produtos (EX3 + EX4)"""
import pytest


def _auth_header(client):
    client.post("/api/v1/auth/register",
                json={"name": "Test", "email": "t@test.com", "password": "senha1234"})
    res = client.post("/api/v1/auth/login",
                      json={"email": "t@test.com", "password": "senha1234"})
    token = res.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_product(client):
    headers = _auth_header(client)
    res = client.post("/api/v1/products", json={
        "name": "Notebook Gamer", "sku": "NB-001", "price": 4999.99,
        "stock_qty": 10, "unit": "un", "status": "active",
    }, headers=headers)
    assert res.status_code == 201
    data = res.get_json()
    assert data["sku"] == "NB-001"
    assert data["name"] == "Notebook Gamer"


def test_list_products(client):
    headers = _auth_header(client)
    res = client.get("/api/v1/products", headers=headers)
    assert res.status_code == 200
    data = res.get_json()
    assert "items" in data
    assert "total" in data
    assert "pages" in data


def test_get_product_not_found(client):
    headers = _auth_header(client)
    res = client.get("/api/v1/products/99999", headers=headers)
    assert res.status_code == 404


def test_create_duplicate_sku(client):
    headers = _auth_header(client)
    client.post("/api/v1/products",
                json={"name": "Produto A", "sku": "DUP-001", "price": 100},
                headers=headers)
    res = client.post("/api/v1/products",
                      json={"name": "Produto B", "sku": "DUP-001", "price": 200},
                      headers=headers)
    assert res.status_code == 409


def test_update_product(client):
    headers = _auth_header(client)
    create = client.post("/api/v1/products",
                         json={"name": "Teclado", "sku": "KB-001", "price": 199.9},
                         headers=headers)
    pid = create.get_json()["id"]
    res = client.put(f"/api/v1/products/{pid}",
                     json={"name": "Teclado Mecânico", "price": 299.9},
                     headers=headers)
    assert res.status_code == 200
    assert res.get_json()["name"] == "Teclado Mecânico"


def test_delete_product(client):
    headers = _auth_header(client)
    create = client.post("/api/v1/products",
                         json={"name": "Mouse", "sku": "MS-001", "price": 89.9},
                         headers=headers)
    pid = create.get_json()["id"]
    res = client.delete(f"/api/v1/products/{pid}", headers=headers)
    assert res.status_code == 204
    # Verify deleted
    assert client.get(f"/api/v1/products/{pid}", headers=headers).status_code == 404


def test_products_require_auth(client):
    assert client.get("/api/v1/products").status_code == 401
    assert client.post("/api/v1/products", json={}).status_code == 401

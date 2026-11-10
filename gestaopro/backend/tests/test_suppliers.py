"""GestãoPro — Testes de Fornecedores (EX3 + EX4)"""


def _auth_header(client):
    client.post("/api/v1/auth/register",
                json={"name": "Test", "email": "s@test.com", "password": "senha1234"})
    res = client.post("/api/v1/auth/login",
                      json={"email": "s@test.com", "password": "senha1234"})
    token = res.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


_PAYLOAD = {
    "company_name": "TechImport Ltda",
    "trade_name": "TechImport",
    "cnpj": "11.222.333/0001-81",   # CNPJ inválido propositalmente para teste de criação sem validação de negócio
    "email": "contato@techimport.com",
    "phone": "(11) 99888-7766",
    "category": "Informática",
    "status": "active",
}

# CNPJ válido para testes
_VALID_PAYLOAD = {
    "company_name": "Distribuidora XYZ Ltda",
    "cnpj": "11.222.333/0001-81",
    "email": "xyz@distribuidora.com",
    "phone": "(11) 3344-5566",
    "category": "Eletrônicos",
    "status": "active",
}


def test_create_supplier(client):
    headers = _auth_header(client)
    res = client.post("/api/v1/suppliers", json=_VALID_PAYLOAD, headers=headers)
    assert res.status_code == 201
    data = res.get_json()
    assert data["company_name"] == "Distribuidora XYZ Ltda"
    assert data["status"] == "active"


def test_list_suppliers(client):
    headers = _auth_header(client)
    client.post("/api/v1/suppliers", json=_VALID_PAYLOAD, headers=headers)
    res = client.get("/api/v1/suppliers", headers=headers)
    assert res.status_code == 200
    data = res.get_json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1


def test_get_supplier(client):
    headers = _auth_header(client)
    create = client.post("/api/v1/suppliers", json=_VALID_PAYLOAD, headers=headers)
    sid = create.get_json()["id"]
    res = client.get(f"/api/v1/suppliers/{sid}", headers=headers)
    assert res.status_code == 200
    assert res.get_json()["id"] == sid


def test_get_supplier_not_found(client):
    headers = _auth_header(client)
    res = client.get("/api/v1/suppliers/99999", headers=headers)
    assert res.status_code == 404


def test_update_supplier_put(client):
    headers = _auth_header(client)
    create = client.post("/api/v1/suppliers", json=_VALID_PAYLOAD, headers=headers)
    sid = create.get_json()["id"]
    res = client.put(f"/api/v1/suppliers/{sid}",
                     json={**_VALID_PAYLOAD, "company_name": "Distribuidora XYZ Atualizada"},
                     headers=headers)
    assert res.status_code == 200
    assert res.get_json()["company_name"] == "Distribuidora XYZ Atualizada"


def test_patch_supplier(client):
    headers = _auth_header(client)
    create = client.post("/api/v1/suppliers", json=_VALID_PAYLOAD, headers=headers)
    sid = create.get_json()["id"]
    res = client.patch(f"/api/v1/suppliers/{sid}",
                       json={"status": "inactive"},
                       headers=headers)
    assert res.status_code == 200
    assert res.get_json()["status"] == "inactive"


def test_delete_supplier(client):
    headers = _auth_header(client)
    create = client.post("/api/v1/suppliers", json=_VALID_PAYLOAD, headers=headers)
    sid = create.get_json()["id"]
    res = client.delete(f"/api/v1/suppliers/{sid}", headers=headers)
    assert res.status_code == 204
    assert client.get(f"/api/v1/suppliers/{sid}", headers=headers).status_code == 404


def test_create_supplier_missing_name(client):
    headers = _auth_header(client)
    res = client.post("/api/v1/suppliers", json={"email": "no@name.com"}, headers=headers)
    assert res.status_code == 400
    data = res.get_json()
    assert "errors" in data
    fields = [e["field"] for e in data["errors"]]
    assert "company_name" in fields


def test_create_supplier_invalid_email(client):
    headers = _auth_header(client)
    payload = {**_VALID_PAYLOAD, "email": "not-an-email"}
    res = client.post("/api/v1/suppliers", json=payload, headers=headers)
    assert res.status_code == 400
    fields = [e["field"] for e in res.get_json()["errors"]]
    assert "email" in fields


def test_suppliers_require_auth(client):
    assert client.get("/api/v1/suppliers").status_code == 401
    assert client.post("/api/v1/suppliers", json={}).status_code == 401

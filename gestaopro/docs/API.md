# GestãoPro — Documentação da API REST (EX4)

Base URL: `http://localhost:5000/api/v1`

## Autenticação

Todas as rotas (exceto `/auth/register` e `/auth/login`) exigem um **Bearer Token JWT** no header:

```
Authorization: Bearer <access_token>
```

O token é obtido via `POST /auth/login`. Expira em 30 minutos (configurável em `.env`).

---

## Códigos HTTP utilizados

| Código | Significado                               |
|--------|-------------------------------------------|
| 200    | OK — operação bem-sucedida                |
| 201    | Created — recurso criado com sucesso      |
| 204    | No Content — recurso excluído             |
| 400    | Bad Request — dados inválidos             |
| 401    | Unauthorized — token ausente ou inválido  |
| 403    | Forbidden — permissão insuficiente        |
| 404    | Not Found — recurso não encontrado        |
| 409    | Conflict — duplicidade (e-mail, SKU etc.) |
| 500    | Internal Server Error                     |

---

## Auth — `/api/v1/auth`

### POST /auth/register
Cadastra um novo usuário.

**Body:**
```json
{
  "name": "João Silva",
  "email": "joao@empresa.com",
  "password": "Senha@2025"
}
```

**Resposta 201:**
```json
{ "id": 2, "name": "João Silva", "email": "joao@empresa.com", "role": "user", "is_active": true, "created_at": "..." }
```

---

### POST /auth/login
Autentica e retorna tokens JWT.

**Body:**
```json
{ "email": "admin@gestaopro.local", "password": "Admin@123" }
```

**Resposta 200:**
```json
{
  "access_token": "<JWT>",
  "refresh_token": "<JWT>",
  "token_type": "bearer"
}
```

---

### POST /auth/refresh
Renova o `access_token` com um `refresh_token` válido.

**Body:** `{ "refresh_token": "<JWT>" }`

**Resposta 200:** `{ "access_token": "...", "refresh_token": "...", "token_type": "bearer" }`

---

### POST /auth/logout
Revoga o `refresh_token`.

**Body:** `{ "refresh_token": "<JWT>" }`  
**Resposta 200:** `{ "message": "Logged out successfully" }`

---

### GET /auth/me  *(requer token)*
Retorna o perfil do usuário autenticado.

---

## Produtos — `/api/v1/products`

Todos os endpoints exigem autenticação.

### GET /products
Listagem paginada com busca e filtros.

**Query params:**
| Param        | Padrão | Descrição              |
|--------------|--------|------------------------|
| page         | 1      | Número da página       |
| limit        | 20     | Itens por página (max 50) |
| search       | —      | Busca em nome e SKU    |
| status       | —      | Filtro: active/inactive |
| category_id  | —      | Filtro por categoria   |

**Resposta 200:**
```json
{
  "items": [ { "id": 1, "name": "Notebook", "sku": "NB-001", "price": 3499.90, ... } ],
  "total": 10, "page": 1, "limit": 20, "pages": 1
}
```

---

### GET /products/:id
Retorna um produto pelo ID. **404** se não existir.

---

### POST /products
Cria um produto. Campos obrigatórios: `name`, `sku`.

**Body:**
```json
{
  "name": "Notebook ProBook",
  "sku": "NB-999",
  "price": 3499.90,
  "cost": 2800.00,
  "stock_qty": 10,
  "unit": "un",
  "category_id": 2,
  "release_date": "2024-01-15",
  "status": "active"
}
```

**Resposta 201:** objeto do produto criado.  
**400:** erros de validação com array `errors`.  
**409:** SKU já cadastrado.

---

### PUT /products/:id
Substitui os campos enviados. SKU pode ser alterado (verificação de unicidade).

**Resposta 200:** produto atualizado.

---

### DELETE /products/:id
Remove o produto. **Resposta 204** (sem corpo).

---

## Clientes — `/api/v1/customers`

### GET /customers
**Query:** `page`, `limit`, `search`, `status`

### GET /customers/:id

### POST /customers
Campos obrigatórios: `name`.

```json
{
  "name": "Maria Costa",
  "person_type": "PF",
  "email": "maria@email.com",
  "phone": "(11) 99123-4567",
  "document": "529.982.247-25",
  "birth_date": "1990-05-20",
  "credit_limit": 5000.00,
  "city": "São Paulo",
  "state": "SP",
  "zip_code": "01310-100",
  "status": "active"
}
```

**Validações:** CPF/CNPJ (dígitos verificadores), e-mail, telefone BR, CEP, UF.

### PUT /customers/:id
### DELETE /customers/:id — **204**

---

## Fornecedores — `/api/v1/suppliers`

### GET /suppliers
**Query:** `page`, `limit`, `search`, `status`

### GET /suppliers/:id

### POST /suppliers
Campos obrigatórios: `company_name`.

```json
{
  "company_name": "TechImport Ltda",
  "trade_name": "TechImport",
  "cnpj": "11.222.333/0001-81",
  "email": "compras@techimport.com",
  "phone": "(11) 3456-7890",
  "contact": "Roberto Lima",
  "address": "Av. Paulista, 1000",
  "city": "São Paulo",
  "state": "SP",
  "zip_code": "01310-100",
  "category": "Informática",
  "contract_date": "2024-01-15",
  "status": "active"
}
```

**Validações:** CNPJ (dígitos), e-mail, telefone BR, CEP, UF, data ISO.

### PUT /suppliers/:id — substitui campos
### PATCH /suppliers/:id — atualiza campos parcialmente
### DELETE /suppliers/:id — **204**

---

## Usuários (admin) — `/api/v1`

### GET /admin/users
Lista todos os usuários. Requer `role = admin`.

### GET /users/me
Perfil do usuário autenticado.

### GET /audit
Lista logs de auditoria. Requer `role = admin`.

---

## Erros de validação

Resposta **400** com array de erros:

```json
{
  "detail": "Validation error",
  "errors": [
    { "field": "email", "code": "VALIDATION_EMAIL", "message": "Invalid email" },
    { "field": "document", "code": "VALIDATION_DOCUMENT", "message": "Invalid CPF/CNPJ" }
  ]
}
```

### Códigos de erro (EX3/EX4)

| Código                | Campo     | Descrição                |
|-----------------------|-----------|--------------------------|
| VALIDATION_REQUIRED   | qualquer  | Campo obrigatório vazio  |
| VALIDATION_EMAIL      | email     | E-mail inválido          |
| VALIDATION_PHONE      | phone     | Telefone inválido (BR)   |
| VALIDATION_CEP        | zip_code  | CEP inválido             |
| VALIDATION_UF         | state     | UF inválida              |
| VALIDATION_DOCUMENT   | document  | CPF/CNPJ inválido        |
| VALIDATION_CNPJ       | cnpj      | CNPJ inválido            |
| VALIDATION_DATE       | *_date    | Data não está em YYYY-MM-DD |
| VALIDATION_POSITIVE   | price/cost/credit_limit | Deve ser ≥ 0 |

---

## CORS

Todas as rotas `/api/*` aceitam origens configuradas via `CORS_ORIGINS` no `.env`.

Padrão de desenvolvimento: `*` (todas as origens).  
Produção: definir explicitamente, ex.: `CORS_ORIGINS=https://gestaopro.empresa.com`.

---

## Importar no Postman / Insomnia

1. Abrir Postman → Import → Upload File  
2. Selecionar `docs/GestãoPro.postman_collection.json`  
3. Executar **Login** para popular automaticamente a variável `access_token`  
4. Todos os demais requests usam `{{access_token}}` automaticamente

---

*Documentação gerada em 2025 — GestãoPro v1.0*

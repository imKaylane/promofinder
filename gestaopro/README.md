# GestãoPro — Sistema ERP

**Sistema integrado de gestão empresarial.**

---

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.x · Flask 3 · SQLAlchemy 2 (síncrono) |
| Banco de dados | MySQL 8 |
| Frontend | HTML5 · CSS3 · JavaScript puro |
| Autenticação | JWT (PyJWT) + bcrypt |
| Mobile | Kotlin + Android Studio (pasta `mobile/`) |

---

## Instalação rápida

### 1. Banco de dados

```bash
mysql -u root -p < database/schema.sql
```

### 2. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt

cp .env.example .env
# Edite .env com suas credenciais MySQL

python run.py
# Servidor em http://localhost:5000
```

### 3. Frontend

Abra `index.html` diretamente no navegador ou sirva com qualquer servidor estático:

```bash
# Python built-in server (na pasta gestaopro/)
python -m http.server 5500
# Acesse http://localhost:5500
```

---

## Endpoints da API

### Autenticação

| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/api/v1/auth/register` | Registrar novo usuário |
| POST | `/api/v1/auth/login` | Login (JSON ou form-data) |
| POST | `/api/v1/auth/refresh` | Renovar token |
| POST | `/api/v1/auth/logout` | Revogar token |
| GET | `/api/v1/users/me` | Perfil do usuário autenticado |

### Produtos (EX3 + EX4 — CRUD completo)

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/v1/products` | Listar (busca, filtros, paginação) |
| GET | `/api/v1/products/<id>` | Detalhe |
| POST | `/api/v1/products` | Criar |
| PUT | `/api/v1/products/<id>` | Atualizar |
| DELETE | `/api/v1/products/<id>` | Excluir |

### Clientes (EX3 + EX4 — CRUD completo)

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/v1/customers` | Listar |
| GET | `/api/v1/customers/<id>` | Detalhe |
| POST | `/api/v1/customers` | Criar |
| PUT | `/api/v1/customers/<id>` | Atualizar |
| DELETE | `/api/v1/customers/<id>` | Excluir |

### Admin (requer role=admin)

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/v1/admin/users` | Listar usuários |
| GET | `/api/v1/audit` | Log de auditoria |

---

## Usuário admin padrão

- Email: `admin@gestaopro.local`
- Senha: `Admin@123`

⚠️ Troque a senha após a primeira instalação.

---

## Executar testes

```bash
cd backend
python -m pytest tests/ -v
```

---

## Estrutura de pastas

```
gestaopro/
├── frontend/
│   ├── css/main.css          # CSS3: Flexbox, Grid, responsividade
│   ├── js/                   # i18n.js, layout.js, auth.js, ui.js
│   ├── pages/                # dashboard, clientes, produtos, ...
│   └── i18n/                 # pt-BR.json, en.json (EX2)
├── backend/
│   ├── app/
│   │   ├── api/              # Blueprints Flask (EX4)
│   │   ├── models/           # SQLAlchemy models + database.py
│   │   ├── repositories/     # Queries parametrizadas (EX3)
│   │   ├── services/         # security.py (JWT + bcrypt)
│   │   └── middleware/       # auth.py (decorators)
│   ├── tests/                # pytest
│   └── run.py
├── database/
│   └── schema.sql            # Script MySQL (EX3)
├── mobile/                   # App Kotlin (EX5, EX7)
├── docs/
└── index.html                # Login
```

---

## Exercícios implementados

| Ex | Descrição | Status |
|---|---|---|
| EX1 | Interface Web responsiva (HTML5/CSS3/JS, hamburger, 3+ páginas) | ✅ |
| EX2 | Internacionalização PT-BR/EN com arquivos JSON e Intl | ✅ |
| EX3 | CRUD MySQL — Produtos e Clientes com schema.sql | ✅ |
| EX4 | API REST Flask com JWT, CORS, validação, códigos HTTP | ✅ |
| EX5 | App Android Kotlin | 🔧 Em desenvolvimento |
| EX6 | Frontend consumindo API via Fetch API | ✅ (integrado ao EX1) |
| EX7 | Android consumindo API | 🔧 Em desenvolvimento |
| EX8 | Calculadora sem eval(), histórico, precedência, relatório | ✅ |
| EX9 | ERP completo MVC, todos os módulos, ERD | ✅ (estrutura base) |

# TechDeals AI

**Plataforma inteligente de busca, monitoramento e recomendação de promoções de tecnologia.**

Pesquise produtos no Mercado Livre em linguagem natural, monitore o histórico de preços e receba alertas quando um produto atingir seu preço alvo — tudo com auxílio de inteligência artificial.

---

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.15 · FastAPI · SQLAlchemy (async) · Alembic |
| Banco de dados | PostgreSQL 16 |
| Filas | Celery + Redis |
| Frontend | React 18 · TypeScript · Vite · Tailwind CSS |
| IA | OpenAI GPT-4o-mini **ou** IBM watsonx (plugável; app funciona sem IA) |
| Containers | Docker Compose |

---

## Início rápido

### 1. Pré-requisitos

- Docker e Docker Compose
- (Opcional) Python 3.15 + Node 20 para desenvolvimento local

### 2. Configurar variáveis de ambiente

```bash
cp .env.example .env
# Edite .env e preencha pelo menos SECRET_KEY e as credenciais MELI
```

Variáveis obrigatórias:

| Variável | Descrição |
|---|---|
| `SECRET_KEY` | Chave secreta JWT (gere com `openssl rand -hex 32`) |
| `MELI_CLIENT_ID` | App ID do Mercado Livre |
| `MELI_CLIENT_SECRET` | Secret do app Mercado Livre |

Variáveis opcionais para IA:

| Variável | Descrição |
|---|---|
| `AI_PROVIDER` | `openai`, `watsonx` ou `disabled` (padrão) |
| `OPENAI_API_KEY` | Chave OpenAI (se `AI_PROVIDER=openai`) |
| `WATSONX_API_KEY` | Chave IBM watsonx (se `AI_PROVIDER=watsonx`) |
| `WATSONX_PROJECT_ID` | ID do projeto watsonx |

### 3. Subir os containers

```bash
docker compose up --build
```

| Serviço | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

### 4. Aplicar migrations

```bash
docker compose exec backend alembic upgrade head
```

---

## Desenvolvimento local (sem Docker)

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt

# Configure DATABASE_URL para apontar para o PostgreSQL local
# e as demais variáveis em .env

uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev                     # http://localhost:5173
```

O Vite está configurado para fazer proxy de `/api` para `http://localhost:8000`, então o backend e frontend coexistem sem CORS no desenvolvimento.

---

## Executar testes

```bash
cd backend
python -m pytest                # SQLite in-memory, sem PostgreSQL necessário
python -m pytest -v             # verbose
python -m pytest app/tests/test_deal_analyzer.py  # somente análise de deals
```

---

## Endpoints principais

### Autenticação

| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/api/v1/auth/register` | Cadastrar novo usuário |
| POST | `/api/v1/auth/login` | Login (form-data) |
| POST | `/api/v1/auth/refresh` | Renovar token |
| POST | `/api/v1/auth/logout` | Revogar token |

### Produtos

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/v1/products/search` | Busca na base local |
| GET | `/api/v1/products/search/live` | Busca ao vivo no Mercado Livre |
| GET | `/api/v1/products/{id}` | Detalhe do produto |
| GET | `/api/v1/products/{id}/offers` | Ofertas do produto |
| POST | `/api/v1/products/{id}/favorite` | Adicionar aos favoritos |
| DELETE | `/api/v1/products/{id}/favorite` | Remover dos favoritos |

### Ofertas / Deals

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/v1/deals` | Listar melhores ofertas (ranqueadas) |

### IA

| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/api/v1/ai/search` | Busca com linguagem natural |
| GET | `/api/v1/ai/analyze/{offer_id}` | Análise de deal com IA |

### Usuário

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/v1/users/me` | Perfil do usuário |
| GET | `/api/v1/users/me/alerts` | Alertas de preço |
| POST | `/api/v1/users/me/alerts` | Criar alerta |
| DELETE | `/api/v1/users/me/alerts/{id}` | Excluir alerta |
| GET | `/api/v1/users/me/notifications` | Notificações |

---

## Arquitetura

```
┌────────────────────────────────────────────────────────────────┐
│  React Frontend (SPA)                                          │
│  React Router · Tailwind CSS · Axios                           │
└───────────────────────────────┬────────────────────────────────┘
                                │ REST /api/v1/
┌───────────────────────────────▼────────────────────────────────┐
│  FastAPI Backend                                               │
│  auth · products · deals · ai · users · admin                  │
│  JWT auth · SQLAlchemy async · Pydantic v2                     │
└──────┬──────────────┬──────────────────────────────────────────┘
       │              │
┌──────▼──────┐ ┌─────▼──────────────────────────────────────────┐
│ PostgreSQL  │ │  External APIs                                  │
│  (ORM)      │ │  · api.mercadolibre.com (produtos)              │
└─────────────┘ │  · OpenAI / IBM watsonx (IA, opcional)         │
                └────────────────────────────────────────────────┘
       │
┌──────▼──────────────────────┐
│ Celery + Redis               │
│ · check_price_alerts (30m)   │
│ · refresh_deals_cache (60m)  │
└─────────────────────────────┘
```

---

## Estrutura de pastas

```
.
├── backend/
│   ├── app/
│   │   ├── ai/          # AIService (openai / watsonx / disabled)
│   │   ├── api/v1/      # Routers FastAPI
│   │   ├── core/        # Config, database, security
│   │   ├── integrations/# MercadoLivreService
│   │   ├── models/      # ORM SQLAlchemy
│   │   ├── repositories/# Queries de banco
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # DealAnalyzer
│   │   ├── tasks/       # Celery tasks
│   │   └── tests/       # pytest
│   └── alembic/         # Migrations
├── frontend/
│   └── src/
│       ├── components/  # Navbar, ProductCard
│       ├── hooks/       # useAuth, useApi
│       ├── pages/       # 9 páginas
│       ├── services/    # API wrappers
│       ├── types/       # TypeScript types
│       └── utils/       # format helpers
└── docker-compose.yml
```

---

## Licença

MIT

# TechDeals AI

**Plataforma inteligente de busca, monitoramento e recomendação de promoções de tecnologia.**

Pesquise produtos no Mercado Livre em linguagem natural, monitore o histórico de preços e receba alertas quando um produto atingir seu preço alvo — tudo com auxílio de inteligência artificial.

---

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.15 · FastAPI · SQLAlchemy (async) · Alembic |
| Banco de dados | PostgreSQL 15 |
| Filas | Celery + Redis |
| Frontend | React 18 · TypeScript · Vite · Tailwind CSS |
| IA | Google Gemini (opcional; busca no Mercado Livre funciona sem IA) |
| Containers | Docker Compose |

---

## Início rápido

### 1. Pré-requisitos

- Docker e Docker Compose
- (Opcional) Python 3.11+ + Node 20 para desenvolvimento local

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

Para evitar conflitos de portas com outra aplicação Docker, `.env` aceita
`FRONTEND_PORT`, `BACKEND_PORT`, `POSTGRES_PORT` e `REDIS_PORT`. Os valores
padrão são `5173`, `8000`, `5432` e `6379`, respectivamente.

Para conectar a conta do Mercado Livre, cadastre no portal de desenvolvedores a URL de retorno
configurada em `MELI_REDIRECT_URI`. No perfil da aplicação, clique em **Conectar Mercado Livre**.
No Compose local, use `http://localhost:<FRONTEND_PORT>/auth/mercadolivre/callback`
(`http://localhost:5174/auth/mercadolivre/callback` nesta configuração). URLs temporárias
de túneis, como `trycloudflare.com`, precisam estar ativas e cadastradas exatamente como
`MELI_REDIRECT_URI`; elas podem mudar ou expirar.
O backend troca o código OAuth e guarda os tokens no Redis; não exponha o `MELI_CLIENT_SECRET`
nem os tokens no frontend. Em produção, use Redis privado e persistente.

Variáveis opcionais para IA:

| Variável | Descrição |
|---|---|
| `AI_PROVIDER` | `gemini` ou `disabled` |
| `GEMINI_API_KEY` | Chave da API Google Gemini |
| `GEMINI_MODEL` | Modelo Gemini (padrão: `gemini-3.8-flash`) |
| `MELI_COLLECTION_QUERIES` | Termos separados por vírgula (padrão: componentes de PC, monitores, mouses e teclados) |

O worker e o Celery Beat coletam um termo a cada cinco minutos, em rodízio pela lista
configurada, evitando executar todas as buscas na mesma rodada. A busca ao vivo pela tela
**Buscar** consulta o Mercado Livre imediatamente e não depende do Gemini.
As categorias e ofertas exibidas são limitadas a peças de PC e periféricos. Livros,
instrumentos musicais, cabos, adaptadores, capas, cases, suportes e itens infantis são
descartados ou ocultados.
O idioma pode ser alterado entre português, inglês e espanhol no cabeçalho; tema claro/escuro
e idioma ficam salvos neste dispositivo.
Se o Mercado Livre retornar HTTP 403, conecte uma conta autorizada em **Perfil > Mercado Livre**.
Para a coleta periódica, deixe worker e Beat ativos.

### 3. Subir os containers

```bash
docker compose up --build
```

| Serviço | URL |
|---|---|
| Frontend | http://localhost:5173 |
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

# Configure DATABASE_URL, REDIS_URL, CELERY_BROKER_URL e CELERY_RESULT_BACKEND
# para usar localhost ao executar sem Docker
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
└─────────────┘ │  · Google Gemini (IA, opcional)                │
                └────────────────────────────────────────────────┘
       │
┌──────▼──────────────────────┐
│ Celery + Redis               │
│ · check_price_alerts (30m)   │
│ · refresh_deals_cache (60m)  │
│ · collect_meli_products (30m)│
└─────────────────────────────┘
```

---

## Estrutura de pastas

```
.
├── backend/
│   ├── app/
│   │   ├── ai/          # Gemini AIService
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


## Integração com o aplicativo Android

O app Android deve consumir o backend deste projeto; ele não deve chamar a API do Mercado Livre diretamente. A busca compartilhada está disponível em `GET /api/v1/products/search/live`, e a versão web já utiliza esse mesmo backend por meio do proxy `/api`.

- Web local: `http://localhost:5173`
- Backend local: `http://localhost:8000`
- Android Emulator: use `http://10.0.2.2:8000/` como endereço do backend (já é o padrão do app).
- Celular físico: configure o IP LAN do computador, por exemplo `-PPROMOFINDER_API_URL=http://192.168.0.10:8000/`, mantendo ambos na mesma rede.

Para iniciar o backend, copie `.env.example` para `.env`, ajuste as variáveis, execute `docker compose up --build` e aplique as migrations. O app Android e o site passam então a consultar o mesmo serviço de busca. Em produção, publique o backend em HTTPS e configure `PROMOFINDER_API_URL` com a URL HTTPS; não use o endereço do emulador.


# codigos precisos conexção 

'no terminal vs code'
deactivate
Remove-Item -Recurse -Force venv
py -3.12 -m venv venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload


'no terminal android studio'

& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" reverse tcp:8000 tcp:8000
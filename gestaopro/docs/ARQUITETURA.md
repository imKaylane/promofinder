# GestãoPro — Arquitetura do Sistema (EX9)

## Visão Geral

GestãoPro é um ERP web desenvolvido como projeto acadêmico para a Fatec Americana.  
A arquitetura segue o padrão **MVC** com separação clara de responsabilidades.

```
gestaopro/
├── backend/          # API REST — Python + Flask (porta 5000)
├── frontend/         # Interface Web — HTML5 + CSS3 + JavaScript puro
├── database/         # Scripts SQL + migrações
├── mobile/           # Aplicativo Android — Kotlin + MVVM
├── docs/             # Documentação
└── scripts/          # Scripts utilitários
```

---

## Backend (Python + Flask)

### Estrutura MVC

```
backend/
├── run.py                          # Entrypoint — inicia Flask
├── pytest.ini                      # Configuração de testes
├── requirements.txt                # Dependências Python
└── app/
    ├── __init__.py                 # create_app() — Factory Pattern
    ├── config.py                   # Variáveis de ambiente (.env)
    ├── api/                        # Controllers (Blueprints Flask)
    │   ├── auth.py                 # /api/v1/auth/*
    │   ├── products.py             # /api/v1/products/*
    │   ├── customers.py            # /api/v1/customers/*
    │   ├── suppliers.py            # /api/v1/suppliers/*
    │   └── users.py                # /api/v1/admin/* + /api/v1/audit
    ├── models/
    │   ├── database.py             # SQLAlchemy engine + session
    │   └── models.py               # Modelos ORM (15 entidades)
    ├── repositories/               # Acesso ao banco de dados
    │   ├── user_repository.py
    │   ├── product_repository.py
    │   └── customer_repository.py
    ├── services/
    │   ├── security.py             # JWT (criação, verificação)
    │   └── validators.py           # Validadores de domínio
    └── middleware/
        └── auth.py                 # require_auth, require_admin decorators
```

### Fluxo de uma Requisição

```
HTTP Request
    │
    ▼
[Flask Router] ──→ Middleware (auth.py)
                        │
                        ▼ (Token válido)
                   [Blueprint / Controller]
                        │
                    ┌───┴───┐
                    │       │
               Validators  Repository
               (services/) (repositories/)
                    │       │
                    └───┬───┘
                        │
                   [Model / DB]
                        │
                        ▼
                 JSON Response
```

### Tecnologias Backend

| Componente      | Tecnologia           | Versão  |
|-----------------|----------------------|---------|
| Framework Web   | Flask                | 3.1.0   |
| ORM             | SQLAlchemy (síncrono)| 2.0.41  |
| Autenticação    | PyJWT + bcrypt       | —       |
| Banco de Dados  | MySQL (prod) / SQLite (testes) | — |
| CORS            | flask-cors           | —       |
| Driver MySQL    | PyMySQL              | —       |

---

## Frontend (HTML5 + CSS3 + JavaScript puro)

### Estrutura

```
frontend/
├── css/
│   └── main.css                    # Design system completo (variáveis CSS, componentes)
├── js/
│   ├── config.js                   # Configuração central (API_BASE_URL, endpoints)
│   ├── i18n.js                     # Internacionalização (pt-BR, en, es)
│   ├── auth.js                     # Autenticação JWT + fetchWithAuth
│   ├── api.js                      # Módulo API (Products, Customers, Suppliers) + ViaCEP
│   ├── ui.js                       # Componentes UI (Toast, Modal, Loading)
│   ├── layout.js                   # Shell (sidebar, header, hamburger, aria)
│   ├── validators.js               # Validações frontend (CPF, CNPJ, CEP, UF)
│   └── calc-engine.js              # Motor da calculadora (Shunting-Yard, sem eval)
├── i18n/
│   ├── pt-BR.json                  # 158 chaves (idioma padrão)
│   ├── en.json                     # 158 chaves
│   └── es.json                     # 158 chaves
└── pages/
    ├── dashboard.html              # KPIs + ações rápidas
    ├── clientes.html               # CRUD completo (EX3/EX4)
    ├── produtos.html               # CRUD completo (EX3/EX4)
    ├── fornecedores.html           # CRUD completo (EX3/EX4)
    ├── vendas.html                 # Tela de vendas
    ├── pedidos.html                # Tela de pedidos
    ├── estoque.html                # Tela de estoque
    ├── financeiro.html             # Financeiro / contas
    ├── usuarios.html               # Gerenciamento de usuários (admin)
    ├── auditoria.html              # Log de auditoria
    ├── calculadora.html            # Calculadora (EX8)
    └── calculadora-relatorio.html  # Relatório de implementação (EX8)
```

### Padrão de Componentes

```
Página HTML
    │
    ├── config.js          (BASE_URL, endpoints)
    ├── i18n.js            (I18N.t(), applyAll())
    ├── ui.js              (UI.toast(), UI.openModal())
    ├── auth.js            (Auth.fetchWithAuth(), requireAuth())
    ├── layout.js          (Layout.init() → sidebar + header)
    └── api.js             (GestaoAPI.Products.list(), etc.)
```

---

## Banco de Dados (MySQL)

### Entidades e Relacionamentos (simplificado)

```
users 1──* refresh_tokens
users 1──* audit_logs
users 1──* sales (user_id)
users 1──* orders (user_id)

customers 1──* sales
customers 1──* accounts_receivable

suppliers 1──* orders
suppliers 1──* accounts_payable

categories 1──* products

products 1──* sale_items
products 1──* order_items
products 1──* stock_movements

sales 1──* sale_items
sales 1──* accounts_receivable

orders 1──* order_items
```

### Tabelas

| Tabela               | Descrição                          | Campos-chave               |
|----------------------|------------------------------------|----------------------------|
| users                | Usuários do sistema                | id, email, role, is_active |
| refresh_tokens       | Tokens de renovação JWT            | token_hash, expires_at     |
| categories           | Categorias de produtos             | id, name                   |
| products             | Produtos do ERP                    | id, sku, price, stock_qty  |
| customers            | Clientes                           | id, person_type, document  |
| suppliers            | Fornecedores                       | id, cnpj, contract_date    |
| sales                | Vendas                             | id, total, payment_method  |
| sale_items           | Itens de venda                     | sale_id, product_id        |
| orders               | Pedidos de compra                  | id, supplier_id, status    |
| order_items          | Itens de pedido                    | order_id, product_id       |
| stock_movements      | Movimentações de estoque           | product_id, type, quantity |
| accounts_payable     | Contas a pagar                     | amount, due_date, status   |
| accounts_receivable  | Contas a receber                   | amount, due_date, status   |
| audit_logs           | Auditoria de ações                 | action, entity, entity_id  |

---

## Aplicativo Mobile (Kotlin + Android)

Localizado em: `mobile/GestaoProApp/`

### Arquitetura MVVM

```
app/
└── src/main/java/br/com/gestaopro/
    ├── data/
    │   ├── api/          ApiService.kt, RetrofitClient.kt
    │   ├── model/        User, Product, Customer, Supplier (data classes)
    │   └── repository/   AuthRepository, ProductRepository
    ├── ui/
    │   ├── auth/         LoginActivity, LoginViewModel
    │   ├── products/     ProductListFragment, ProductViewModel
    │   └── common/       BaseFragment, LoadingDialog
    └── util/
        ├── SecureStorage.kt   (EncryptedSharedPreferences)
        └── Extensions.kt
```

### Recursos de Internacionalização

```
res/
├── values/strings.xml       (pt-BR — padrão)
├── values-en/strings.xml    (English)
└── values-es/strings.xml    (Español)
```

---

## Segurança

| Aspecto              | Implementação                                    |
|----------------------|--------------------------------------------------|
| Senhas               | bcrypt (custo 12)                                |
| Autenticação         | JWT Bearer Token (acesso 30min, refresh 7dias)   |
| Transporte           | HTTPS em produção (dev: HTTP localhost)           |
| Secrets no código    | Nunca — usam variáveis de ambiente (.env)        |
| SQL Injection        | SQLAlchemy ORM (consultas parametrizadas)        |
| XSS                  | `esc()` em todas as interpolações HTML           |
| 500 errors           | `logger.exception()` — nunca expõe stack trace  |
| Token Android        | EncryptedSharedPreferences                       |

---

## Testes

| Módulo               | Arquivo                     | Testes |
|----------------------|-----------------------------|--------|
| Autenticação         | test_auth.py                | 9      |
| Produtos             | test_products.py            | 7      |
| Fornecedores         | test_suppliers.py           | 10     |
| Validadores          | test_validators.py          | 22     |
| Calculadora (Node)   | scripts/test_calc.js        | 40     |
| **Total**            |                             | **88** |

---

## Como Executar

### Backend

```bash
cd gestaopro/backend
pip install -r requirements.txt
cp .env.example .env          # editar com credenciais MySQL
python run.py
```

### Frontend

Servido pelo próprio Flask em `http://localhost:5000`

### Banco de Dados

```bash
mysql -u root -p < database/schema.sql
```

### Testes Python

```bash
cd gestaopro/backend
python -m pytest tests/ -v
```

### Testes da Calculadora

```bash
node gestaopro/scripts/test_calc.js
```

---

*GestãoPro — Fatec Americana — 2025*

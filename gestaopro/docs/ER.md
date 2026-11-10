# GestãoPro — Diagrama Entidade-Relacionamento (ERD)

## Diagrama ERD (Mermaid)

```mermaid
erDiagram
    users {
        int id PK
        varchar name
        varchar email UK
        varchar password_hash
        varchar role
        bool is_active
        datetime created_at
        datetime updated_at
    }

    refresh_tokens {
        int id PK
        int user_id FK
        varchar token_hash UK
        datetime expires_at
        bool revoked
        datetime created_at
    }

    categories {
        int id PK
        varchar name UK
        text description
        datetime created_at
    }

    products {
        int id PK
        varchar name
        varchar sku UK
        int category_id FK
        decimal price
        decimal cost
        int stock_qty
        varchar unit
        text description
        date release_date
        varchar status
        datetime created_at
        datetime updated_at
    }

    customers {
        int id PK
        varchar name
        char person_type
        varchar email
        varchar phone
        varchar document
        date birth_date
        decimal credit_limit
        varchar address
        varchar city
        char state
        varchar zip_code
        varchar status
        datetime created_at
        datetime updated_at
    }

    suppliers {
        int id PK
        varchar company_name
        varchar trade_name
        varchar cnpj
        varchar email
        varchar phone
        varchar contact
        varchar address
        varchar city
        char state
        varchar zip_code
        varchar category
        date contract_date
        varchar status
        datetime created_at
        datetime updated_at
    }

    sales {
        int id PK
        int customer_id FK
        int user_id FK
        datetime sale_date
        decimal total
        decimal discount
        varchar payment_method
        varchar status
        text notes
        datetime created_at
    }

    sale_items {
        int id PK
        int sale_id FK
        int product_id FK
        decimal quantity
        decimal unit_price
        decimal subtotal
    }

    orders {
        int id PK
        int supplier_id FK
        int user_id FK
        datetime order_date
        datetime expected_date
        decimal total
        varchar status
        text notes
        datetime created_at
    }

    order_items {
        int id PK
        int order_id FK
        int product_id FK
        decimal quantity
        decimal unit_price
        decimal subtotal
    }

    stock_movements {
        int id PK
        int product_id FK
        int user_id FK
        varchar type
        decimal quantity
        int reference_id
        varchar reference_type
        text notes
        datetime created_at
    }

    accounts_payable {
        int id PK
        varchar description
        int supplier_id FK
        decimal amount
        datetime due_date
        datetime paid_at
        varchar status
        text notes
        datetime created_at
    }

    accounts_receivable {
        int id PK
        varchar description
        int customer_id FK
        int sale_id FK
        decimal amount
        datetime due_date
        datetime paid_at
        varchar status
        text notes
        datetime created_at
    }

    audit_logs {
        int id PK
        int user_id FK
        varchar action
        varchar entity
        int entity_id
        text description
        text details
        varchar ip_address
        datetime created_at
    }

    %% Relacionamentos
    users ||--o{ refresh_tokens : "possui"
    users ||--o{ audit_logs : "gera"
    users ||--o{ sales : "registra"
    users ||--o{ orders : "cria"
    users ||--o{ stock_movements : "executa"

    categories ||--o{ products : "classifica"

    customers ||--o{ sales : "realiza"
    customers ||--o{ accounts_receivable : "deve"

    suppliers ||--o{ orders : "recebe"
    suppliers ||--o{ accounts_payable : "gera"

    products ||--o{ sale_items : "compõe"
    products ||--o{ order_items : "compõe"
    products ||--o{ stock_movements : "movimenta"

    sales ||--o{ sale_items : "contém"
    sales ||--o{ accounts_receivable : "origina"

    orders ||--o{ order_items : "contém"
```

---

## Descrição dos Relacionamentos

### Usuários e Segurança
- `users` ← 1:N → `refresh_tokens`: Um usuário pode ter múltiplos tokens de renovação ativos
- `users` ← 1:N → `audit_logs`: Toda ação autenticada gera um registro de auditoria

### Produtos e Categorias
- `categories` ← 1:N → `products`: Um produto pertence a uma categoria

### Ciclo de Vendas
- `customers` ← 1:N → `sales`: Um cliente pode ter múltiplas vendas
- `sales` ← 1:N → `sale_items`: Uma venda contém múltiplos itens
- `products` ← 1:N → `sale_items`: Um produto pode aparecer em múltiplos itens de venda
- `sales` ← 1:N → `accounts_receivable`: Vendas geram contas a receber

### Ciclo de Compras
- `suppliers` ← 1:N → `orders`: Um fornecedor pode receber múltiplos pedidos
- `orders` ← 1:N → `order_items`: Um pedido contém múltiplos itens
- `products` ← 1:N → `order_items`: Um produto pode aparecer em múltiplos itens de pedido
- `suppliers` ← 1:N → `accounts_payable`: Fornecedores geram contas a pagar

### Estoque
- `products` ← 1:N → `stock_movements`: Todo movimentação de estoque referencia um produto
- Tipos de movimentação: `in` (entrada), `out` (saída), `adjust` (ajuste)

---

## Cardinalidade das Entidades Principais

| Entidade           | Registros esperados (produção) |
|--------------------|-------------------------------|
| users              | Dezenas (equipe interna)      |
| categories         | Dezenas                       |
| products           | Centenas a milhares           |
| customers          | Milhares                      |
| suppliers          | Dezenas a centenas            |
| sales              | Milhares / mês                |
| sale_items         | Dezenas de milhares / mês     |
| orders             | Centenas / mês                |
| stock_movements    | Dezenas de milhares           |
| audit_logs         | Alta frequência (> 1M/ano)    |

---

## Índices Relevantes

| Tabela              | Índice                   | Tipo    | Justificativa                |
|---------------------|--------------------------|---------|------------------------------|
| users               | email                    | UNIQUE  | Login, unicidade             |
| products            | sku                      | UNIQUE  | Identificador de produto     |
| products            | name                     | INDEX   | Busca textual frequente      |
| products            | status                   | INDEX   | Filtro de ativos/inativos    |
| customers           | name                     | INDEX   | Busca textual                |
| customers           | status                   | INDEX   | Filtro                       |
| suppliers           | company_name             | INDEX   | Busca textual                |
| audit_logs          | entity                   | INDEX   | Filtra logs por entidade     |
| audit_logs          | created_at               | INDEX   | Consultas por período        |
| stock_movements     | product_id               | INDEX   | Histórico de produto         |
| accounts_payable    | due_date, status         | INDEX   | Dashboard financeiro         |
| accounts_receivable | due_date, status         | INDEX   | Dashboard financeiro         |

---

*GestãoPro — Fatec Americana — 2025*

-- =========================================================
-- GestãoPro — Script de instalação do banco de dados MySQL
-- EX3: Script SQL de instalação com todas as entidades ERP
-- Executar: mysql -u root -p < schema.sql
-- =========================================================

CREATE DATABASE IF NOT EXISTS gestaopro
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE gestaopro;

-- ── Usuários ──────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
  id            INT            NOT NULL AUTO_INCREMENT,
  name          VARCHAR(255)   NOT NULL,
  email         VARCHAR(255)   NOT NULL,
  password_hash VARCHAR(255)   NOT NULL,
  role          VARCHAR(50)    NOT NULL DEFAULT 'user',
  is_active     TINYINT(1)     NOT NULL DEFAULT 1,
  created_at    DATETIME(6)    NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at    DATETIME(6)    NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_users_email (email),
  INDEX ix_users_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Refresh Tokens ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS refresh_tokens (
  id          INT          NOT NULL AUTO_INCREMENT,
  user_id     INT          NOT NULL,
  token_hash  VARCHAR(255) NOT NULL,
  expires_at  DATETIME(6)  NOT NULL,
  revoked     TINYINT(1)   NOT NULL DEFAULT 0,
  created_at  DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_refresh_tokens_hash (token_hash),
  INDEX ix_refresh_user (user_id),
  CONSTRAINT fk_refresh_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Categorias ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS categories (
  id          INT          NOT NULL AUTO_INCREMENT,
  name        VARCHAR(255) NOT NULL,
  description TEXT,
  created_at  DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_categories_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Produtos ──────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS products (
  id          INT             NOT NULL AUTO_INCREMENT,
  name        VARCHAR(512)    NOT NULL,
  sku         VARCHAR(100)    NOT NULL,
  category_id INT,
  price       DECIMAL(12, 2)  NOT NULL DEFAULT 0.00,
  cost        DECIMAL(12, 2)           DEFAULT 0.00,
  stock_qty   INT             NOT NULL DEFAULT 0,
  unit        VARCHAR(20)     NOT NULL DEFAULT 'un',
  description TEXT,
  status      VARCHAR(20)     NOT NULL DEFAULT 'active',
  created_at  DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at  DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_products_sku (sku),
  INDEX ix_products_name (name),
  INDEX ix_products_sku (sku),
  INDEX ix_products_status (status),
  CONSTRAINT fk_product_category FOREIGN KEY (category_id) REFERENCES categories(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Clientes ──────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS customers (
  id          INT          NOT NULL AUTO_INCREMENT,
  name        VARCHAR(255) NOT NULL,
  email       VARCHAR(255),
  phone       VARCHAR(50),
  document    VARCHAR(50),
  address     VARCHAR(512),
  city        VARCHAR(100),
  state       CHAR(2),
  zip_code    VARCHAR(20),
  status      VARCHAR(20)  NOT NULL DEFAULT 'active',
  created_at  DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at  DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  INDEX ix_customers_name (name),
  INDEX ix_customers_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Fornecedores ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS suppliers (
  id           INT          NOT NULL AUTO_INCREMENT,
  company_name VARCHAR(255) NOT NULL,
  trade_name   VARCHAR(255),
  cnpj         VARCHAR(20),
  email        VARCHAR(255),
  phone        VARCHAR(50),
  contact      VARCHAR(255),
  address      VARCHAR(512),
  category     VARCHAR(100),
  status       VARCHAR(20)  NOT NULL DEFAULT 'active',
  created_at   DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at   DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  INDEX ix_suppliers_company_name (company_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Vendas ────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sales (
  id             INT             NOT NULL AUTO_INCREMENT,
  customer_id    INT,
  user_id        INT,
  sale_date      DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  total          DECIMAL(12, 2)  NOT NULL DEFAULT 0.00,
  discount       DECIMAL(12, 2)           DEFAULT 0.00,
  payment_method VARCHAR(50),
  status         VARCHAR(30)     NOT NULL DEFAULT 'completed',
  notes          TEXT,
  created_at     DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  INDEX ix_sales_customer (customer_id),
  INDEX ix_sales_date (sale_date),
  CONSTRAINT fk_sale_customer FOREIGN KEY (customer_id) REFERENCES customers(id),
  CONSTRAINT fk_sale_user     FOREIGN KEY (user_id)     REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Itens de Venda ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sale_items (
  id          INT             NOT NULL AUTO_INCREMENT,
  sale_id     INT             NOT NULL,
  product_id  INT             NOT NULL,
  quantity    DECIMAL(10, 3)  NOT NULL DEFAULT 1.000,
  unit_price  DECIMAL(12, 2)  NOT NULL,
  subtotal    DECIMAL(12, 2)  NOT NULL,
  PRIMARY KEY (id),
  INDEX ix_sale_items_sale (sale_id),
  CONSTRAINT fk_sale_item_sale    FOREIGN KEY (sale_id)    REFERENCES sales(id)    ON DELETE CASCADE,
  CONSTRAINT fk_sale_item_product FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Pedidos ───────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS orders (
  id            INT             NOT NULL AUTO_INCREMENT,
  supplier_id   INT,
  user_id       INT,
  order_date    DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  expected_date DATETIME(6),
  total         DECIMAL(12, 2)  NOT NULL DEFAULT 0.00,
  status        VARCHAR(30)     NOT NULL DEFAULT 'pending',
  notes         TEXT,
  created_at    DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  INDEX ix_orders_supplier (supplier_id),
  CONSTRAINT fk_order_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
  CONSTRAINT fk_order_user     FOREIGN KEY (user_id)     REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Itens de Pedido ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS order_items (
  id          INT             NOT NULL AUTO_INCREMENT,
  order_id    INT             NOT NULL,
  product_id  INT             NOT NULL,
  quantity    DECIMAL(10, 3)  NOT NULL DEFAULT 1.000,
  unit_price  DECIMAL(12, 2)  NOT NULL,
  subtotal    DECIMAL(12, 2)  NOT NULL,
  PRIMARY KEY (id),
  INDEX ix_order_items_order (order_id),
  CONSTRAINT fk_order_item_order   FOREIGN KEY (order_id)   REFERENCES orders(id)   ON DELETE CASCADE,
  CONSTRAINT fk_order_item_product FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Movimentações de Estoque ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS stock_movements (
  id             INT             NOT NULL AUTO_INCREMENT,
  product_id     INT             NOT NULL,
  user_id        INT,
  type           VARCHAR(10)     NOT NULL,
  quantity       DECIMAL(10, 3)  NOT NULL,
  reference_id   INT,
  reference_type VARCHAR(30),
  notes          TEXT,
  created_at     DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  INDEX ix_stock_product (product_id),
  INDEX ix_stock_created_at (created_at),
  CONSTRAINT fk_stock_product FOREIGN KEY (product_id) REFERENCES products(id),
  CONSTRAINT fk_stock_user    FOREIGN KEY (user_id)    REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Contas a Pagar ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS accounts_payable (
  id          INT             NOT NULL AUTO_INCREMENT,
  description VARCHAR(512)    NOT NULL,
  supplier_id INT,
  amount      DECIMAL(12, 2)  NOT NULL,
  due_date    DATETIME(6)     NOT NULL,
  paid_at     DATETIME(6),
  status      VARCHAR(20)     NOT NULL DEFAULT 'pending',
  notes       TEXT,
  created_at  DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  INDEX ix_payable_due_date (due_date),
  INDEX ix_payable_status (status),
  CONSTRAINT fk_payable_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Contas a Receber ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS accounts_receivable (
  id          INT             NOT NULL AUTO_INCREMENT,
  description VARCHAR(512)    NOT NULL,
  customer_id INT,
  sale_id     INT,
  amount      DECIMAL(12, 2)  NOT NULL,
  due_date    DATETIME(6)     NOT NULL,
  paid_at     DATETIME(6),
  status      VARCHAR(20)     NOT NULL DEFAULT 'pending',
  notes       TEXT,
  created_at  DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  INDEX ix_receivable_due_date (due_date),
  INDEX ix_receivable_status (status),
  CONSTRAINT fk_receivable_customer FOREIGN KEY (customer_id) REFERENCES customers(id),
  CONSTRAINT fk_receivable_sale     FOREIGN KEY (sale_id)     REFERENCES sales(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Auditoria ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS audit_logs (
  id          INT          NOT NULL AUTO_INCREMENT,
  user_id     INT,
  action      VARCHAR(30)  NOT NULL,
  entity      VARCHAR(100) NOT NULL,
  entity_id   INT,
  description TEXT,
  details     TEXT,
  ip_address  VARCHAR(50),
  created_at  DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  INDEX ix_audit_entity (entity),
  INDEX ix_audit_created_at (created_at),
  CONSTRAINT fk_audit_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Usuário admin padrão (senha: Admin@123) ───────────────────────────────────
-- ATENÇÃO: Troque a senha imediatamente após a instalação!
INSERT IGNORE INTO users (name, email, password_hash, role, is_active)
VALUES (
  'Administrador',
  'admin@gestaopro.local',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewYpfaAzRCi1aHXi',
  'admin',
  1
);

-- ── Categorias de exemplo ─────────────────────────────────────────────────────
INSERT IGNORE INTO categories (name, description) VALUES
  ('Eletrônicos', 'Produtos eletrônicos e tecnologia'),
  ('Informática', 'Computadores, notebooks e periféricos'),
  ('Celulares', 'Smartphones e acessórios'),
  ('Eletrodomésticos', 'Eletrodomésticos em geral');

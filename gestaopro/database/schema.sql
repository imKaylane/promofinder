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
  id           INT             NOT NULL AUTO_INCREMENT,
  name         VARCHAR(512)    NOT NULL,
  sku          VARCHAR(100)    NOT NULL,
  category_id  INT,
  price        DECIMAL(12, 2)  NOT NULL DEFAULT 0.00,
  cost         DECIMAL(12, 2)           DEFAULT 0.00,
  stock_qty    INT             NOT NULL DEFAULT 0,
  unit         VARCHAR(20)     NOT NULL DEFAULT 'un',
  description  TEXT,
  release_date DATE,
  status       VARCHAR(20)     NOT NULL DEFAULT 'active',
  created_at   DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at   DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_products_sku (sku),
  INDEX ix_products_name (name),
  INDEX ix_products_sku (sku),
  INDEX ix_products_status (status),
  CONSTRAINT fk_product_category FOREIGN KEY (category_id) REFERENCES categories(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Clientes ──────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS customers (
  id           INT             NOT NULL AUTO_INCREMENT,
  name         VARCHAR(255)    NOT NULL,
  person_type  CHAR(2)         NOT NULL DEFAULT 'PF',
  email        VARCHAR(255),
  phone        VARCHAR(50),
  document     VARCHAR(50),
  birth_date   DATE,
  credit_limit DECIMAL(12,2)            DEFAULT 0.00,
  address      VARCHAR(512),
  city         VARCHAR(100),
  state        CHAR(2),
  zip_code     VARCHAR(20),
  status       VARCHAR(20)     NOT NULL DEFAULT 'active',
  created_at   DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at   DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  INDEX ix_customers_name (name),
  INDEX ix_customers_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Fornecedores ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS suppliers (
  id            INT          NOT NULL AUTO_INCREMENT,
  company_name  VARCHAR(255) NOT NULL,
  trade_name    VARCHAR(255),
  cnpj          VARCHAR(20),
  email         VARCHAR(255),
  phone         VARCHAR(50),
  contact       VARCHAR(255),
  address       VARCHAR(512),
  city          VARCHAR(100),
  state         CHAR(2),
  zip_code      VARCHAR(20),
  category      VARCHAR(100),
  contract_date DATE,
  status        VARCHAR(20)  NOT NULL DEFAULT 'active',
  created_at    DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at    DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
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
  ('Eletrodomésticos', 'Eletrodomésticos em geral'),
  ('Escritório', 'Material de escritório e papelaria'),
  ('Ferramentas', 'Ferramentas e equipamentos');

-- ── Produtos de exemplo ────────────────────────────────────────────────────────
INSERT IGNORE INTO products (name, sku, category_id, price, cost, stock_qty, unit, description, release_date, status) VALUES
  ('Notebook ProBook 450 G9',        'NB-001', 2, 3499.90, 2800.00, 15, 'un', 'Notebook corporativo Intel i5 8GB 256GB SSD', '2023-01-15', 'active'),
  ('Monitor UltraWide 34"',          'MN-001', 2, 1899.00, 1400.00, 8,  'un', 'Monitor ultrawide 34 polegadas IPS 144Hz',   '2023-03-01', 'active'),
  ('Teclado Mecânico TKL',           'TC-001', 1, 349.90,  220.00,  30, 'un', 'Teclado mecânico tenkeyless switches blue',  '2022-11-10', 'active'),
  ('Mouse Gamer 12000DPI',           'MS-001', 1, 189.90,  120.00,  45, 'un', 'Mouse óptico 12000DPI RGB ajustável',        '2022-09-20', 'active'),
  ('Smartphone Galaxy A54',          'SP-001', 3, 1599.00, 1200.00, 20, 'un', 'Smartphone 128GB 8GB RAM câmera tripla',     '2023-04-05', 'active'),
  ('Roteador Wi-Fi 6 AX1800',        'RT-001', 1, 299.90,  180.00,  12, 'un', 'Roteador dual band Wi-Fi 6 1800Mbps',       '2022-06-15', 'active'),
  ('SSD 1TB NVMe PCIe 4.0',          'SD-001', 2, 449.90,  320.00,  25, 'un', 'SSD NVMe PCIe 4.0 leitura 7000MB/s',       '2023-02-01', 'active'),
  ('Impressora Multifuncional A4',   'IP-001', 4, 799.00,  560.00,  6,  'un', 'Impressora laser mono frente e verso',      '2022-12-01', 'active'),
  ('Webcam Full HD 1080p',           'WC-001', 1, 159.90,  100.00,  18, 'un', 'Webcam Full HD microfone integrado',        '2023-01-20', 'active'),
  ('Headset USB Stereo',             'HS-001', 1, 119.90,  75.00,   22, 'un', 'Headset USB drivers 40mm cancelamento',     '2023-01-05', 'active');

-- ── Clientes de exemplo ───────────────────────────────────────────────────────
INSERT IGNORE INTO customers (name, person_type, email, phone, document, credit_limit, city, state, zip_code, status) VALUES
  ('Ana Carolina Silva',    'PF', 'ana.silva@email.com',   '(11) 99887-6655', '123.456.789-09', 5000.00, 'São Paulo',      'SP', '01310-100', 'active'),
  ('Bruno Ferreira Santos', 'PF', 'bruno.f@email.com',     '(21) 98765-4321', '987.654.321-00', 3000.00, 'Rio de Janeiro', 'RJ', '20040-020', 'active'),
  ('Tech Solutions Ltda',   'PJ', 'contato@techsol.com',   '(11) 3344-5566',  '12.345.678/0001-95', 20000.00, 'São Paulo', 'SP', '04578-000', 'active'),
  ('Carlos Eduardo Alves',  'PF', 'carlos.alves@mail.com', '(31) 97654-3210', '456.789.123-87', 2000.00, 'Belo Horizonte', 'MG', '30130-100', 'active'),
  ('Distribuidora Omega',   'PJ', 'vendas@omega.com',      '(41) 3222-1100',  '98.765.432/0001-10', 15000.00, 'Curitiba', 'PR', '80010-020', 'active');

-- ── Fornecedores de exemplo ───────────────────────────────────────────────────
INSERT IGNORE INTO suppliers (company_name, trade_name, cnpj, email, phone, contact, city, state, category, contract_date, status) VALUES
  ('Distribuidora TechImport Ltda', 'TechImport',   '11.222.333/0001-44', 'compras@techimport.com.br', '(11) 3456-7890', 'Roberto Lima',    'São Paulo',      'SP', 'Informática',      '2022-01-10', 'active'),
  ('Eletrônicos do Brasil S.A.',    'EletrosBR',     '44.555.666/0001-77', 'pedidos@eletrosbr.com',    '(21) 2233-4455', 'Sandra Oliveira', 'Rio de Janeiro', 'RJ', 'Eletrônicos',      '2021-06-15', 'active'),
  ('Papelaria Central Ltda',        'PapelCentral',  '77.888.999/0001-11', 'contato@papelcentral.com', '(31) 3311-2200', 'Marcos Souza',    'Belo Horizonte', 'MG', 'Escritório',       '2023-03-01', 'active'),
  ('Ferramentas Sul Ltda',          'FerraSul',      '22.333.444/0001-55', 'vendas@ferrasul.com.br',   '(51) 3344-5500', 'Patrícia Mendes', 'Porto Alegre',   'RS', 'Ferramentas',      '2022-09-20', 'active'),
  ('Global Tech Importação Ltda',   'GlobalTech',    '55.666.777/0001-88', 'gtech@globaltech.com',     '(11) 4455-6677', 'José Fernandes',  'São Paulo',      'SP', 'Eletrodomésticos', '2020-11-05', 'active');

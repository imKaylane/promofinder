-- =========================================================
-- GestãoPro — Migration 001: Novos campos (EX3)
-- Adiciona campos de data e campos extras às entidades
-- Executar: mysql -u root -p gestaopro < migrations/001_new_fields.sql
-- =========================================================

USE gestaopro;

-- ── Clientes ──────────────────────────────────────────────
ALTER TABLE customers
  ADD COLUMN IF NOT EXISTS person_type   CHAR(2)         NOT NULL DEFAULT 'PF'  AFTER name,
  ADD COLUMN IF NOT EXISTS birth_date    DATETIME(6)                             AFTER document,
  ADD COLUMN IF NOT EXISTS credit_limit  DECIMAL(12,2)   NOT NULL DEFAULT 0.00  AFTER birth_date;

-- ── Produtos ──────────────────────────────────────────────
ALTER TABLE products
  ADD COLUMN IF NOT EXISTS release_date  DATETIME(6)     AFTER description;

-- ── Fornecedores ──────────────────────────────────────────
ALTER TABLE suppliers
  ADD COLUMN IF NOT EXISTS contract_date DATETIME(6)     AFTER category;

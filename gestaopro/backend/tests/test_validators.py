"""GestãoPro — Testes dos validadores de domínio (EX3)"""
import pytest
from app.services.validators import (
    validate_email, validate_cpf, validate_cnpj, validate_cep,
    validate_phone_br, validate_uf, validate_date_iso,
    validate_positive_decimal, validate_document,
)


# ── Email ─────────────────────────────────────────────────────────────────────
class TestEmail:
    def test_valid(self):
        assert validate_email("user@example.com")
        assert validate_email("a+b@x.co.uk")

    def test_invalid(self):
        assert not validate_email("not-an-email")
        assert not validate_email("@missing.com")
        assert not validate_email("missing@")
        assert not validate_email("")


# ── CPF ───────────────────────────────────────────────────────────────────────
class TestCPF:
    def test_valid(self):
        assert validate_cpf("529.982.247-25")
        assert validate_cpf("52998224725")

    def test_invalid_digit(self):
        assert not validate_cpf("529.982.247-26")  # dígito errado

    def test_invalid_all_same(self):
        assert not validate_cpf("111.111.111-11")
        assert not validate_cpf("00000000000")

    def test_invalid_length(self):
        assert not validate_cpf("123.456.789")
        assert not validate_cpf("")


# ── CNPJ ──────────────────────────────────────────────────────────────────────
class TestCNPJ:
    def test_valid(self):
        assert validate_cnpj("11.222.333/0001-81")
        assert validate_cnpj("11222333000181")

    def test_invalid_digit(self):
        assert not validate_cnpj("11.222.333/0001-82")

    def test_invalid_all_same(self):
        assert not validate_cnpj("00.000.000/0000-00")

    def test_invalid_length(self):
        assert not validate_cnpj("123.456")
        assert not validate_cnpj("")


# ── CEP ───────────────────────────────────────────────────────────────────────
class TestCEP:
    def test_valid(self):
        assert validate_cep("01001-000")
        assert validate_cep("01001000")

    def test_invalid(self):
        assert not validate_cep("1234-567")
        assert not validate_cep("abc")
        assert not validate_cep("")


# ── Telefone ──────────────────────────────────────────────────────────────────
class TestPhone:
    def test_valid(self):
        assert validate_phone_br("(11) 99999-9999")
        assert validate_phone_br("11999999999")
        assert validate_phone_br("(11) 3333-4444")

    def test_invalid(self):
        assert not validate_phone_br("123")
        assert not validate_phone_br("")


# ── UF ────────────────────────────────────────────────────────────────────────
class TestUF:
    def test_valid(self):
        assert validate_uf("SP")
        assert validate_uf("sp")  # case-insensitive
        assert validate_uf("RJ")

    def test_invalid(self):
        assert not validate_uf("XX")
        assert not validate_uf("")


# ── Data ISO ──────────────────────────────────────────────────────────────────
class TestDate:
    def test_valid(self):
        assert validate_date_iso("2024-01-15")
        assert validate_date_iso("")   # opcional

    def test_invalid(self):
        assert not validate_date_iso("15/01/2024")
        assert not validate_date_iso("not-a-date")


# ── Decimal positivo ──────────────────────────────────────────────────────────
class TestDecimal:
    def test_valid(self):
        assert validate_positive_decimal(0)
        assert validate_positive_decimal(10.5)
        assert validate_positive_decimal("99.99")

    def test_invalid(self):
        assert not validate_positive_decimal(-1)
        assert not validate_positive_decimal("abc")


# ── Documento composto ────────────────────────────────────────────────────────
class TestDocument:
    def test_pf_cpf(self):
        assert validate_document("529.982.247-25", "PF")
        assert not validate_document("529.982.247-26", "PF")

    def test_pj_cnpj(self):
        assert validate_document("11.222.333/0001-81", "PJ")
        assert not validate_document("11.222.333/0001-82", "PJ")

"""
GestãoPro — Validadores de domínio (EX3)
Validação de CPF, CNPJ, CEP, telefone, UF, e-mail, data e número positivo.
Devolve erros no formato {field, code, message}.
"""
import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation


# ── E-mail ────────────────────────────────────────────────────────────────────
_EMAIL_RE = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')

def validate_email(value: str) -> bool:
    return bool(_EMAIL_RE.match((value or "").strip()))


# ── CPF ───────────────────────────────────────────────────────────────────────
def validate_cpf(cpf: str) -> bool:
    digits = re.sub(r'\D', '', cpf or '')
    if len(digits) != 11 or len(set(digits)) == 1:
        return False
    for i in range(9, 11):
        total = sum(int(digits[j]) * (i + 1 - j) for j in range(i))
        expected = (total * 10 % 11) % 10
        if expected != int(digits[i]):
            return False
    return True


# ── CNPJ ──────────────────────────────────────────────────────────────────────
def validate_cnpj(cnpj: str) -> bool:
    digits = re.sub(r'\D', '', cnpj or '')
    if len(digits) != 14 or len(set(digits)) == 1:
        return False
    weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    for w, pos in [(weights1, 12), (weights2, 13)]:
        total = sum(int(digits[i]) * w[i] for i in range(len(w)))
        remainder = total % 11
        expected = 0 if remainder < 2 else 11 - remainder
        if expected != int(digits[pos]):
            return False
    return True


# ── CEP ───────────────────────────────────────────────────────────────────────
_CEP_RE = re.compile(r'^\d{5}-?\d{3}$')

def validate_cep(cep: str) -> bool:
    return bool(_CEP_RE.match((cep or "").strip()))


# ── Telefone (Brasil) ─────────────────────────────────────────────────────────
_PHONE_RE = re.compile(r'^\(?\d{2}\)?\s?[\d\s\-]{8,10}$')

def validate_phone_br(phone: str) -> bool:
    digits = re.sub(r'\D', '', phone or '')
    return len(digits) in (10, 11)


# ── UF (estados brasileiros) ──────────────────────────────────────────────────
_UFS = {'AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS',
        'MG','PA','PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC',
        'SP','SE','TO'}

def validate_uf(uf: str) -> bool:
    return (uf or "").upper() in _UFS


# ── Data ISO (YYYY-MM-DD) ─────────────────────────────────────────────────────
def validate_date_iso(value: str) -> bool:
    if not value:
        return True  # datas são opcionais por padrão
    try:
        datetime.strptime(value.strip(), '%Y-%m-%d')
        return True
    except ValueError:
        return False


# ── Número decimal positivo ───────────────────────────────────────────────────
def validate_positive_decimal(value) -> bool:
    try:
        d = Decimal(str(value))
        return d >= 0
    except (InvalidOperation, TypeError):
        return False


# ── Helpers compostos ─────────────────────────────────────────────────────────
def validate_document(document: str, person_type: str = "PF") -> bool:
    """Valida CPF se PF, CNPJ se PJ."""
    if person_type == "PJ":
        return validate_cnpj(document)
    return validate_cpf(document)


def build_error(field: str, code: str, message: str) -> dict:
    return {"field": field, "code": code, "message": message}

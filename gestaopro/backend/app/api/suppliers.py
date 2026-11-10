"""
GestãoPro — Blueprint de Fornecedores (EX3 + EX4)
CRUD completo: GET(list), GET(detail), POST, PUT, PATCH, DELETE
Validação: CNPJ, telefone, CEP, UF, e-mail, data
Paginação + busca + filtro por status
"""
import logging
import math
from flask import Blueprint, request, jsonify, g
from sqlalchemy import select, func, or_

logger = logging.getLogger(__name__)

import app.models.database as _db
def get_db(): return _db.get_db()
from app.models.models import Supplier, AuditLog
from app.middleware.auth import require_auth
from app.services.validators import (
    validate_email, validate_phone_br, validate_cep, validate_uf,
    validate_cnpj, validate_date_iso, build_error,
)

suppliers_bp = Blueprint("suppliers", __name__, url_prefix="/api/v1/suppliers")


# ── GET /api/v1/suppliers  (listagem + busca + paginação) ─────────────────────
@suppliers_bp.get("")
@require_auth
def list_suppliers():
    page = max(1, int(request.args.get("page", 1)))
    limit = min(50, max(1, int(request.args.get("limit", 20))))
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()

    db = next(get_db())
    try:
        q = select(Supplier)
        count_q = select(func.count()).select_from(Supplier)

        if search:
            like = f"%{search}%"
            flt = (
                Supplier.company_name.ilike(like) |
                Supplier.trade_name.ilike(like) |
                Supplier.cnpj.ilike(like) |
                Supplier.email.ilike(like)
            )
            q = q.where(flt)
            count_q = count_q.where(flt)

        if status:
            q = q.where(Supplier.status == status)
            count_q = count_q.where(Supplier.status == status)

        total = db.scalar(count_q) or 0
        items = db.scalars(
            q.order_by(Supplier.company_name)
             .offset((page - 1) * limit)
             .limit(limit)
        ).all()
        pages = math.ceil(total / limit) if total else 0

        return jsonify({
            "items": [_out(s) for s in items],
            "total": total, "page": page, "limit": limit, "pages": pages,
        })
    finally:
        db.close()


# ── GET /api/v1/suppliers/<id> ────────────────────────────────────────────────
@suppliers_bp.get("/<int:supplier_id>")
@require_auth
def get_supplier(supplier_id: int):
    db = next(get_db())
    try:
        s = db.get(Supplier, supplier_id)
        if not s:
            return jsonify({"detail": "Supplier not found"}), 404
        return jsonify(_out(s))
    finally:
        db.close()


# ── POST /api/v1/suppliers ────────────────────────────────────────────────────
@suppliers_bp.post("")
@require_auth
def create_supplier():
    data = request.get_json(silent=True) or {}
    errors = _validate(data)
    if errors:
        return jsonify({"detail": "Validation error", "errors": errors}), 400

    db = next(get_db())
    try:
        s = Supplier(**_clean(data))
        db.add(s)
        db.flush()
        _audit(db, g.user_id, "CREATE", s.id, f"Supplier '{s.company_name}' created")
        db.commit()
        return jsonify(_out(s)), 201
    except Exception:
        db.rollback()
        logger.exception("Error creating supplier")
        return jsonify({"detail": "Internal server error"}), 500
    finally:
        db.close()


# ── PUT /api/v1/suppliers/<id> ────────────────────────────────────────────────
@suppliers_bp.put("/<int:supplier_id>")
@require_auth
def update_supplier(supplier_id: int):
    data = request.get_json(silent=True) or {}
    errors = _validate(data, is_update=False)
    if errors:
        return jsonify({"detail": "Validation error", "errors": errors}), 400

    db = next(get_db())
    try:
        s = db.get(Supplier, supplier_id)
        if not s:
            return jsonify({"detail": "Supplier not found"}), 404
        for k, v in _clean(data).items():
            setattr(s, k, v)
        _audit(db, g.user_id, "UPDATE", supplier_id, f"Supplier '{s.company_name}' updated")
        db.commit()
        return jsonify(_out(s))
    except Exception:
        db.rollback()
        logger.exception("Error updating supplier %d", supplier_id)
        return jsonify({"detail": "Internal server error"}), 500
    finally:
        db.close()


# ── PATCH /api/v1/suppliers/<id> ──────────────────────────────────────────────
@suppliers_bp.patch("/<int:supplier_id>")
@require_auth
def patch_supplier(supplier_id: int):
    data = request.get_json(silent=True) or {}
    errors = _validate(data, is_update=True)
    if errors:
        return jsonify({"detail": "Validation error", "errors": errors}), 400

    db = next(get_db())
    try:
        s = db.get(Supplier, supplier_id)
        if not s:
            return jsonify({"detail": "Supplier not found"}), 404
        for k, v in _clean(data).items():
            setattr(s, k, v)
        _audit(db, g.user_id, "UPDATE", supplier_id, f"Supplier '{s.company_name}' patched")
        db.commit()
        return jsonify(_out(s))
    except Exception:
        db.rollback()
        logger.exception("Error patching supplier %d", supplier_id)
        return jsonify({"detail": "Internal server error"}), 500
    finally:
        db.close()


# ── DELETE /api/v1/suppliers/<id> ─────────────────────────────────────────────
@suppliers_bp.delete("/<int:supplier_id>")
@require_auth
def delete_supplier(supplier_id: int):
    db = next(get_db())
    try:
        s = db.get(Supplier, supplier_id)
        if not s:
            return jsonify({"detail": "Supplier not found"}), 404
        name = s.company_name
        db.delete(s)
        _audit(db, g.user_id, "DELETE", supplier_id, f"Supplier '{name}' deleted")
        db.commit()
        return "", 204
    except Exception:
        db.rollback()
        logger.exception("Error deleting supplier %d", supplier_id)
        return jsonify({"detail": "Internal server error"}), 500
    finally:
        db.close()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _validate(data: dict, is_update: bool = False) -> list:
    errors = []
    if not is_update and not (data.get("company_name") or "").strip():
        errors.append(build_error("company_name", "VALIDATION_REQUIRED", "Company name is required"))
    if data.get("cnpj") and not validate_cnpj(data["cnpj"]):
        errors.append(build_error("cnpj", "VALIDATION_CNPJ", "Invalid CNPJ"))
    if data.get("email") and not validate_email(data["email"]):
        errors.append(build_error("email", "VALIDATION_EMAIL", "Invalid email"))
    if data.get("phone") and not validate_phone_br(data["phone"]):
        errors.append(build_error("phone", "VALIDATION_PHONE", "Invalid phone"))
    if data.get("zip_code") and not validate_cep(data["zip_code"]):
        errors.append(build_error("zip_code", "VALIDATION_CEP", "Invalid ZIP code"))
    if data.get("state") and not validate_uf(data["state"]):
        errors.append(build_error("state", "VALIDATION_UF", "Invalid UF"))
    if data.get("contract_date") and not validate_date_iso(data["contract_date"]):
        errors.append(build_error("contract_date", "VALIDATION_DATE", "Invalid date"))
    return errors


def _clean(data: dict) -> dict:
    allowed = {
        "company_name", "trade_name", "cnpj", "email", "phone",
        "contact", "address", "city", "state", "zip_code",
        "category", "contract_date", "status",
    }
    return {k: v for k, v in data.items() if k in allowed}


def _out(s) -> dict:
    return {
        "id": s.id,
        "company_name": s.company_name,
        "trade_name": s.trade_name,
        "cnpj": s.cnpj,
        "email": s.email,
        "phone": s.phone,
        "contact": s.contact,
        "address": s.address,
        "city": getattr(s, "city", None),
        "state": getattr(s, "state", None),
        "zip_code": getattr(s, "zip_code", None),
        "category": s.category,
        "contract_date": (
            s.contract_date.strftime("%Y-%m-%d")
            if getattr(s, "contract_date", None) else None
        ),
        "status": s.status,
        "created_at": s.created_at.isoformat() if s.created_at else None,
        "updated_at": s.updated_at.isoformat() if s.updated_at else None,
    }


def _audit(db, user_id, action, entity_id, description):
    log = AuditLog(
        user_id=user_id, action=action, entity="suppliers",
        entity_id=entity_id, description=description,
        ip_address=request.remote_addr,
    )
    db.add(log)

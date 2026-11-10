"""
GestãoPro — Blueprint de Clientes (EX3 + EX4)
CRUD completo — segunda entidade do exercício
"""
import logging
from flask import Blueprint, request, jsonify, g

logger = logging.getLogger(__name__)

import app.models.database as _db
def get_db(): return _db.get_db()
from app.repositories.customer_repository import CustomerRepository
from app.middleware.auth import require_auth
from app.models.models import AuditLog
from app.services.validators import (
    validate_email, validate_phone_br, validate_cep, validate_uf,
    validate_document, validate_date_iso, validate_positive_decimal,
    build_error,
)

customers_bp = Blueprint("customers", __name__, url_prefix="/api/v1/customers")


@customers_bp.get("")
@require_auth
def list_customers():
    page = max(1, int(request.args.get("page", 1)))
    limit = min(50, max(1, int(request.args.get("limit", 20))))
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()

    db = next(get_db())
    try:
        repo = CustomerRepository(db)
        items, total, pages = repo.list(page=page, limit=limit, search=search, status=status)
        return jsonify({
            "items": [_out(c) for c in items],
            "total": total, "page": page, "limit": limit, "pages": pages,
        })
    finally:
        db.close()


@customers_bp.get("/<int:customer_id>")
@require_auth
def get_customer(customer_id: int):
    db = next(get_db())
    try:
        repo = CustomerRepository(db)
        c = repo.get_by_id(customer_id)
        if not c:
            return jsonify({"detail": "Customer not found"}), 404
        return jsonify(_out(c))
    finally:
        db.close()


@customers_bp.post("")
@require_auth
def create_customer():
    data = request.get_json(silent=True) or {}
    errors = _validate(data)
    if errors:
        return jsonify({"detail": "Validation error", "errors": errors}), 400

    db = next(get_db())
    try:
        repo = CustomerRepository(db)
        c = repo.create(_clean(data))
        db.commit()
        _audit(db, g.user_id, "CREATE", "customers", c.id, f"Customer '{c.name}' created")
        db.commit()
        return jsonify(_out(c)), 201
    except Exception:
        db.rollback()
        logger.exception("Error creating customer")
        return jsonify({"detail": "Internal server error"}), 500
    finally:
        db.close()


@customers_bp.put("/<int:customer_id>")
@require_auth
def update_customer(customer_id: int):
    data = request.get_json(silent=True) or {}
    errors = _validate(data, is_update=True)
    if errors:
        return jsonify({"detail": "Validation error", "errors": errors}), 400

    db = next(get_db())
    try:
        repo = CustomerRepository(db)
        c = repo.get_by_id(customer_id)
        if not c:
            return jsonify({"detail": "Customer not found"}), 404
        updated = repo.update(c, _clean(data))
        db.commit()
        _audit(db, g.user_id, "UPDATE", "customers", customer_id, f"Customer '{updated.name}' updated")
        db.commit()
        return jsonify(_out(updated))
    except Exception:
        db.rollback()
        logger.exception("Error updating customer %d", customer_id)
        return jsonify({"detail": "Internal server error"}), 500
    finally:
        db.close()


@customers_bp.delete("/<int:customer_id>")
@require_auth
def delete_customer(customer_id: int):
    db = next(get_db())
    try:
        repo = CustomerRepository(db)
        c = repo.get_by_id(customer_id)
        if not c:
            return jsonify({"detail": "Customer not found"}), 404
        name = c.name
        repo.delete(c)
        db.commit()
        _audit(db, g.user_id, "DELETE", "customers", customer_id, f"Customer '{name}' deleted")
        db.commit()
        return "", 204
    except Exception:
        db.rollback()
        logger.exception("Error deleting customer %d", customer_id)
        return jsonify({"detail": "Internal server error"}), 500
    finally:
        db.close()


# ── helpers ───────────────────────────────────────────────────────────────────

def _validate(data: dict, is_update: bool = False) -> list:
    errors = []
    name = (data.get("name") or "").strip()
    if not is_update and not name:
        errors.append(build_error("name", "VALIDATION_REQUIRED", "Name is required"))
    if data.get("email") and not validate_email(data["email"]):
        errors.append(build_error("email", "VALIDATION_EMAIL", "Invalid email"))
    if data.get("phone") and not validate_phone_br(data["phone"]):
        errors.append(build_error("phone", "VALIDATION_PHONE", "Invalid phone"))
    if data.get("zip_code") and not validate_cep(data["zip_code"]):
        errors.append(build_error("zip_code", "VALIDATION_CEP", "Invalid ZIP code"))
    if data.get("state") and not validate_uf(data["state"]):
        errors.append(build_error("state", "VALIDATION_UF", "Invalid UF"))
    if data.get("document") and not validate_document(data["document"], data.get("person_type", "PF")):
        errors.append(build_error("document", "VALIDATION_DOCUMENT", "Invalid CPF/CNPJ"))
    if data.get("birth_date") and not validate_date_iso(data["birth_date"]):
        errors.append(build_error("birth_date", "VALIDATION_DATE", "Invalid date"))
    if data.get("credit_limit") is not None and not validate_positive_decimal(data["credit_limit"]):
        errors.append(build_error("credit_limit", "VALIDATION_POSITIVE", "Must be non-negative"))
    return errors


def _clean(data: dict) -> dict:
    allowed = {"name", "person_type", "email", "phone", "document",
               "birth_date", "credit_limit", "address", "city", "state", "zip_code", "status"}
    return {k: v for k, v in data.items() if k in allowed}


def _out(c) -> dict:
    return {
        "id": c.id, "name": c.name,
        "person_type": getattr(c, "person_type", "PF"),
        "email": c.email, "phone": c.phone,
        "document": c.document,
        "birth_date": c.birth_date.isoformat() if getattr(c, "birth_date", None) else None,
        "credit_limit": float(c.credit_limit) if getattr(c, "credit_limit", None) is not None else 0,
        "address": c.address, "city": c.city,
        "state": c.state, "zip_code": c.zip_code, "status": c.status,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }


def _audit(db, user_id, action, entity, entity_id, description):
    log = AuditLog(user_id=user_id, action=action, entity=entity,
                   entity_id=entity_id, description=description,
                   ip_address=request.remote_addr)
    db.add(log)

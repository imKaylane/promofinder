"""
GestãoPro — Blueprint de Clientes (EX3 + EX4)
CRUD completo — segunda entidade do exercício
"""
from flask import Blueprint, request, jsonify, g

import app.models.database as _db
def get_db(): return _db.get_db()
from app.repositories.customer_repository import CustomerRepository
from app.middleware.auth import require_auth
from app.models.models import AuditLog

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
    except Exception as e:
        db.rollback()
        return jsonify({"detail": str(e)}), 500
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
    except Exception as e:
        db.rollback()
        return jsonify({"detail": str(e)}), 500
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
    except Exception as e:
        db.rollback()
        return jsonify({"detail": str(e)}), 500
    finally:
        db.close()


# ── helpers ───────────────────────────────────────────────────────────────────

def _validate(data: dict, is_update: bool = False) -> list:
    errors = []
    if not is_update and not data.get("name", "").strip():
        errors.append({"field": "name", "msg": "Name is required"})
    return errors


def _clean(data: dict) -> dict:
    allowed = {"name", "email", "phone", "document", "address", "city", "state", "zip_code", "status"}
    return {k: v for k, v in data.items() if k in allowed}


def _out(c) -> dict:
    return {
        "id": c.id, "name": c.name, "email": c.email, "phone": c.phone,
        "document": c.document, "address": c.address, "city": c.city,
        "state": c.state, "zip_code": c.zip_code, "status": c.status,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }


def _audit(db, user_id, action, entity, entity_id, description):
    log = AuditLog(user_id=user_id, action=action, entity=entity,
                   entity_id=entity_id, description=description,
                   ip_address=request.remote_addr)
    db.add(log)

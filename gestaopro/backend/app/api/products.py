"""
GestãoPro — Blueprint de Produtos (EX3 + EX4)
CRUD completo: GET(list), GET(detail), POST, PUT, PATCH, DELETE
Autenticação: JWT Bearer token
Validação: frontend + backend
Paginação + busca + filtros
"""
import logging
from flask import Blueprint, request, jsonify, g

logger = logging.getLogger(__name__)

import app.models.database as _db
def get_db(): return _db.get_db()
from app.repositories.product_repository import ProductRepository
from app.middleware.auth import require_auth

products_bp = Blueprint("products", __name__, url_prefix="/api/v1/products")


# ── GET /api/v1/products  (listagem + busca + paginação) ──────────────────────
@products_bp.get("")
@require_auth
def list_products():
    page = max(1, int(request.args.get("page", 1)))
    limit = min(50, max(1, int(request.args.get("limit", 20))))
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()
    category_id = request.args.get("category_id", type=int)

    db = next(get_db())
    try:
        repo = ProductRepository(db)
        items, total, pages = repo.list(page=page, limit=limit, search=search,
                                        status=status, category_id=category_id)
        return jsonify({
            "items": [_product_out(p) for p in items],
            "total": total,
            "page": page,
            "limit": limit,
            "pages": pages,
        })
    finally:
        db.close()


# ── GET /api/v1/products/<id> (detalhe) ───────────────────────────────────────
@products_bp.get("/<int:product_id>")
@require_auth
def get_product(product_id: int):
    db = next(get_db())
    try:
        repo = ProductRepository(db)
        p = repo.get_by_id(product_id)
        if not p:
            return jsonify({"detail": "Product not found"}), 404
        return jsonify(_product_out(p))
    finally:
        db.close()


# ── POST /api/v1/products (criar) ─────────────────────────────────────────────
@products_bp.post("")
@require_auth
def create_product():
    data = request.get_json(silent=True) or {}
    errors = _validate_product(data)
    if errors:
        return jsonify({"detail": "Validation error", "errors": errors}), 400

    db = next(get_db())
    try:
        repo = ProductRepository(db)
        if repo.get_by_sku(data["sku"]):
            return jsonify({"detail": f"SKU '{data['sku']}' already in use"}), 409
        product = repo.create(_clean_product(data))
        db.commit()
        _log_audit(db, g.user_id, "CREATE", "products", product.id,
                   f"Product '{product.name}' created")
        db.commit()
        return jsonify(_product_out(product)), 201
    except Exception:
        db.rollback()
        logger.exception("Error creating product")
        return jsonify({"detail": "Internal server error"}), 500
    finally:
        db.close()


# ── PUT /api/v1/products/<id> (atualizar) ─────────────────────────────────────
@products_bp.put("/<int:product_id>")
@require_auth
def update_product(product_id: int):
    data = request.get_json(silent=True) or {}
    db = next(get_db())
    try:
        repo = ProductRepository(db)
        p = repo.get_by_id(product_id)
        if not p:
            return jsonify({"detail": "Product not found"}), 404

        # If SKU changed, check uniqueness
        new_sku = data.get("sku", "").strip()
        if new_sku and new_sku != p.sku:
            if repo.get_by_sku(new_sku):
                return jsonify({"detail": f"SKU '{new_sku}' already in use"}), 409

        errors = _validate_product(data, is_update=True)
        if errors:
            return jsonify({"detail": "Validation error", "errors": errors}), 400

        updated = repo.update(p, _clean_product(data))
        db.commit()
        _log_audit(db, g.user_id, "UPDATE", "products", product_id,
                   f"Product '{updated.name}' updated")
        db.commit()
        return jsonify(_product_out(updated))
    except Exception:
        db.rollback()
        logger.exception("Error updating product %d", product_id)
        return jsonify({"detail": "Internal server error"}), 500
    finally:
        db.close()


# ── DELETE /api/v1/products/<id> (excluir) ────────────────────────────────────
@products_bp.delete("/<int:product_id>")
@require_auth
def delete_product(product_id: int):
    db = next(get_db())
    try:
        repo = ProductRepository(db)
        p = repo.get_by_id(product_id)
        if not p:
            return jsonify({"detail": "Product not found"}), 404
        name = p.name
        repo.delete(p)
        db.commit()
        _log_audit(db, g.user_id, "DELETE", "products", product_id,
                   f"Product '{name}' deleted")
        db.commit()
        return "", 204
    except Exception:
        db.rollback()
        logger.exception("Error deleting product %d", product_id)
        return jsonify({"detail": "Internal server error"}), 500
    finally:
        db.close()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _validate_product(data: dict, is_update: bool = False) -> list:
    from app.services.validators import validate_positive_decimal, build_error
    errors = []
    if not is_update:
        if not data.get("name", "").strip():
            errors.append(build_error("name", "VALIDATION_REQUIRED", "Name is required"))
        if not data.get("sku", "").strip():
            errors.append(build_error("sku", "VALIDATION_REQUIRED", "SKU is required"))
    if "price" in data and not validate_positive_decimal(data["price"]):
        errors.append(build_error("price", "VALIDATION_POSITIVE", "Price must be non-negative"))
    if "cost" in data and data["cost"] is not None and not validate_positive_decimal(data["cost"]):
        errors.append(build_error("cost", "VALIDATION_POSITIVE", "Cost must be non-negative"))
    if data.get("release_date"):
        from app.services.validators import validate_date_iso
        if not validate_date_iso(data["release_date"]):
            errors.append(build_error("release_date", "VALIDATION_DATE", "Invalid date"))
    return errors


def _clean_product(data: dict) -> dict:
    allowed = {"name", "sku", "category_id", "price", "cost", "stock_qty",
               "unit", "description", "release_date", "status"}
    return {k: v for k, v in data.items() if k in allowed}


def _product_out(p) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "sku": p.sku,
        "category": p.category.name if p.category else None,
        "category_id": p.category_id,
        "price": float(p.price or 0),
        "cost": float(p.cost or 0),
        "stock_qty": int(p.stock_qty or 0),
        "unit": p.unit,
        "description": p.description,
        "release_date": p.release_date.isoformat() if getattr(p, "release_date", None) else None,
        "status": p.status,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
    }


def _log_audit(db, user_id, action, entity, entity_id, description):
    from app.models.models import AuditLog
    log = AuditLog(user_id=user_id, action=action, entity=entity,
                   entity_id=entity_id, description=description,
                   ip_address=request.remote_addr)
    db.add(log)

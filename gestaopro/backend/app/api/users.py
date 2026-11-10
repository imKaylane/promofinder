"""
GestãoPro — Blueprint de Usuários (admin)
"""
from flask import Blueprint, request, jsonify, g
from sqlalchemy import select, func, and_
import math

import app.models.database as _db
def get_db(): return _db.get_db()
from app.models.models import User
from app.middleware.auth import require_auth, require_admin
from app.repositories.user_repository import UserRepository

users_bp = Blueprint("users", __name__, url_prefix="/api/v1")


@users_bp.get("/users/me")
@require_auth
def get_me():
    return jsonify(_user_out(g.current_user))


@users_bp.get("/admin/users")
@require_admin
def list_users():
    page = max(1, int(request.args.get("page", 1)))
    limit = min(50, max(1, int(request.args.get("limit", 20))))
    search = request.args.get("search", "").strip()

    db = next(get_db())
    try:
        q = select(User)
        count_q = select(func.count()).select_from(User)
        if search:
            like = f"%{search}%"
            flt = User.name.ilike(like) | User.email.ilike(like)
            q = q.where(flt)
            count_q = count_q.where(flt)

        total = db.scalar(count_q) or 0
        items = db.scalars(q.order_by(User.name).offset((page - 1) * limit).limit(limit)).all()
        pages = math.ceil(total / limit) if total else 0
        return jsonify({
            "items": [_user_out(u) for u in items],
            "total": total, "page": page, "limit": limit, "pages": pages,
        })
    finally:
        db.close()


@users_bp.get("/audit")
@require_admin
def get_audit():
    page = max(1, int(request.args.get("page", 1)))
    limit = min(100, max(1, int(request.args.get("limit", 20))))
    from app.models.models import AuditLog
    from sqlalchemy import desc
    db = next(get_db())
    try:
        q = select(AuditLog).order_by(desc(AuditLog.created_at))
        total = db.scalar(select(func.count()).select_from(AuditLog)) or 0
        items = db.scalars(q.offset((page - 1) * limit).limit(limit)).all()
        pages = math.ceil(total / limit) if total else 0
        return jsonify({
            "items": [_audit_out(l) for l in items],
            "total": total, "page": page, "limit": limit, "pages": pages,
        })
    finally:
        db.close()


def _user_out(u) -> dict:
    return {
        "id": u.id, "name": u.name, "email": u.email,
        "role": u.role, "is_active": u.is_active,
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def _audit_out(l) -> dict:
    return {
        "id": l.id,
        "user_id": l.user_id,
        "user_name": l.user.name if l.user else None,
        "action": l.action,
        "entity": l.entity,
        "entity_id": l.entity_id,
        "description": l.description,
        "ip_address": l.ip_address,
        "created_at": l.created_at.isoformat() if l.created_at else None,
    }

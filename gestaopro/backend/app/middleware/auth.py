"""
GestãoPro — Middleware de autenticação
Portado de: backend/app/api/deps.py (TechDeals AI)
"""
from functools import wraps
from flask import request, g, jsonify
from app.services.security import decode_token
from app.repositories.user_repository import UserRepository
import app.models.database as _db
def get_db(): return _db.get_db()


def _get_token() -> str | None:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:]
    return None


def require_auth(f):
    """Decorator: require valid JWT access token."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = _get_token()
        if not token:
            return jsonify({"detail": "Missing token"}), 401

        payload = decode_token(token)
        if payload is None or payload.get("type") != "access":
            return jsonify({"detail": "Invalid or expired token"}), 401

        user_id = payload.get("sub")
        if not user_id:
            return jsonify({"detail": "Invalid token payload"}), 401

        db = next(get_db())
        try:
            repo = UserRepository(db)
            user = repo.get_by_id(int(user_id))
            if user is None or not user.is_active:
                return jsonify({"detail": "User not found or inactive"}), 401
        finally:
            db.close()

        g.current_user = user
        g.user_id = user.id
        return f(*args, **kwargs)
    return wrapper


def require_admin(f):
    """Decorator: require admin role."""
    @wraps(f)
    @require_auth
    def wrapper(*args, **kwargs):
        if g.current_user.role != "admin":
            return jsonify({"detail": "Admin access required"}), 403
        return f(*args, **kwargs)
    return wrapper

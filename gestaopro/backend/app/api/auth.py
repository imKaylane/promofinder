"""
GestãoPro — Blueprint de autenticação
Portado de: backend/app/api/v1/auth.py (TechDeals AI)
"""
from datetime import datetime, timedelta, timezone

from flask import Blueprint, request, jsonify

import app.models.database as _db
def get_db(): return _db.get_db()
from app.repositories.user_repository import UserRepository
from app.services.security import (
    create_access_token, create_refresh_token,
    verify_password, get_password_hash, decode_token,
)
from app.config import config
from app.middleware.auth import require_auth
from flask import g

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name or len(name) < 2:
        return jsonify({"detail": "Name must be at least 2 characters"}), 400
    if not email or "@" not in email:
        return jsonify({"detail": "Invalid email"}), 400
    if len(password) < 8:
        return jsonify({"detail": "Password must be at least 8 characters"}), 400

    db = next(get_db())
    try:
        repo = UserRepository(db)
        if repo.get_by_email(email):
            return jsonify({"detail": "Email already registered"}), 409
        hashed = get_password_hash(password)
        user = repo.create(name=name, email=email, password_hash=hashed)
        db.commit()
        return jsonify(_user_out(user)), 201
    except Exception as e:
        db.rollback()
        return jsonify({"detail": str(e)}), 500
    finally:
        db.close()


@auth_bp.post("/login")
def login():
    """Accepts JSON {email, password} or form-encoded {username, password}."""
    if request.is_json:
        data = request.get_json(silent=True) or {}
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""
    else:
        email = (request.form.get("username") or "").strip().lower()
        password = request.form.get("password") or ""

    if not email or not password:
        return jsonify({"detail": "Email and password required"}), 400

    db = next(get_db())
    try:
        repo = UserRepository(db)
        user = repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            return jsonify({"detail": "Invalid credentials"}), 401
        if not user.is_active:
            return jsonify({"detail": "Account is inactive"}), 403

        access = create_access_token({"sub": str(user.id), "role": user.role})
        refresh = create_refresh_token({"sub": str(user.id)})
        expires = datetime.now(timezone.utc) + timedelta(days=config.JWT_REFRESH_DAYS)
        repo.save_refresh_token(user.id, refresh, expires)
        db.commit()

        _audit(db, user.id, "LOGIN", "auth", description=f"User {user.email} logged in",
               ip=request.remote_addr)
        db.commit()

        return jsonify({"access_token": access, "refresh_token": refresh, "token_type": "bearer"})
    except Exception as e:
        db.rollback()
        return jsonify({"detail": str(e)}), 500
    finally:
        db.close()


@auth_bp.post("/refresh")
def refresh():
    data = request.get_json(silent=True) or {}
    token = data.get("refresh_token") or ""
    if not token:
        return jsonify({"detail": "refresh_token required"}), 400

    payload = decode_token(token)
    if not payload or payload.get("type") != "refresh":
        return jsonify({"detail": "Invalid or expired refresh token"}), 401

    db = next(get_db())
    try:
        repo = UserRepository(db)
        stored = repo.get_refresh_token(token)
        if not stored:
            return jsonify({"detail": "Refresh token not found or revoked"}), 401

        user = repo.get_by_id(int(payload["sub"]))
        if not user or not user.is_active:
            return jsonify({"detail": "Account inactive"}), 403

        repo.revoke_refresh_token(token)
        new_access = create_access_token({"sub": str(user.id), "role": user.role})
        new_refresh = create_refresh_token({"sub": str(user.id)})
        expires = datetime.now(timezone.utc) + timedelta(days=config.JWT_REFRESH_DAYS)
        repo.save_refresh_token(user.id, new_refresh, expires)
        db.commit()

        return jsonify({"access_token": new_access, "refresh_token": new_refresh, "token_type": "bearer"})
    except Exception as e:
        db.rollback()
        return jsonify({"detail": str(e)}), 500
    finally:
        db.close()


@auth_bp.post("/logout")
def logout():
    data = request.get_json(silent=True) or {}
    token = data.get("refresh_token") or ""
    if token:
        db = next(get_db())
        try:
            repo = UserRepository(db)
            repo.revoke_refresh_token(token)
            db.commit()
        except Exception:
            pass
        finally:
            db.close()
    return jsonify({"message": "Logged out successfully"})


@auth_bp.get("/me")
@require_auth
def get_me():
    return jsonify(_user_out(g.current_user))


# ── helpers ───────────────────────────────────────────────────────────────────

def _user_out(u) -> dict:
    return {
        "id": u.id,
        "name": u.name,
        "email": u.email,
        "role": u.role,
        "is_active": u.is_active,
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def _audit(db, user_id, action, entity, description="", ip=None):
    from app.models.models import AuditLog
    log = AuditLog(user_id=user_id, action=action, entity=entity,
                   description=description, ip_address=ip)
    db.add(log)

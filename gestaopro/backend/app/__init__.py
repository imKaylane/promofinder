"""
GestãoPro — Entrypoint Flask
Serve a API REST (/api/v1/...) e os arquivos estáticos do frontend
no mesmo processo, na mesma porta (5000).
Um único comando: python run.py
"""
import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from app.config import config
from app.models.database import init_db, check_connection
from app.api.auth import auth_bp
from app.api.products import products_bp
from app.api.customers import customers_bp
from app.api.users import users_bp

# Pasta raiz do projeto GestãoPro (um nível acima de backend/)
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_FRONTEND_DIR = os.path.join(_PROJECT_ROOT, "frontend")
_INDEX_HTML   = os.path.join(_PROJECT_ROOT, "index.html")


def create_app() -> Flask:
    app = Flask(__name__, static_folder=None)
    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.config["DEBUG"] = config.DEBUG

    # CORS apenas para /api/* (frontend está na mesma origem, não precisa de CORS)
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # ── API Blueprints ──────────────────────────────────────────────────────
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(users_bp)

    # ── Health check ────────────────────────────────────────────────────────
    @app.get("/health")
    def health():
        db_ok = check_connection()
        return jsonify({
            "status": "ok" if db_ok else "degraded",
            "app": "GestãoPro",
            "version": "1.0.0",
            "database": "connected" if db_ok else "unreachable",
        }), 200 if db_ok else 503

    # ── Servir arquivos estáticos do frontend ───────────────────────────────
    # /frontend/css/main.css  →  gestaopro/frontend/css/main.css
    # /frontend/js/auth.js    →  gestaopro/frontend/js/auth.js
    # /frontend/pages/*.html  →  gestaopro/frontend/pages/*.html
    # /frontend/i18n/*.json   →  gestaopro/frontend/i18n/*.json
    @app.route("/frontend/<path:filepath>")
    def serve_frontend(filepath):
        return send_from_directory(_FRONTEND_DIR, filepath)

    # / → index.html (tela de login)
    @app.route("/")
    def serve_index():
        return send_from_directory(_PROJECT_ROOT, "index.html")

    # ── Error handlers ──────────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        # Se for uma rota de API, retorna JSON; caso contrário, serve o index
        from flask import request
        if request.path.startswith("/api/"):
            return jsonify({"detail": "Not found"}), 404
        return send_from_directory(_PROJECT_ROOT, "index.html")

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"detail": "Method not allowed"}), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"detail": "Internal server error"}), 500

    return app


app = create_app()

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=config.DEBUG)

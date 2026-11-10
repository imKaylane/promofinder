"""
GestãoPro — Entrypoint Flask
"""
from flask import Flask, jsonify
from flask_cors import CORS

from app.config import config
from app.models.database import init_db, check_connection
from app.api.auth import auth_bp
from app.api.products import products_bp
from app.api.customers import customers_bp
from app.api.users import users_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.config["DEBUG"] = config.DEBUG

    # CORS — allow frontend origins
    CORS(app, resources={r"/api/*": {"origins": config.CORS_ORIGINS}},
         supports_credentials=True)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(users_bp)

    # Health check
    @app.get("/health")
    def health():
        db_ok = check_connection()
        return jsonify({
            "status": "ok" if db_ok else "degraded",
            "app": "GestãoPro",
            "version": "1.0.0",
            "database": "connected" if db_ok else "unreachable",
        }), 200 if db_ok else 503

    # Global error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"detail": "Not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"detail": "Method not allowed"}), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"detail": "Internal server error"}), 500

    return app


app = create_app()

if __name__ == "__main__":
    # Init DB on startup (dev convenience)
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=config.DEBUG)

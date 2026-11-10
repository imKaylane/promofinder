"""GestãoPro — run.py (ponto de entrada para desenvolvimento)"""
from app import app
from app.models.database import init_db

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)

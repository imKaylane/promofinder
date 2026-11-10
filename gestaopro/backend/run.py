"""GestãoPro — run.py (ponto de entrada para desenvolvimento)"""
from app.config import config
config.validate_production()

from app import app
from app.models.database import init_db

if __name__ == "__main__":
    init_db()
    print("\n" + "=" * 50)
    print("  GestãoPro ERP")
    print("  Acesse: http://localhost:5000")
    print("=" * 50 + "\n")
    app.run(host="0.0.0.0", port=5000, debug=config.DEBUG)

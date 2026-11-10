"""
GestãoPro — Configuração da aplicação
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

_DEFAULT_SECRET = "CHANGE-ME-gestaopro-dev-only-not-for-production"


class Config:
    SECRET_KEY: str = os.getenv("SECRET_KEY", _DEFAULT_SECRET)
    FLASK_ENV: str = os.getenv("FLASK_ENV", "development")
    DEBUG: bool = os.getenv("FLASK_DEBUG", "true").lower() == "true"

    # MySQL via SQLAlchemy
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_USER: str = os.getenv("DB_USER", "gestaopro")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "gestaopro")
    DB_NAME: str = os.getenv("DB_NAME", "gestaopro")

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"?charset=utf8mb4"
        )

    # JWT
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))
    JWT_REFRESH_DAYS: int = int(os.getenv("JWT_REFRESH_DAYS", "7"))

    # CORS — ler do .env (separar por vírgula) ou usar padrão de dev
    @property
    def CORS_ORIGINS(self) -> list:
        raw = os.getenv("CORS_ORIGINS", "")
        if raw:
            return [o.strip() for o in raw.split(",") if o.strip()]
        return ["http://localhost:5500", "http://127.0.0.1:5500",
                "http://localhost:3000", "null"]

    def validate_production(self) -> None:
        """Recusa iniciar em modo produção com a SECRET_KEY padrão."""
        if self.FLASK_ENV == "production" and self.SECRET_KEY == _DEFAULT_SECRET:
            print(
                "ERRO: SECRET_KEY padrão detectada em modo produção. "
                "Defina SECRET_KEY no arquivo .env antes de iniciar.",
                file=sys.stderr,
            )
            sys.exit(1)


config = Config()

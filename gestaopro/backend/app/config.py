"""
GestãoPro — Configuração da aplicação
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "gestaopro-dev-secret")
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

    # CORS
    CORS_ORIGINS: list = ["http://localhost:5500", "http://127.0.0.1:5500",
                          "http://localhost:3000", "null"]


config = Config()

from pathlib import Path

from pydantic_settings import BaseSettings
from typing import List


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    # App
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://techdeals:techdeals@localhost:5432/techdeals"

    # Security
    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Mercado Livre
    MELI_CLIENT_ID: str = ""
    MELI_CLIENT_SECRET: str = ""
    MELI_REDIRECT_URI: str = "http://localhost:5173/auth/mercadolivre/callback"
    MELI_SITE_ID: str = "MLB"
    MELI_MAX_REQUESTS_PER_MINUTE: int = 60
    MELI_CACHE_TTL_SECONDS: int = 300
    MELI_COLLECTION_QUERIES: str = (
        "placa de video,processador,memoria ram,ssd nvme,perifericos gamer,"
        "monitor gamer,mouse gamer,teclado mecanico"
    )

    # AI
    AI_PROVIDER: str = "gemini"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.8-flash"

    # Redis / Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    model_config = {"env_file": PROJECT_ROOT / ".env", "extra": "ignore"}


settings = Settings()

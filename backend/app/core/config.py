from pydantic_settings import BaseSettings
from typing import List


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
    MELI_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/meli/callback"
    MELI_SITE_ID: str = "MLB"
    MELI_MAX_REQUESTS_PER_MINUTE: int = 60
    MELI_CACHE_TTL_SECONDS: int = 300

    # AI
    AI_PROVIDER: str = "disabled"  # openai | watsonx | disabled
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    WATSONX_API_KEY: str = ""
    WATSONX_PROJECT_ID: str = ""
    WATSONX_URL: str = "https://us-south.ml.cloud.ibm.com"
    WATSONX_MODEL_ID: str = "ibm/granite-13b-chat-v2"

    # Redis / Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

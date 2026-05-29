# app/core/config.py
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, Field
from typing import List, Optional


class Settings(BaseSettings):
    """Общие настройки приложения"""

    # Базовые настройки
    PROJECT_NAME: str = "Payment System API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = Field(default="postgresql+asyncpg://postgres:postgres@localhost:5432/payment_db")
    DB_ECHO: bool = Field(default=False)
    DB_POOL_SIZE: int = Field(default=20)
    DB_MAX_OVERFLOW: int = Field(default=10)
    DB_POOL_TIMEOUT: int = Field(default=30)

    # Security
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)

    # Webhook
    WEBHOOK_SECRET_KEY: str = Field(default="gfdmhghif38yrf9ew0jkf32")

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
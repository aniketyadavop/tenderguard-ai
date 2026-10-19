import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "TenderGuard AI"
    PROJECT_DESCRIPTION: str = (
        "Explainable AI Framework for Vendor Compliance Verification in Government Procurement (GeM / CPPP)"
    )
    VERSION: str = "4.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # Database & Cache
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./tenderguard.db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "tenderguard-in-gov-procurement-secret-key-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Short-lived (30 minutes) per Phase 6 standard

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",
    ]

    # File Upload Security
    MAX_UPLOAD_SIZE_BYTES: int = 25 * 1024 * 1024  # 25 MB max per statutory tender guidelines
    ALLOWED_MIME_TYPES: List[str] = [
        "application/pdf",
        "image/png",
        "image/jpeg",
        "image/jpg",
    ]
    UPLOAD_STORAGE_DIR: str = os.getenv(
        "UPLOAD_STORAGE_DIR",
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "uploads")
    )
    ZERO_RETENTION_MODE: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()

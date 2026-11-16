"""
app/config.py
Configuration settings loaded from environment or defaults.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    APP_NAME: str = "SamaadSetu Grievance Portal"
    APP_ENV: str = "development"
    APP_SECRET_KEY: str = "default_dev_secret_key_32_characters_long"
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["*"]

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./grievance.db"
    DATABASE_URL_SYNC: str = "sqlite:///./grievance.db"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 5

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # OpenAI
    OPENAI_API_KEY: Optional[str] = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    OPENAI_WHISPER_MODEL: str = "whisper-1"
    OPENAI_VLM_MODEL: str = "gpt-4o"
    OPENAI_EMBED_MODEL: str = "text-embedding-3-large"

    # Google Cloud
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    GOOGLE_TTS_LANGUAGE_CODE: str = "hi-IN"

    # Media Storage
    MEDIA_STORAGE_BACKEND: str = "local"
    MEDIA_LOCAL_DIR: Path = Path(__file__).resolve().parent.parent / "media"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

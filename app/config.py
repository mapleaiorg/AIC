# app/config.py - Clean version without syntax errors
import os
from pydantic_settings import BaseSettings
from typing import Optional, List
import secrets


class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "Maple AI Companion"
    VERSION: str = "2.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./maple_ai.db")

    # LLM Provider
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")

    # OpenAI settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")

    # Anthropic settings
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")

    # Google settings
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    GOOGLE_MODEL: str = os.getenv("GOOGLE_MODEL", "gemini-pro")

    # TTS Provider
    TTS_PROVIDER: str = os.getenv("TTS_PROVIDER", "edge")

    # File upload settings
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".png", ".jpg", ".jpeg", ".gif", ".webp"]

    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60

    # CORS settings
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "https://yourdomain.com"]

    # Advanced features
    VOICE_CLONING_ENABLED: bool = os.getenv("VOICE_CLONING_ENABLED", "false").lower() == "true"
    PERSONALITY_ADAPTATION_ENABLED: bool = os.getenv("PERSONALITY_ADAPTATION_ENABLED", "true").lower() == "true"
    MEMORY_RETENTION_DAYS: int = int(os.getenv("MEMORY_RETENTION_DAYS", "365"))
    ANALYTICS_ENABLED: bool = os.getenv("ANALYTICS_ENABLED", "true").lower() == "true"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


# Create settings instance
settings = Settings()

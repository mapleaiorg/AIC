# app/auth.py - Enhanced authentication system
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import secrets
import logging

from app.config import settings
from app.database import UserDB, get_db

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


class AuthenticationService:
    """Enhanced authentication service with advanced security features"""

    def __init__(self):
        self.failed_attempts = {}  # Track failed login attempts
        self.password_reset_tokens = {}  # Track password reset tokens

    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token with enhanced security"""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        # Add standard JWT claims
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "iss": settings.APP_NAME,
            "aud": "maple-ai-users",
            "jti": secrets.token_urlsafe(16)  # Unique token ID
        })

        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)  # Refresh tokens last 7 days

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
            "jti": secrets.token_urlsafe(16)
        })

        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify JWT token with enhanced validation"""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
                audience="maple-ai-users",
                issuer=settings.APP_NAME
            )

            # Verify token type if specified
            if token_type == "refresh" and payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def get_current_user(self, credentials: HTTPAuthorizationCredentials, db: Session) -> UserDB:
        """Get current user from token with enhanced security checks"""
        payload = self.verify_token(credentials.credentials)
        email: str = payload.get("sub")

        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = db.query(UserDB).filter(UserDB.email == email).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account temporarily locked",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Update last active timestamp
        user.last_active = datetime.utcnow()
        db.commit()

        return user

    def hash_password(self, password: str) -> str:
        """Hash password with bcrypt"""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)

    def generate_password_reset_token(self, email: str) -> str:
        """Generate password reset token"""
        token = secrets.token_urlsafe(32)
        self.password_reset_tokens[token] = {
            "email": email,
            "expires": datetime.utcnow() + timedelta(hours=1)
        }
        return token

    def verify_password_reset_token(self, token: str) -> Optional[str]:
        """Verify password reset token"""
        if token in self.password_reset_tokens:
            token_data = self.password_reset_tokens[token]
            if token_data["expires"] > datetime.utcnow():
                return token_data["email"]
            else:
                del self.password_reset_tokens[token]
        return None


# Global authentication service instance
auth_service = AuthenticationService()


# Dependency functions
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    return auth_service.create_access_token(data, expires_delta)


def create_refresh_token(data: Dict[str, Any]) -> str:
    return auth_service.create_refresh_token(data)


def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    return auth_service.verify_token(token, token_type)


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
) -> UserDB:
    return await auth_service.get_current_user(credentials, db)


async def get_current_active_user(current_user: UserDB = Depends(get_current_user)) -> UserDB:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_premium_user(current_user: UserDB = Depends(get_current_user)) -> UserDB:
    """Get current premium user"""
    if not current_user.is_premium:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Premium subscription required"
        )
    return current_user


# app/config.py - Enhanced configuration
import os
from pydantic_settings import BaseSettings
from typing import Optional, List
import secrets


class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "Maple AI Companion"
    VERSION: str = "2.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Enhanced security settings
    BCRYPT_ROUNDS: int = 12
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15
    PASSWORD_MIN_LENGTH: int = 8
    REQUIRE_EMAIL_VERIFICATION: bool = True

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./maple_ai.db")
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Redis (for caching and sessions)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_EXPIRE_SECONDS: int = 3600

    # LLM Provider (openai, anthropic, google, local)
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")

    # OpenAI settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_MAX_TOKENS: int = 1000
    OPENAI_TEMPERATURE: float = 0.7

    # Anthropic settings
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
    ANTHROPIC_MAX_TOKENS: int = 1000

    # Google settings
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    GOOGLE_MODEL: str = os.getenv("GOOGLE_MODEL", "gemini-pro")

    # TTS Provider (google, azure, aws, edge)
    TTS_PROVIDER: str = os.getenv("TTS_PROVIDER", "edge")  # Default to free edge-tts

    # Google Cloud TTS
    GOOGLE_CLOUD_CREDENTIALS: Optional[str] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    # Azure TTS
    AZURE_SPEECH_KEY: Optional[str] = os.getenv("AZURE_SPEECH_KEY")
    AZURE_SPEECH_REGION: Optional[str] = os.getenv("AZURE_SPEECH_REGION")

    # AWS Polly
    AWS_ACCESS_KEY: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

    # File upload settings
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".png", ".jpg", ".jpeg", ".gif", ".webp", ".mp3", ".wav", ".mp4"]
    UPLOAD_DIR: str = "uploads"

    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds
    RATE_LIMIT_ENABLED: bool = True

    # CORS settings
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "https://yourdomain.com"]
    ALLOW_CREDENTIALS: bool = True

    # Email settings (for notifications and verification)
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: Optional[str] = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "noreply@mapleai.org")

    # Monitoring and analytics
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    PROMETHEUS_ENABLED: bool = True
    ANALYTICS_ENABLED: bool = True
    LOG_LEVEL: str = "INFO"

    # Advanced AI features
    VOICE_CLONING_ENABLED: bool = False
    PERSONALITY_ADAPTATION_ENABLED: bool = True
    MEMORY_RETENTION_DAYS: int = 365
    MAX_CONVERSATION_HISTORY: int = 1000

    # Premium features
    PREMIUM_FEATURES_ENABLED: bool = True
    STRIPE_PUBLISHABLE_KEY: Optional[str] = os.getenv("STRIPE_PUBLISHABLE_KEY")
    STRIPE_SECRET_KEY: Optional[str] = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET: Optional[str] = os.getenv("STRIPE_WEBHOOK_SECRET")

    # Content moderation
    CONTENT_MODERATION_ENABLED: bool = True
    OPENAI_MODERATION_ENABLED: bool = True
    CUSTOM_WORD_FILTER_ENABLED: bool = True

    # Backup and disaster recovery
    AUTO_BACKUP_ENABLED: bool = True
    BACKUP_RETENTION_DAYS: int = 30
    BACKUP_STORAGE_PATH: str = "./backups"

    # Performance settings
    CACHE_TTL_SECONDS: int = 300  # 5 minutes
    MAX_CONCURRENT_REQUESTS: int = 100
    REQUEST_TIMEOUT_SECONDS: int = 30

    # Feature flags
    FEATURE_FLAGS: dict = {
        "multimodal_chat": True,
        "advanced_analytics": True,
        "voice_chat": True,
        "image_generation": False,
        "video_chat": False,
        "group_conversations": False
    }

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "forbid"  # Prevent typos in environment variables

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    def get_database_url(self) -> str:
        """Get database URL with connection parameters"""
        if "postgresql" in self.DATABASE_URL:
            return f"{self.DATABASE_URL}?pool_size={self.DATABASE_POOL_SIZE}&max_overflow={self.DATABASE_MAX_OVERFLOW}"
        return self.DATABASE_URL

    def validate_configuration(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []

        if not self.SECRET_KEY or self.SECRET_KEY == "your-secret-key-change-in-production":
            issues.append("SECRET_KEY must be set to a secure value")

        if self.LLM_PROVIDER == "openai" and not self.OPENAI_API_KEY:
            issues.append("OPENAI_API_KEY required when using OpenAI provider")

        if self.LLM_PROVIDER == "anthropic" and not self.ANTHROPIC_API_KEY:
            issues.append("ANTHROPIC_API_KEY required when using Anthropic provider")

        if self.LLM_PROVIDER == "google" and not self.GOOGLE_API_KEY:
            issues.append("GOOGLE_API_KEY required when using Google provider")

        if self.PREMIUM_FEATURES_ENABLED and not self.STRIPE_SECRET_KEY:
            issues.append("STRIPE_SECRET_KEY required when premium features are enabled")

        if self.REQUIRE_EMAIL_VERIFICATION and not self.SMTP_USERNAME:
            issues.append("SMTP configuration required when email verification is enabled")

        return issues


# Create settings instance
settings = Settings()

# Validate configuration on startup
if __name__ == "__main__":
    issues = settings.validate_configuration()
    if issues:
        print("⚠️  Configuration Issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ Configuration validated successfully")
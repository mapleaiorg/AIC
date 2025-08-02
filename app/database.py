# app/database.py - Fixed version
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime
from typing import AsyncGenerator

from app.config import settings

# Create database engine with proper configuration
if "sqlite" in settings.DATABASE_URL:
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# ===== ENHANCED USER MODELS =====

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    avatar_name = Column(String, default="maple_avatar_1")
    avatar_url = Column(String, nullable=True)

    # Timestamps
    join_date = Column(DateTime, default=datetime.utcnow, index=True)
    last_active = Column(DateTime, default=datetime.utcnow, index=True)
    last_login = Column(DateTime, nullable=True)

    # Status and security
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)

    # Personal info
    birth_date = Column(DateTime, nullable=True)
    timezone = Column(String, default="UTC")
    preferred_language = Column(String, default="en")

    # Usage statistics
    total_conversations = Column(Integer, default=0)
    total_messages = Column(Integer, default=0)
    total_voice_minutes = Column(Float, default=0.0)

    # Relationships
    chat_messages = relationship("ChatMessageDB", back_populates="user", cascade="all, delete-orphan")
    companion_state = relationship("CompanionStateDB", back_populates="user", uselist=False, cascade="all, delete-orphan")
    preferences = relationship("UserPreferencesDB", back_populates="user", uselist=False, cascade="all, delete-orphan")

class ChatMessageDB(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    content = Column(Text, nullable=False)
    is_user = Column(Boolean, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Enhanced message data
    message_type = Column(String, default="text")
    attachment_url = Column(String, nullable=True)
    emotion = Column(String, nullable=True)
    sentiment_score = Column(Float, default=0.0)
    confidence = Column(Float, default=0.8)

    # Relationships
    user = relationship("UserDB", back_populates="chat_messages")

class CompanionStateDB(Base):
    __tablename__ = "companion_states"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # Core stats
    mood = Column(String, default="happy")
    energy = Column(Integer, default=85)
    happiness = Column(Integer, default=75)
    intelligence = Column(Integer, default=90)

    # Relationship dynamics
    bond_level = Column(Integer, default=50)
    trust_level = Column(Integer, default=50)
    intimacy_level = Column(Integer, default=30)

    # Activity tracking
    last_interaction = Column(DateTime, default=datetime.utcnow, index=True)
    interaction_streak = Column(Integer, default=0)
    total_interactions = Column(Integer, default=0)

    # Personality dimensions (Big Five + custom)
    openness = Column(Float, default=0.7)
    conscientiousness = Column(Float, default=0.8)
    extraversion = Column(Float, default=0.6)
    agreeableness = Column(Float, default=0.9)
    neuroticism = Column(Float, default=0.2)

    # Custom AI traits
    playfulness = Column(Float, default=0.7)
    empathy = Column(Float, default=0.95)
    humor = Column(Float, default=0.7)
    supportiveness = Column(Float, default=0.95)
    adaptability = Column(Float, default=0.8)

    # Growth and learning
    experience_points = Column(Integer, default=0)
    skill_data = Column(JSON, default=dict)
    achievements = Column(JSON, default=list)

    user = relationship("UserDB", back_populates="companion_state")

class UserPreferencesDB(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # Voice settings
    voice = Column(String, default="maple_default")
    voice_speed = Column(Float, default=1.0)
    voice_pitch = Column(Float, default=1.0)

    # Notification settings
    notifications_enabled = Column(Boolean, default=True)
    companion_updates = Column(Boolean, default=True)
    daily_reminders = Column(Boolean, default=False)

    # Theme settings
    theme = Column(String, default="maple_red")
    dark_mode = Column(Boolean, default=False)

    # Other preferences
    companion_name = Column(String, default="Maple")
    auto_play_voice = Column(Boolean, default=False)

    user = relationship("UserDB", back_populates="preferences")

# ===== DATABASE INITIALIZATION =====

async def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")

async def get_db() -> AsyncGenerator[Session, None]:
    """Async dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_sync() -> Session:
    """Synchronous database session for background tasks"""
    return SessionLocal()

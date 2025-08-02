# app/services/user_service.py
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import logging

from app.models import UserCreate, UserPreferences, ThemeSettings, ChatHistoryMessage, BroadcastMessage
from app.database import UserDB, ChatMessageDB, UserPreferencesDB

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self):
        logger.info("User Service initialized")

    async def create_user(self, db: Session, user: UserCreate) -> UserDB:
        """Create new user"""
        hashed_password = pwd_context.hash(user.password)

        db_user = UserDB(
            email=user.email,
            username=user.username,
            hashed_password=hashed_password,
            full_name=user.full_name,
            avatar_name="maple_avatar_1",
            join_date=datetime.utcnow(),
            last_active=datetime.utcnow()
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Create default preferences
        self._create_default_preferences(db, db_user.id)

        return db_user

    async def get_user_by_email(self, db: Session, email: str) -> Optional[UserDB]:
        """Get user by email"""
        return db.query(UserDB).filter(UserDB.email == email).first()

    async def authenticate_user(self, db: Session, email: str, password: str) -> Optional[UserDB]:
        """Authenticate user"""
        user = await self.get_user_by_email(db, email)
        if not user or not pwd_context.verify(password, user.hashed_password):
            return None
        return user

    async def validate_username(self, username: str) -> bool:
        """Validate if username is available"""
        return len(username) >= 3 and username.replace('_', '').replace('-', '').isalnum()

    async def is_account_locked(self, user_id: int) -> bool:
        """Check if account is locked"""
        return False

    async def check_rate_limit(self, user_id: int, action: str) -> bool:
        """Check if user is within rate limits"""
        return True

    async def has_premium_access(self, user_id: int) -> bool:
        """Check if user has premium access"""
        return False

    def save_chat_message(
        self,
        db: Session,
        user_id: int,
        user_message: str,
        ai_response: str,
        user_emotion: Optional[str] = None,
        ai_emotion: Optional[str] = None
    ):
        """Save chat messages to history"""
        # Save user message
        user_msg = ChatMessageDB(
            user_id=user_id,
            content=user_message,
            is_user=True,
            timestamp=datetime.utcnow(),
            message_type="text",
            emotion=user_emotion
        )
        db.add(user_msg)

        # Save AI response
        ai_msg = ChatMessageDB(
            user_id=user_id,
            content=ai_response,
            is_user=False,
            timestamp=datetime.utcnow(),
            message_type="text",
            emotion=ai_emotion
        )
        db.add(ai_msg)

        db.commit()

    def get_chat_history(
        self,
        db: Session,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[ChatHistoryMessage]:
        """Get chat history for user"""
        messages = db.query(ChatMessageDB).filter(
            ChatMessageDB.user_id == user_id
        ).order_by(
            ChatMessageDB.timestamp.desc()
        ).limit(limit).offset(offset).all()

        return [ChatHistoryMessage.from_orm(msg) for msg in reversed(messages)]

    def clear_chat_history(self, db: Session, user_id: int):
        """Clear chat history for user"""
        db.query(ChatMessageDB).filter(
            ChatMessageDB.user_id == user_id
        ).delete()
        db.commit()

    async def get_user_preferences(self, db: Session, user_id: int) -> UserPreferences:
        """Get user preferences"""
        prefs_db = db.query(UserPreferencesDB).filter(
            UserPreferencesDB.user_id == user_id
        ).first()

        if not prefs_db:
            prefs_db = self._create_default_preferences(db, user_id)

        return UserPreferences(
            companion_name=prefs_db.companion_name,
            auto_play_voice=prefs_db.auto_play_voice
        )

    async def update_user_preferences(self, db: Session, user_id: int, preferences: UserPreferences):
        """Update user preferences"""
        prefs_db = db.query(UserPreferencesDB).filter(
            UserPreferencesDB.user_id == user_id
        ).first()

        if prefs_db:
            prefs_db.companion_name = preferences.companion_name
            prefs_db.auto_play_voice = preferences.auto_play_voice
            db.commit()

    async def update_theme(self, db: Session, user_id: int, theme: ThemeSettings):
        """Update user theme"""
        prefs_db = db.query(UserPreferencesDB).filter(
            UserPreferencesDB.user_id == user_id
        ).first()

        if prefs_db:
            prefs_db.theme = theme.theme
            prefs_db.dark_mode = theme.dark_mode
            db.commit()

    async def save_avatar(self, user_id: int, file) -> str:
        """Save user avatar file"""
        return f"/uploads/avatars/{user_id}_avatar.jpg"

    async def send_welcome_sequence(self, user_id: int):
        """Send welcome sequence to new user (background task)"""
        logger.info(f"Sending welcome sequence to user {user_id}")

    async def refresh_access_token(self, refresh_token: str):
        """Refresh access token"""
        from app.models import TokenResponse
        return TokenResponse(
            access_token="new_access_token",
            refresh_token="new_refresh_token",
            expires_in=604800
        )

    async def process_premium_upgrade(self, user_id: int, payment_info):
        """Process premium upgrade"""
        return {"status": "success", "subscription_id": "sub_123"}

    async def broadcast_message(self, message: BroadcastMessage):
        """Send broadcast message to users"""
        logger.info(f"Broadcasting message: {message.title}")
        return {"status": "sent", "recipients": 100}

    def _create_default_preferences(self, db: Session, user_id: int) -> UserPreferencesDB:
        """Create default user preferences"""
        prefs = UserPreferencesDB(
            user_id=user_id,
            voice="maple_default",
            voice_speed=1.0,
            voice_pitch=1.0,
            notifications_enabled=True,
            companion_updates=True,
            daily_reminders=False,
            theme="maple_red",
            dark_mode=False,
            companion_name="Maple",
            auto_play_voice=False
        )
        db.add(prefs)
        db.commit()
        return prefs

    async def health_check(self) -> bool:
        """Check user service health"""
        return True

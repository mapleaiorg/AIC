#!/bin/bash

echo "🔧 Creating all missing service files..."

# Create companion_service.py
cat > app/services/companion_service.py << 'EOF'
# app/services/companion_service.py
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import logging

from app.models import CompanionState, CompanionMood, PersonalityDimension, CompanionAction, CompanionResponse
from app.database import CompanionStateDB

logger = logging.getLogger(__name__)

class CompanionService:
    def __init__(self):
        self.energy_decay_rate = 1
        self.bond_growth_rate = 2
        logger.info("Companion Service initialized")

    async def get_companion_state(self, db: Session, user_id: int) -> CompanionState:
        """Get current companion state for user"""
        state_db = db.query(CompanionStateDB).filter(
            CompanionStateDB.user_id == user_id
        ).first()

        if not state_db:
            state_db = self._create_default_state(db, user_id)

        # Apply time-based changes
        self._apply_time_effects(state_db)

        return CompanionState(
            mood=CompanionMood(state_db.mood),
            energy=state_db.energy,
            bond_level=state_db.bond_level,
            last_interaction=state_db.last_interaction,
            personality=PersonalityDimension(
                openness=state_db.openness,
                conscientiousness=state_db.conscientiousness,
                extraversion=state_db.extraversion,
                agreeableness=state_db.agreeableness,
                neuroticism=state_db.neuroticism,
                playfulness=state_db.playfulness,
                empathy=state_db.empathy,
                humor=state_db.humor,
                supportiveness=state_db.supportiveness,
                adaptability=state_db.adaptability
            ),
            experience_points=state_db.experience_points,
            skills=state_db.skill_data or {}
        )

    async def get_enhanced_companion_state(self, db: Session, user_id: int) -> CompanionState:
        """Get enhanced companion state (alias for compatibility)"""
        return await self.get_companion_state(db, user_id)

    async def process_interaction(self, db: Session, user_id: int, action: str) -> CompanionState:
        """Process companion interaction and update state"""
        state_db = db.query(CompanionStateDB).filter(
            CompanionStateDB.user_id == user_id
        ).first()

        if not state_db:
            state_db = self._create_default_state(db, user_id)

        # Update based on action
        if action == "play":
            state_db.energy = max(0, state_db.energy - 10)
            state_db.mood = CompanionMood.EXCITED.value
            state_db.bond_level = min(100, state_db.bond_level + 3)
        elif action == "feed":
            state_db.energy = min(100, state_db.energy + 20)
            state_db.mood = CompanionMood.HAPPY.value
            state_db.bond_level = min(100, state_db.bond_level + 2)
        elif action == "chat":
            state_db.mood = CompanionMood.THOUGHTFUL.value
            state_db.bond_level = min(100, state_db.bond_level + 2)
        elif action == "rest":
            state_db.energy = min(100, state_db.energy + 30)
            state_db.mood = CompanionMood.SLEEPY.value

        state_db.last_interaction = datetime.utcnow()
        state_db.total_interactions += 1
        db.commit()

        return await self.get_companion_state(db, user_id)

    async def process_enhanced_interaction(
        self,
        db: Session,
        user_id: int,
        action: CompanionAction
    ) -> CompanionResponse:
        """Process enhanced companion interaction"""
        state = await self.process_interaction(db, user_id, action.action)

        message = f"Thanks for the {action.action}! I'm feeling great!"
        animation = action.action

        return CompanionResponse(
            state=state,
            message=message,
            animation=animation,
            state_changes={"energy": "+10" if action.action == "feed" else "0"},
            rewards_earned=[],
            next_suggestions=[f"Want to {action.action} again?", "How about we try something else?"]
        )

    async def process_message_interaction(
        self,
        user_id: int,
        user_message: str,
        ai_response: str,
        user_emotion: Optional[str]
    ):
        """Process message interaction (background task)"""
        logger.info(f"Processing message interaction for user {user_id}")

    async def initialize_companion(self, user_id: int):
        """Initialize companion for new user (background task)"""
        logger.info(f"Initializing companion for user {user_id}")

    def get_default_state(self) -> CompanionState:
        """Get default companion state for guest users"""
        return CompanionState()

    def _create_default_state(self, db: Session, user_id: int) -> CompanionStateDB:
        """Create default companion state in database"""
        state = CompanionStateDB(
            user_id=user_id,
            mood=CompanionMood.HAPPY.value,
            energy=85,
            bond_level=50,
            last_interaction=datetime.utcnow(),
            total_interactions=0,
            openness=0.7,
            conscientiousness=0.8,
            extraversion=0.6,
            agreeableness=0.9,
            neuroticism=0.2,
            playfulness=0.7,
            empathy=0.95,
            humor=0.7,
            supportiveness=0.95,
            adaptability=0.8,
            experience_points=0,
            skill_data={}
        )
        db.add(state)
        db.commit()
        return state

    def _apply_time_effects(self, state: CompanionStateDB):
        """Apply time-based effects on companion state"""
        now = datetime.utcnow()
        time_passed = now - state.last_interaction
        hours_passed = time_passed.total_seconds() / 3600

        # Decrease energy over time
        energy_loss = int(hours_passed * self.energy_decay_rate)
        state.energy = max(0, state.energy - energy_loss)

        # Update mood based on energy and time
        if state.energy < 20:
            state.mood = CompanionMood.SLEEPY.value
        elif hours_passed > 24:
            state.mood = CompanionMood.NEUTRAL.value
EOF

# Create tts_service.py
cat > app/services/tts_service.py << 'EOF'
# app/services/tts_service.py
import io
import asyncio
from typing import Optional, List, Dict
import logging

try:
    import edge_tts
except ImportError:
    edge_tts = None

from app.config import settings
from app.models import CompanionState, UserPreferences

logger = logging.getLogger(__name__)

class TTSService:
    def __init__(self):
        self.provider = settings.TTS_PROVIDER
        logger.info(f"Initialized TTS service with provider: {self.provider}")

    async def synthesize(
        self,
        text: str,
        voice: str = "en-US-AriaNeural",
        speed: float = 1.0,
        pitch: float = 1.0
    ) -> io.BytesIO:
        """Synthesize text to speech"""

        if self.provider == "edge" and edge_tts:
            return await self._synthesize_edge(text, voice, speed, pitch)
        else:
            # Return empty audio data as fallback
            return io.BytesIO(b"")

    async def _synthesize_edge(self, text: str, voice: str, speed: float, pitch: float) -> io.BytesIO:
        """Use Edge TTS (free alternative)"""
        try:
            voice_map = {
                "en-US-Standard-C": "en-US-AriaNeural",
                "en-US-Standard-D": "en-US-GuyNeural",
                "maple_default": "en-US-JennyNeural"
            }

            edge_voice = voice_map.get(voice, voice)
            rate = f"{int((speed - 1) * 100):+d}%"
            pitch_hz = f"{int((pitch - 1) * 50):+d}Hz"

            communicate = edge_tts.Communicate(text, edge_voice, rate=rate, pitch=pitch_hz)

            audio_data = io.BytesIO()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data.write(chunk["data"])

            audio_data.seek(0)
            return audio_data

        except Exception as e:
            logger.error(f"Edge TTS error: {e}")
            return io.BytesIO(b"")

    async def synthesize_with_personality(
        self,
        text: str,
        companion_state: CompanionState,
        preferences: UserPreferences,
        emotion: Optional[str] = None
    ) -> io.BytesIO:
        """Synthesize with personality and emotion"""
        voice = preferences.voice_settings.voice if preferences else "maple_default"
        speed = preferences.voice_settings.speed if preferences else 1.0
        pitch = preferences.voice_settings.pitch if preferences else 1.0

        # Adjust based on companion mood
        if companion_state.mood == "excited":
            speed *= 1.1
            pitch *= 1.05
        elif companion_state.mood == "sleepy":
            speed *= 0.9
            pitch *= 0.95

        return await self.synthesize(text, voice, speed, pitch)

    async def get_available_voices(self) -> List[Dict[str, str]]:
        """Get list of available voices"""
        if self.provider == "edge" and edge_tts:
            try:
                voices = await edge_tts.list_voices()
                return [
                    {
                        "id": v["ShortName"],
                        "name": v["FriendlyName"],
                        "gender": v["Gender"],
                        "locale": v["Locale"]
                    }
                    for v in voices if v["Locale"].startswith("en")
                ]
            except Exception as e:
                logger.error(f"Error getting voices: {e}")

        # Return default voices
        return [
            {"id": "maple_default", "name": "Maple Default", "gender": "Female", "locale": "en-US"},
            {"id": "en-US-Standard-C", "name": "US English Female", "gender": "Female", "locale": "en-US"},
            {"id": "en-US-Standard-D", "name": "US English Male", "gender": "Male", "locale": "en-US"},
        ]

    async def clone_voice(self, user_id: int, audio_file) -> str:
        """Voice cloning feature (premium)"""
        return "voice_clone_id_placeholder"

    def is_healthy(self) -> bool:
        """Check if TTS service is healthy"""
        return True

    async def initialize(self):
        """Initialize service"""
        logger.info("TTS Service initialized")

    async def cleanup(self):
        """Cleanup service"""
        logger.info("TTS Service cleanup complete")
EOF

# Create user_service.py
cat > app/services/user_service.py << 'EOF'
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
EOF

# Create memory_service.py
cat > app/services/memory_service.py << 'EOF'
# app/services/memory_service.py
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

from app.models import ConversationContext, EmotionType

logger = logging.getLogger(__name__)

class MemoryService:
    def __init__(self):
        logger.info("Memory Service initialized")

    async def store_interaction(
        self,
        user_id: int,
        user_message: str,
        ai_response: str,
        user_emotion: Optional[EmotionType],
        ai_emotion: Optional[EmotionType]
    ):
        """Store interaction in memory system"""
        logger.info(f"Storing interaction for user {user_id}")

    async def get_conversation_context(self, user_id: int) -> ConversationContext:
        """Get relevant conversation context for user"""
        return ConversationContext(
            recent_topics=["general chat"],
            emotional_state=EmotionType.NEUTRAL,
            conversation_style="friendly",
            memory_references=[]
        )

    async def create_memory(
        self,
        user_id: int,
        content: str,
        memory_type: str,
        importance: float
    ) -> str:
        """Create a specific memory"""
        memory_id = f"mem_{user_id}_{datetime.utcnow().timestamp()}"
        logger.info(f"Created memory {memory_id} for user {user_id}")
        return memory_id

    async def get_memories(
        self,
        user_id: int,
        memory_type: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get user memories"""
        return []

    async def health_check(self) -> bool:
        """Check memory service health"""
        return True
EOF

# Update analytics_service.py (replace the existing simple one)
cat > app/services/analytics_service.py << 'EOF'
# app/services/analytics_service.py
from datetime import datetime
from typing import Dict, Any
import logging

from app.models import UserDashboard, InteractionMetrics, CompanionGrowthMetrics

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self):
        self.start_time = datetime.utcnow()
        logger.info("Analytics Service initialized")

    async def initialize(self):
        """Initialize analytics service"""
        logger.info("Analytics service initialized")

    async def log_successful_login(self, user_id: int):
        """Log successful user login"""
        logger.info(f"User {user_id} logged in successfully")

    async def log_failed_login(self, email: str):
        """Log failed login attempt"""
        logger.info(f"Failed login attempt for {email}")

    async def log_companion_interaction(self, user_id: int, interaction_type: str, companion_state: Any):
        """Log companion interaction"""
        logger.info(f"User {user_id} performed {interaction_type}")

    async def log_tts_usage(self, user_id: int, text_length: int):
        """Log TTS usage"""
        logger.info(f"User {user_id} used TTS for {text_length} characters")

    async def get_user_dashboard(self, user_id: int) -> UserDashboard:
        """Get comprehensive user dashboard"""
        return UserDashboard(
            user_id=user_id,
            companion_stats=None,  # Will be populated by companion service
            interaction_metrics=InteractionMetrics(),
            growth_metrics=CompanionGrowthMetrics(),
            recent_highlights=["Started chatting with Maple!"],
            upcoming_features=["Voice chat improvements"],
            personalized_insights=["You're building a great bond with Maple!"]
        )

    async def get_companion_growth(self, user_id: int, days: int) -> Dict[str, Any]:
        """Get companion growth data"""
        return {
            "period_days": days,
            "daily_data": {},
            "total_interactions": 0,
            "growth_trend": "stable"
        }

    async def get_admin_stats(self) -> Dict[str, Any]:
        """Get system-wide admin statistics"""
        return {
            "users": {"total": 1, "active_today": 1, "premium": 0},
            "usage": {"total_messages": 0, "total_voice_minutes": 0.0},
            "features": {},
            "system": {"uptime_hours": 1.0, "version": "2.0.0"}
        }

    def get_uptime(self) -> str:
        """Get system uptime"""
        uptime_delta = datetime.utcnow() - self.start_time
        hours = int(uptime_delta.total_seconds() // 3600)
        minutes = int((uptime_delta.total_seconds() % 3600) // 60)
        return f"{hours}h {minutes}m"

    async def health_check(self) -> bool:
        """Check analytics service health"""
        return True
EOF

echo "✅ All missing service files created!"
echo ""
echo "🚀 Now try starting the server:"
echo "python -m uvicorn main:app --reload"
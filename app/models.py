# app/models.py - Fixed version without syntax errors
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any, Literal, Union
from datetime import datetime, date
from enum import Enum
import uuid


# ===== ENHANCED USER MODELS =====

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = Field(None, max_length=100)
    birth_date: Optional[date] = None
    timezone: Optional[str] = "UTC"

    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    avatar_name: str
    avatar_url: Optional[str]
    join_date: datetime
    last_active: Optional[datetime]
    is_premium: bool = False
    subscription_expires: Optional[datetime]
    companion_bond_level: int = 0
    total_conversations: int = 0

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ===== ENHANCED CHAT MODELS =====

class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VOICE = "voice"
    VIDEO = "video"
    COMPANION_ACTION = "companion_action"
    SYSTEM = "system"
    MEMORY = "memory"


class EmotionType(str, Enum):
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    NEUTRAL = "neutral"
    LOVE = "love"
    EXCITEMENT = "excitement"
    ANXIETY = "anxiety"
    CONTENTMENT = "contentment"


class ChatMessage(BaseModel):
    content: str = Field(..., max_length=5000)
    message_type: MessageType = MessageType.TEXT
    attachment_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}


class ChatResponse(BaseModel):
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    message_type: MessageType = MessageType.TEXT
    emotion: Optional[EmotionType] = None
    voice_emotion: Optional[EmotionType] = None
    confidence: float = Field(0.8, ge=0.0, le=1.0)
    personality_traits: Optional[Dict[str, float]] = {}
    response_context: Optional[Dict[str, Any]] = {}
    audio_url: Optional[str] = None
    animation: Optional[str] = None


class ConversationContext(BaseModel):
    recent_topics: List[str] = []
    emotional_state: EmotionType = EmotionType.NEUTRAL
    conversation_style: str = "friendly"
    user_preferences: Dict[str, Any] = {}
    memory_references: List[str] = []


class ChatHistoryMessage(BaseModel):
    id: int
    content: str
    is_user: bool
    timestamp: datetime
    message_type: MessageType
    emotion: Optional[EmotionType] = None

    class Config:
        from_attributes = True


class ChatHistory(BaseModel):
    messages: List[ChatHistoryMessage]
    total: int


# ===== ADVANCED COMPANION MODELS =====

class CompanionMood(str, Enum):
    ECSTATIC = "ecstatic"
    HAPPY = "happy"
    CONTENT = "content"
    NEUTRAL = "neutral"
    THOUGHTFUL = "thoughtful"
    MELANCHOLY = "melancholy"
    EXCITED = "excited"
    SLEEPY = "sleepy"
    PLAYFUL = "playful"
    CURIOUS = "curious"
    EMPATHETIC = "empathetic"
    ENERGETIC = "energetic"


class PersonalityDimension(BaseModel):
    """Advanced personality system based on Big Five + custom traits"""
    openness: float = Field(0.7, ge=0.0, le=1.0)
    conscientiousness: float = Field(0.8, ge=0.0, le=1.0)
    extraversion: float = Field(0.6, ge=0.0, le=1.0)
    agreeableness: float = Field(0.9, ge=0.0, le=1.0)
    neuroticism: float = Field(0.2, ge=0.0, le=1.0)

    # Custom AI companion traits
    playfulness: float = Field(0.7, ge=0.0, le=1.0)
    empathy: float = Field(0.95, ge=0.0, le=1.0)
    humor: float = Field(0.7, ge=0.0, le=1.0)
    intelligence: float = Field(0.9, ge=0.0, le=1.0)
    supportiveness: float = Field(0.95, ge=0.0, le=1.0)
    adaptability: float = Field(0.8, ge=0.0, le=1.0)


class CompanionMemory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    memory_type: Literal["personal", "preference", "experience", "fact", "emotion", "goal"]
    importance: float = Field(0.5, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed: Optional[datetime] = None
    access_count: int = 0
    emotional_weight: float = 0.0
    tags: List[str] = []


class CompanionState(BaseModel):
    # Core stats
    mood: CompanionMood = CompanionMood.HAPPY
    energy: int = Field(85, ge=0, le=100)
    happiness: int = Field(75, ge=0, le=100)
    intelligence: int = Field(90, ge=0, le=100)

    # Relationship dynamics
    bond_level: int = Field(50, ge=0, le=100)
    trust_level: int = Field(50, ge=0, le=100)
    intimacy_level: int = Field(30, ge=0, le=100)

    # Activity tracking
    last_interaction: datetime = Field(default_factory=datetime.utcnow)
    interaction_streak: int = 0
    favorite_activities: List[str] = []

    # Advanced features
    personality: PersonalityDimension = Field(default_factory=PersonalityDimension)
    memories: List[CompanionMemory] = []
    emotional_state: EmotionType = EmotionType.NEUTRAL
    conversation_style: str = "adaptive"

    # Growth metrics
    experience_points: int = 0
    skills: Dict[str, int] = {}
    achievements: List[str] = []

    # Contextual awareness
    current_focus: Optional[str] = None
    recent_topics: List[str] = []
    user_emotional_state: Optional[EmotionType] = None


# Create alias for backwards compatibility
EnhancedCompanionState = CompanionState


class CompanionAction(BaseModel):
    action: Literal[
        "play", "feed", "chat", "rest", "learn", "exercise",
        "creative", "explore", "meditate", "celebrate", "comfort"
    ]
    intensity: float = Field(1.0, ge=0.1, le=2.0)
    duration: Optional[int] = None
    context: Optional[str] = None


class CompanionResponse(BaseModel):
    state: CompanionState
    message: str
    animation: str
    sound_effects: Optional[List[str]] = []
    state_changes: Dict[str, Any] = {}
    rewards_earned: List[str] = []
    next_suggestions: List[str] = []


# ===== MEMORY SYSTEM MODELS =====

class CreateMemoryRequest(BaseModel):
    content: str = Field(..., max_length=1000)
    memory_type: Literal["personal", "preference", "experience", "fact", "emotion", "goal"]
    importance: float = Field(0.5, ge=0.0, le=1.0)
    tags: List[str] = []


class MemoryResponse(BaseModel):
    id: str
    content: str
    memory_type: str
    importance: float
    created_at: datetime
    relevance_score: float
    emotional_context: Optional[EmotionType]


# ===== ENHANCED TTS MODELS =====

class TTSRequest(BaseModel):
    text: str = Field(..., max_length=2000)
    voice: Optional[str] = "maple_default"
    speed: Optional[float] = Field(1.0, ge=0.5, le=2.0)
    pitch: Optional[float] = Field(1.0, ge=0.5, le=2.0)
    emotion: Optional[EmotionType] = EmotionType.NEUTRAL
    style: Optional[Literal["conversational", "expressive", "calm", "energetic"]] = "conversational"


class TTSResponse(BaseModel):
    audio_url: str
    duration: float
    voice_used: str
    emotion_applied: Optional[EmotionType]
    file_size: int


# ===== ADVANCED USER PREFERENCES =====

class VoiceSettings(BaseModel):
    voice: str = "maple_default"
    speed: float = Field(1.0, ge=0.5, le=2.0)
    pitch: float = Field(1.0, ge=0.5, le=2.0)
    emotion_expression: bool = True
    voice_effects: List[str] = []
    custom_voice_id: Optional[str] = None


class NotificationSettings(BaseModel):
    enabled: bool = True
    companion_updates: bool = True
    daily_reminders: bool = False
    mood_check_ins: bool = True
    achievement_alerts: bool = True
    quiet_hours_start: Optional[str] = "22:00"
    quiet_hours_end: Optional[str] = "08:00"


class PrivacySettings(BaseModel):
    data_sharing: bool = False
    analytics_opt_in: bool = True
    voice_storage: bool = False
    conversation_history: Literal["full", "limited", "minimal"] = "full"
    memory_retention_days: int = 365


class AccessibilitySettings(BaseModel):
    high_contrast: bool = False
    large_text: bool = False
    voice_navigation: bool = False
    haptic_feedback: bool = True
    screen_reader_support: bool = False


class ThemeSettings(BaseModel):
    theme: Literal[
        "maple_red", "sakura_pink", "ocean_blue", "forest_green", "sunset_orange", "midnight_purple"] = "maple_red"
    dark_mode: bool = False
    custom_colors: Optional[Dict[str, str]] = None
    seasonal_themes: bool = True
    animations_enabled: bool = True


class UserPreferences(BaseModel):
    voice_settings: VoiceSettings = Field(default_factory=VoiceSettings)
    notification_settings: NotificationSettings = Field(default_factory=NotificationSettings)
    privacy_settings: PrivacySettings = Field(default_factory=PrivacySettings)
    accessibility_settings: AccessibilitySettings = Field(default_factory=AccessibilitySettings)
    theme_settings: ThemeSettings = Field(default_factory=ThemeSettings)

    # Companion preferences
    companion_name: str = "Maple"
    companion_appearance: str = "default"
    interaction_style: Literal["formal", "casual", "playful", "supportive"] = "casual"
    conversation_topics: List[str] = []
    content_filters: List[str] = []

    # Advanced features
    auto_play_voice: bool = False
    proactive_conversations: bool = True
    learning_mode: bool = True
    multilingual_support: bool = False
    preferred_language: str = "en"


# ===== ANALYTICS MODELS =====

class InteractionMetrics(BaseModel):
    total_messages: int = 0
    total_voice_minutes: float = 0.0
    average_session_length: float = 0.0
    favorite_interaction_times: List[str] = []
    most_used_features: List[str] = []
    emotional_journey: List[Dict[str, Any]] = []


class CompanionGrowthMetrics(BaseModel):
    bond_growth_rate: float = 0.0
    skill_improvements: Dict[str, float] = {}
    milestone_achievements: List[Dict[str, Any]] = []
    personality_evolution: List[Dict[str, Any]] = []


class UserDashboard(BaseModel):
    user_id: int
    companion_stats: CompanionState
    interaction_metrics: InteractionMetrics
    growth_metrics: CompanionGrowthMetrics
    recent_highlights: List[str] = []
    upcoming_features: List[str] = []
    personalized_insights: List[str] = []


# ===== PREMIUM FEATURES =====

class SubscriptionTier(str, Enum):
    FREE = "free"
    PREMIUM = "premium"
    ULTRA = "ultra"


class PaymentInfo(BaseModel):
    payment_method_id: str
    billing_address: Dict[str, str]
    tier: SubscriptionTier


class SubscriptionInfo(BaseModel):
    tier: SubscriptionTier
    expires_at: Optional[datetime]
    features: List[str]
    usage_limits: Dict[str, int]
    auto_renew: bool = True


# ===== RESPONSE MODELS =====

class APIResponse(BaseModel):
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error_code: str
    error_message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None


# ===== ADMIN MODELS =====

class BroadcastMessage(BaseModel):
    title: str
    content: str
    target_audience: Literal["all", "premium", "new_users", "active"] = "all"
    priority: Literal["low", "medium", "high", "urgent"] = "medium"
    expires_at: Optional[datetime] = None


class SystemStats(BaseModel):
    total_users: int
    active_users_today: int
    total_conversations: int
    total_voice_minutes: float
    average_session_length: float
    popular_features: List[Dict[str, Any]]
    system_health: Dict[str, Any]


# For backwards compatibility
Token = TokenResponse
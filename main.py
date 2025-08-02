# main.py - Fixed and simplified for current state
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import uvicorn
from typing import Optional, List
import os
from datetime import datetime
import logging

# Import models and services
from app.models import (
    UserCreate, UserLogin, UserResponse, TokenResponse,
    ChatMessage, ChatResponse, ChatHistory,
    CompanionState, CompanionAction, CompanionResponse,
    TTSRequest, TTSResponse,
    UserPreferences, ThemeSettings
)
from app.auth import create_access_token, verify_token, get_current_user
from app.database import init_db, get_db
from app.services import (
    LLMService, TTSService, CompanionService,
    UserService, AnalyticsService, MemoryService
)
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize services
llm_service = LLMService()
tts_service = TTSService()
companion_service = CompanionService()
user_service = UserService()
analytics_service = AnalyticsService()
memory_service = MemoryService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🍁 Starting Maple AI Companion Backend v2.0...")

    # Initialize database
    await init_db()

    # Initialize services
    await llm_service.initialize()
    await tts_service.initialize()
    await analytics_service.initialize()

    # Create necessary directories
    os.makedirs("uploads/avatars", exist_ok=True)
    os.makedirs("uploads/temp", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    logger.info("✅ Maple AI Backend started successfully!")
    yield

    # Shutdown
    logger.info("🔄 Shutting down Maple AI Backend...")
    await llm_service.cleanup()
    await tts_service.cleanup()
    logger.info("✅ Shutdown complete!")


app = FastAPI(
    title="Maple AI Companion API",
    description="Next-generation AI companion backend with advanced personality, memory, and emotion systems",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

security = HTTPBearer()


# ===== BASIC ENDPOINTS =====

@app.get("/")
async def root():
    return {
        "message": "🍁 Welcome to Maple AI Companion API v2.0",
        "version": "2.0.0",
        "status": "online",
        "features": [
            "Advanced AI personality system",
            "Long-term memory",
            "Emotion recognition",
            "Multi-modal interaction",
            "Real-time analytics"
        ]
    }


@app.get("/health")
async def health_check():
    """Enhanced health check with service status"""
    services_status = {
        "llm": llm_service.is_healthy(),
        "tts": tts_service.is_healthy(),
        "database": await user_service.health_check(),
        "analytics": await analytics_service.health_check(),
        "memory": await memory_service.health_check()
    }

    overall_healthy = all(services_status.values())

    return {
        "status": "healthy" if overall_healthy else "degraded",
        "timestamp": datetime.utcnow(),
        "services": services_status,
        "uptime": analytics_service.get_uptime(),
        "version": "2.0.0"
    }


# ===== AUTHENTICATION ENDPOINTS =====

@app.post("/auth/register", response_model=UserResponse)
async def register(user: UserCreate, background_tasks: BackgroundTasks, db=Depends(get_db)):
    """Enhanced user registration"""
    existing_user = await user_service.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Enhanced validation
    if not await user_service.validate_username(user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username not available or invalid"
        )

    new_user = await user_service.create_user(db, user)

    # Background welcome flow
    background_tasks.add_task(user_service.send_welcome_sequence, new_user.id)
    background_tasks.add_task(companion_service.initialize_companion, new_user.id)

    return UserResponse.from_orm(new_user)


@app.post("/auth/login", response_model=TokenResponse)
async def login(user_login: UserLogin, db=Depends(get_db)):
    """Enhanced login with security features"""
    user = await user_service.authenticate_user(db, user_login.email, user_login.password)
    if not user:
        await analytics_service.log_failed_login(user_login.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Check if account is locked
    if await user_service.is_account_locked(user.id):
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account temporarily locked due to security"
        )

    access_token = create_access_token(data={"sub": user.email, "user_id": user.id})

    # Log successful login
    await analytics_service.log_successful_login(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token="refresh_token_placeholder",  # Implement refresh token logic
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db=Depends(get_db)
):
    """Get current user information"""
    user = await get_current_user(credentials, db)
    return UserResponse.from_orm(user)


# ===== ENHANCED CHAT ENDPOINTS =====

@app.post("/chat/message", response_model=ChatResponse)
async def send_message(
        message: ChatMessage,
        background_tasks: BackgroundTasks,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db=Depends(get_db)
):
    """Enhanced chat with context awareness, memory, and emotion analysis"""
    user = await get_current_user(credentials, db)

    # Rate limiting check
    if not await user_service.check_rate_limit(user.id, "chat"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please slow down."
        )

    # Get conversation context
    context = await memory_service.get_conversation_context(user.id)
    companion_state = await companion_service.get_companion_state(db, user.id)

    # Generate AI response with enhanced context
    response = await llm_service.generate_response(
        message=message.content,
        user_id=user.id,
        companion_state=companion_state,
        conversation_context=context,
        message_type=message.message_type
    )

    # Process companion state changes
    background_tasks.add_task(
        companion_service.process_message_interaction,
        user.id,
        message.content,
        response.content,
        None  # user_emotion placeholder
    )

    # Update memory
    background_tasks.add_task(
        memory_service.store_interaction,
        user.id,
        message.content,
        response.content,
        None,  # user_emotion
        response.emotion
    )

    # Save to chat history
    background_tasks.add_task(
        user_service.save_chat_message,
        db,
        user.id,
        message.content,
        response.content
    )

    return response


@app.get("/chat/history", response_model=ChatHistory)
async def get_chat_history(
        limit: int = 50,
        offset: int = 0,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db=Depends(get_db)
):
    """Get chat history for the current user"""
    user = await get_current_user(credentials, db)
    messages = user_service.get_chat_history(db, user.id, limit, offset)
    return ChatHistory(messages=messages, total=len(messages))


@app.delete("/chat/history")
async def clear_chat_history(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db=Depends(get_db)
):
    """Clear chat history for the current user"""
    user = await get_current_user(credentials, db)
    user_service.clear_chat_history(db, user.id)
    return {"message": "Chat history cleared successfully"}


@app.get("/chat/suggestions")
async def get_chat_suggestions(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db=Depends(get_db)
):
    """Get contextual chat suggestions"""
    user = await get_current_user(credentials, db)

    context = await memory_service.get_conversation_context(user.id)
    companion_state = await companion_service.get_companion_state(db, user.id)

    suggestions = await llm_service.generate_chat_suggestions(
        user_id=user.id,
        context=context,
        companion_state=companion_state
    )

    return {"suggestions": suggestions}


# ===== ADVANCED COMPANION ENDPOINTS =====

@app.get("/companion/state", response_model=CompanionState)
async def get_companion_state(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db=Depends(get_db)
):
    """Get enhanced companion state"""
    user = await get_current_user(credentials, db)
    state = await companion_service.get_companion_state(db, user.id)
    return state


@app.post("/companion/interact", response_model=CompanionResponse)
async def interact_with_companion(
        action: CompanionAction,
        background_tasks: BackgroundTasks,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db=Depends(get_db)
):
    """Enhanced companion interaction"""
    user = await get_current_user(credentials, db)

    # Process interaction with enhanced logic
    response = await companion_service.process_enhanced_interaction(
        db, user.id, action
    )

    # Update analytics
    background_tasks.add_task(
        analytics_service.log_companion_interaction,
        user.id,
        action.action,
        response.state
    )

    return response


# ===== ENHANCED TTS ENDPOINTS =====

@app.post("/tts/synthesize")
async def synthesize_speech(
        request: TTSRequest,
        background_tasks: BackgroundTasks,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db=Depends(get_db)
):
    """Enhanced TTS with emotion and personality"""
    user = await get_current_user(credentials, db)

    # Get user preferences and companion state
    preferences = await user_service.get_user_preferences(db, user.id)
    companion_state = await companion_service.get_companion_state(db, user.id)

    # Generate audio with personality
    audio_data = await tts_service.synthesize_with_personality(
        text=request.text,
        companion_state=companion_state,
        preferences=preferences,
        emotion=request.emotion
    )

    # Log usage
    background_tasks.add_task(
        analytics_service.log_tts_usage,
        user.id,
        len(request.text)
    )

    return StreamingResponse(
        audio_data,
        media_type="audio/mp3",
        headers={
            "Content-Disposition": "attachment; filename=maple_speech.mp3"
        }
    )


@app.get("/tts/voices")
async def get_available_voices():
    """Get list of available TTS voices"""
    voices = await tts_service.get_available_voices()
    return {"voices": voices}


# ===== USER PREFERENCES ENDPOINTS =====

@app.get("/user/preferences", response_model=UserPreferences)
async def get_user_preferences(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db=Depends(get_db)
):
    """Get user preferences"""
    user = await get_current_user(credentials, db)
    preferences = await user_service.get_user_preferences(db, user.id)
    return preferences


@app.put("/user/preferences")
async def update_user_preferences(
        preferences: UserPreferences,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db=Depends(get_db)
):
    """Update user preferences"""
    user = await get_current_user(credentials, db)
    await user_service.update_user_preferences(db, user.id, preferences)
    return {"message": "Preferences updated successfully"}


@app.put("/user/theme")
async def update_theme(
        theme: ThemeSettings,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db=Depends(get_db)
):
    """Update user theme preferences"""
    user = await get_current_user(credentials, db)
    await user_service.update_theme(db, user.id, theme)
    return {"message": "Theme updated successfully"}


# ===== ANALYTICS & INSIGHTS =====

@app.get("/analytics/dashboard")
async def get_analytics_dashboard(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db=Depends(get_db)
):
    """Get user analytics dashboard"""
    user = await get_current_user(credentials, db)
    dashboard = await analytics_service.get_user_dashboard(user.id)
    return dashboard


@app.get("/analytics/companion-growth")
async def get_companion_growth(
        days: int = 30,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db=Depends(get_db)
):
    """Get companion growth analytics"""
    user = await get_current_user(credentials, db)
    growth_data = await analytics_service.get_companion_growth(user.id, days)
    return growth_data


# ===== FILE UPLOAD ENDPOINTS =====

@app.post("/upload/avatar")
async def upload_avatar(
        file: UploadFile = File(...),
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db=Depends(get_db)
):
    """Upload custom avatar image"""
    user = await get_current_user(credentials, db)

    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )

    # Save file
    file_path = await user_service.save_avatar(user.id, file)

    return {"avatar_url": file_path}


# ===== GUEST MODE ENDPOINTS =====

@app.post("/guest/chat", response_model=ChatResponse)
async def guest_chat(message: ChatMessage):
    """Guest mode chat - limited features"""
    response = await llm_service.generate_response(
        message=message.content,
        user_id=None,
        companion_state=companion_service.get_default_state(),
        message_type=message.message_type
    )
    return response


@app.post("/guest/tts")
async def guest_tts(request: TTSRequest):
    """Guest mode TTS - limited to 100 characters"""
    if len(request.text) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Guest mode limited to 100 characters"
        )

    audio_data = await tts_service.synthesize(
        text=request.text,
        voice="maple_default",
        speed=1.0,
        pitch=1.0
    )

    return StreamingResponse(
        audio_data,
        media_type="audio/mp3"
    )


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP {exc.status_code}: {exc.detail}")
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "timestamp": datetime.utcnow().isoformat()}
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
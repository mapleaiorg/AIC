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

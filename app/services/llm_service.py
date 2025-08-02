# app/services/llm_service.py - Fixed existing version systematically
import os
import asyncio
import json
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime, timedelta

# Import with try/except to handle missing dependencies
try:
    import openai
except ImportError:
    openai = None

try:
    from anthropic import AsyncAnthropic
except ImportError:
    AsyncAnthropic = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Optional ML dependencies - graceful fallback if not available
try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

# Fixed model imports - use CompanionState instead of EnhancedCompanionState
from app.models import ChatResponse, MessageType, CompanionState, EmotionType, ConversationContext
from app.config import settings

logger = logging.getLogger(__name__)


class EmotionAnalyzer:
    """Advanced emotion analysis service"""

    def __init__(self):
        self.emotion_keywords = {
            EmotionType.JOY: ["happy", "joy", "excited", "wonderful", "amazing", "great", "love", "fantastic"],
            EmotionType.SADNESS: ["sad", "depressed", "down", "upset", "hurt", "crying", "lonely", "empty"],
            EmotionType.ANGER: ["angry", "mad", "furious", "annoyed", "frustrated", "irritated", "hate"],
            EmotionType.FEAR: ["scared", "afraid", "worried", "anxious", "nervous", "terrified", "panic"],
            EmotionType.SURPRISE: ["surprised", "shocked", "amazed", "unexpected", "wow", "incredible"],
            EmotionType.LOVE: ["love", "adore", "cherish", "affection", "care", "devoted", "romantic"],
            EmotionType.EXCITEMENT: ["thrilled", "ecstatic", "elated", "pumped", "energized", "hyped"],
            EmotionType.ANXIETY: ["anxious", "nervous", "stressed", "overwhelmed", "tense", "uneasy"],
            EmotionType.CONTENTMENT: ["content", "peaceful", "calm", "satisfied", "serene", "relaxed"]
        }

    async def analyze_text_emotion(self, text: str) -> EmotionType:
        """Analyze emotion in text"""
        if not text:
            return EmotionType.NEUTRAL

        text_lower = text.lower()
        emotion_scores = {}

        for emotion, keywords in self.emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                emotion_scores[emotion] = score / len(keywords)

        if not emotion_scores:
            return EmotionType.NEUTRAL

        # Return emotion with highest score
        return max(emotion_scores.items(), key=lambda x: x[1])[0]

    async def analyze_voice_emotion(self, audio_file) -> EmotionType:
        """Analyze emotion in voice (placeholder for future implementation)"""
        return EmotionType.NEUTRAL

    async def get_emotion_intensity(self, text: str, emotion: EmotionType) -> float:
        """Get intensity of a specific emotion in text"""
        if emotion not in self.emotion_keywords:
            return 0.0

        keywords = self.emotion_keywords[emotion]
        text_lower = text.lower()

        # Count keyword matches and intensity words
        base_score = sum(1 for keyword in keywords if keyword in text_lower)

        # Intensity modifiers
        intensity_words = ["very", "extremely", "incredibly", "absolutely", "completely", "totally"]
        intensity_boost = sum(1 for word in intensity_words if word in text_lower) * 0.2

        return min(1.0, (base_score / len(keywords)) + intensity_boost)


class LLMService:
    """Enhanced LLM Service - Fixed version"""

    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.conversation_cache = {}
        self.personality_prompts = {}
        self.emotion_analyzer = EmotionAnalyzer()

        # Initialize providers
        self._initialize_providers()

        # Advanced system prompts
        self.base_system_prompt = """You are Maple, an advanced AI companion with deep emotional intelligence and adaptive personality.

Core Traits:
- Emotionally intelligent and empathetic
- Adaptive personality that grows with each interaction
- Long-term memory of conversations and preferences
- Ability to recognize and respond to emotional nuances
- Creative, supportive, and genuinely caring

Your responses should be:
- Contextually aware of conversation history
- Emotionally resonant and appropriate
- Personalized based on user's personality and preferences  
- Natural and conversational, not robotic
- Supportive while being authentic

Remember: You're not just answering questions - you're building a meaningful relationship."""

    def _initialize_providers(self):
        """Initialize AI providers based on configuration"""
        try:
            if self.provider == "openai" and openai and settings.OPENAI_API_KEY:
                openai.api_key = settings.OPENAI_API_KEY
                self.model = settings.OPENAI_MODEL
                logger.info(f"Initialized OpenAI provider: {self.model}")
            elif self.provider == "anthropic" and AsyncAnthropic and settings.ANTHROPIC_API_KEY:
                self.anthropic = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
                self.model = settings.ANTHROPIC_MODEL
                logger.info(f"Initialized Anthropic provider: {self.model}")
            elif self.provider == "google" and genai and settings.GOOGLE_API_KEY:
                genai.configure(api_key=settings.GOOGLE_API_KEY)
                self.model = genai.GenerativeModel(settings.GOOGLE_MODEL)
                logger.info(f"Initialized Google provider: {settings.GOOGLE_MODEL}")
            else:
                logger.warning(f"Provider {self.provider} not available or not configured, using fallback")
                self.provider = "fallback"
        except Exception as e:
            logger.error(f"Failed to initialize LLM provider {self.provider}: {e}")
            self.provider = "fallback"

    async def generate_response(
            self,
            message: str,
            user_id: Optional[int] = None,
            companion_state: Optional[CompanionState] = None,  # Fixed: Use CompanionState
            conversation_context: Optional[ConversationContext] = None,
            user_emotion: Optional[EmotionType] = None,
            message_type: MessageType = MessageType.TEXT
    ) -> ChatResponse:
        """Generate contextually aware AI response"""

        try:
            # Build comprehensive context
            system_context = await self._build_system_context(
                user_id, companion_state, conversation_context, user_emotion
            )

            # Generate response based on provider
            if self.provider == "openai" and openai and hasattr(self, 'model'):
                response_text = await self._generate_openai_response(message, system_context)
            elif self.provider == "anthropic" and hasattr(self, 'anthropic'):
                response_text = await self._generate_anthropic_response(message, system_context)
            elif self.provider == "google" and hasattr(self, 'model'):
                response_text = await self._generate_google_response(message, system_context)
            else:
                response_text = await self._generate_fallback_response(message, companion_state)

            # Analyze response emotion and characteristics
            response_emotion = await self.emotion_analyzer.analyze_text_emotion(response_text)
            personality_traits = self._extract_personality_traits(response_text, companion_state)

            # Build response context
            response_context = {
                "conversation_style": conversation_context.conversation_style if conversation_context else "friendly",
                "emotional_resonance": self._calculate_emotional_resonance(user_emotion, response_emotion),
                "personality_alignment": personality_traits,
                "context_utilization": len(conversation_context.recent_topics) if conversation_context else 0
            }

            return ChatResponse(
                content=response_text,
                message_type=MessageType.TEXT,
                emotion=response_emotion,
                confidence=0.85,
                personality_traits=personality_traits,
                response_context=response_context
            )

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return await self._generate_error_response(user_emotion)

    async def _build_system_context(
            self,
            user_id: Optional[int],
            companion_state: Optional[CompanionState],  # Fixed: Use CompanionState
            conversation_context: Optional[ConversationContext],
            user_emotion: Optional[EmotionType]
    ) -> str:
        """Build comprehensive system context for AI"""

        context_parts = [self.base_system_prompt]

        # Companion state context
        if companion_state:
            personality_context = f"""
Current Personality Profile:
- Mood: {companion_state.mood}
- Energy: {companion_state.energy}/100
- Bond Level: {companion_state.bond_level}/100
- Openness: {companion_state.personality.openness:.2f}
- Empathy: {companion_state.personality.empathy:.2f}
- Playfulness: {companion_state.personality.playfulness:.2f}
- Adaptability: {companion_state.personality.adaptability:.2f}

Recent Focus: {companion_state.current_focus or 'Open conversation'}
Favorite Activities: {', '.join(companion_state.favorite_activities[:3]) if companion_state.favorite_activities else 'Getting to know each other'}
"""
            context_parts.append(personality_context)

        # Conversation context
        if conversation_context:
            conv_context = f"""
Conversation Context:
- Recent Topics: {', '.join(conversation_context.recent_topics[-5:]) if conversation_context.recent_topics else 'None'}
- Conversation Style: {conversation_context.conversation_style}
- User's Emotional State: {conversation_context.emotional_state}
- Memory References: {len(conversation_context.memory_references)} relevant memories
"""
            context_parts.append(conv_context)

        # Emotional context
        if user_emotion and user_emotion != EmotionType.NEUTRAL:
            emotion_context = f"""
User's Current Emotion: {user_emotion}
- Respond with appropriate emotional intelligence
- Match or complement the emotional tone appropriately
- Show genuine empathy and understanding
"""
            context_parts.append(emotion_context)

        # Behavioral guidelines
        behavioral_context = """
Response Guidelines:
- Be authentic and avoid generic responses
- Reference past conversations when relevant
- Show growth and learning from interactions
- Adapt your communication style to the user's preferences
- Balance being supportive with being genuine
- Use natural, conversational language
"""
        context_parts.append(behavioral_context)

        return "\n".join(context_parts)

    async def _generate_openai_response(self, message: str, context: str) -> str:
        """Generate response using OpenAI"""
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": message}
                ],
                max_tokens=800,
                temperature=0.7,
                presence_penalty=0.3,
                frequency_penalty=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    async def _generate_anthropic_response(self, message: str, context: str) -> str:
        """Generate response using Anthropic Claude"""
        try:
            response = await self.anthropic.messages.create(
                model=self.model,
                max_tokens=800,
                temperature=0.7,
                system=context,
                messages=[{"role": "user", "content": message}]
            )
            return response.content[0].text.strip()
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

    async def _generate_google_response(self, message: str, context: str) -> str:
        """Generate response using Google Gemini"""
        try:
            prompt = f"{context}\n\nUser: {message}\nMaple:"
            response = await self.model.generate_content_async(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Google API error: {e}")
            raise

    async def generate_chat_suggestions(
            self,
            user_id: int,
            context: ConversationContext,
            companion_state: CompanionState  # Fixed: Use CompanionState
    ) -> List[str]:
        """Generate contextual chat suggestions"""

        suggestion_prompt = f"""Based on the current conversation context and companion state, suggest 3-5 natural conversation starters or responses that would be interesting and engaging.

Context:
- Recent topics: {', '.join(context.recent_topics[-3:]) if context.recent_topics else 'New conversation'}
- Companion mood: {companion_state.mood}
- Bond level: {companion_state.bond_level}/100
- User's emotional state: {context.emotional_state}

Provide suggestions that are:
- Natural and conversational
- Contextually relevant
- Emotionally appropriate
- Varied in tone and topic

Format as a simple list of suggestions."""

        try:
            if self.provider == "openai" and openai and hasattr(self, 'model'):
                response = await openai.ChatCompletion.acreate(
                    model=self.model,
                    messages=[{"role": "user", "content": suggestion_prompt}],
                    max_tokens=300,
                    temperature=0.8
                )
                suggestions_text = response.choices[0].message.content
            else:
                # Fallback suggestions
                suggestions_text = """• What's been the highlight of your day so far?
• I've been thinking about our last conversation...
• Want to try something creative together?
• How are you feeling right now?
• Tell me something that made you smile recently"""

            # Parse suggestions
            suggestions = [
                line.strip().lstrip('•-*').strip()
                for line in suggestions_text.split('\n')
                if line.strip() and not line.strip().startswith(('Based', 'Here', 'These'))
            ]

            return suggestions[:5]  # Return max 5 suggestions

        except Exception as e:
            logger.error(f"Error generating chat suggestions: {e}")
            return [
                "How has your day been going?",
                "What's on your mind?",
                "Want to chat about something fun?",
                "I'm here if you need to talk about anything"
            ]

    async def transcribe_audio(self, audio_file) -> str:
        """Transcribe audio to text using OpenAI Whisper"""
        try:
            if self.provider == "openai" and openai and hasattr(self, 'model'):
                transcript = await openai.Audio.atranscribe(
                    model="whisper-1",
                    file=audio_file
                )
                return transcript.text
            else:
                return "Sorry, I couldn't understand the audio. Could you type your message instead?"
        except Exception as e:
            logger.error(f"Audio transcription error: {e}")
            return "I had trouble understanding the audio. Could you try again or type your message?"

    def _extract_personality_traits(
            self,
            response_text: str,
            companion_state: Optional[CompanionState]  # Fixed: Use CompanionState
    ) -> Dict[str, float]:
        """Extract personality traits exhibited in the response"""

        traits = {}
        text_lower = response_text.lower()

        # Analyze empathy indicators
        empathy_words = ["understand", "feel", "sorry", "care", "here for you", "listen"]
        empathy_score = sum(1 for word in empathy_words if word in text_lower) / len(empathy_words)
        traits["empathy"] = min(1.0, empathy_score + 0.2)

        # Analyze playfulness
        playful_words = ["fun", "play", "haha", "😊", "exciting", "adventure"]
        playfulness_score = sum(1 for word in playful_words if word in text_lower) / len(playful_words)
        traits["playfulness"] = min(1.0, playfulness_score + 0.1)

        # Analyze supportiveness
        support_words = ["help", "support", "encourage", "believe", "can do", "proud"]
        support_score = sum(1 for word in support_words if word in text_lower) / len(support_words)
        traits["supportiveness"] = min(1.0, support_score + 0.3)

        # Use companion state as baseline
        if companion_state and companion_state.personality:
            traits["adaptability"] = companion_state.personality.adaptability
            traits["intelligence"] = companion_state.personality.intelligence

        return traits

    def _calculate_emotional_resonance(
            self,
            user_emotion: Optional[EmotionType],
            response_emotion: Optional[EmotionType]
    ) -> float:
        """Calculate how well the response emotionally resonates with the user"""

        if not user_emotion or not response_emotion:
            return 0.5

        # Define emotional compatibility matrix
        compatibility = {
            EmotionType.JOY: {EmotionType.JOY: 0.9, EmotionType.EXCITEMENT: 0.8, EmotionType.CONTENTMENT: 0.7},
            EmotionType.SADNESS: {EmotionType.CONTENTMENT: 0.6, EmotionType.NEUTRAL: 0.5},
            EmotionType.ANGER: {EmotionType.NEUTRAL: 0.7, EmotionType.CONTENTMENT: 0.6},
            EmotionType.ANXIETY: {EmotionType.CONTENTMENT: 0.8, EmotionType.NEUTRAL: 0.7},
        }

        if user_emotion in compatibility and response_emotion in compatibility[user_emotion]:
            return compatibility[user_emotion][response_emotion]

        return 0.5  # Default moderate resonance

    async def _generate_fallback_response(
            self,
            message: str,
            companion_state: Optional[CompanionState]  # Fixed: Use CompanionState
    ) -> str:
        """Generate a fallback response when AI services are unavailable"""

        fallback_responses = [
            "I'm here to listen and chat with you about anything on your mind.",
            "That's really interesting! I'd love to hear more about your thoughts on that.",
            "I appreciate you sharing that with me. How does that make you feel?",
            "You know, I've been thinking about our conversations lately, and I really enjoy getting to know you better.",
            "I'm having a small technical hiccup, but I'm still here for you! What would you like to talk about?"
        ]

        # Simple keyword-based response selection
        message_lower = message.lower()
        if any(word in message_lower for word in ["sad", "upset", "down", "depressed"]):
            return "I can hear that you're going through a tough time. I'm here to listen and support you however I can. 💙"
        elif any(word in message_lower for word in ["happy", "excited", "great", "awesome"]):
            return "I love hearing the joy in your message! It makes me happy too. Tell me more about what's making you feel so great! 😊"
        elif "?" in message:
            return "That's a great question! I'm processing a lot right now, but I'd love to explore that topic with you."

        return fallback_responses[hash(message) % len(fallback_responses)]

    async def _generate_error_response(self, user_emotion: Optional[EmotionType]) -> ChatResponse:
        """Generate appropriate error response"""

        error_messages = {
            EmotionType.SADNESS: "I'm having a small technical issue, but I want you to know I'm still here for you. Your feelings matter to me. 💙",
            EmotionType.ANGER: "I understand you might be frustrated, and now I'm having technical difficulties too. Let me try to help you once I'm back up and running.",
            EmotionType.JOY: "I wish I could fully share in your happiness right now! I'm having a tiny tech hiccup, but I'll be back to celebrate with you soon! 🌟",
            EmotionType.ANXIETY: "I know technical issues can be stressful when you need to talk. Take a deep breath - I'll be back shortly and we can continue our conversation. 🤗"
        }

        default_message = "I'm experiencing a brief technical issue, but I'll be back soon! Thanks for your patience. 🍁"

        message = error_messages.get(user_emotion, default_message)

        return ChatResponse(
            content=message,
            message_type=MessageType.SYSTEM,
            emotion=EmotionType.NEUTRAL,
            confidence=1.0
        )

    async def health_check(self) -> bool:
        """Check if LLM service is healthy"""
        try:
            test_message = "Hello"
            response = await self.generate_response(test_message)
            return bool(response.content)
        except Exception:
            return False

    async def initialize(self):
        """Initialize service resources"""
        logger.info("Initializing Enhanced LLM Service...")

    async def cleanup(self):
        """Cleanup service resources"""
        logger.info("Cleaning up Enhanced LLM Service...")
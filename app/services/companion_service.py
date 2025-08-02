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

from typing import Dict, Any, List
from .base_agent import BaseAgent
import logging
from datetime import datetime, timedelta

class EmotionalAnchoringAgent(BaseAgent):
    def __init__(self):
        super().__init__("emotional_anchoring")
        self.narrative_themes = {}
        self.user_stories = {}
        self.milestone_celebrations = {}
        
    async def initialize(self):
        self.logger.info("Initializing Emotional Anchoring Agent")
        await self.load_narrative_themes()
        
    async def process_cycle(self):
        try:
            # Process user milestones
            await self.process_milestones()
            # Update narrative experiences
            await self.update_narratives()
            # Generate emotional touchpoints
            await self.generate_emotional_touchpoints()
        except Exception as e:
            self.logger.error(f"Error in emotional anchoring cycle: {e}")

    async def load_narrative_themes(self):
        """Load predefined narrative themes"""
        self.narrative_themes = {
            "journey": {
                "title": "Community Journey",
                "milestones": ["first_post", "first_collaboration", "mentor_status"],
                "emotional_anchors": {
                    "beginning": "Starting your adventure",
                    "progress": "Growing together",
                    "achievement": "Reaching new heights"
                }
            },
            "mastery": {
                "title": "Path to Mastery",
                "milestones": ["skill_acquired", "knowledge_shared", "expert_recognition"],
                "emotional_anchors": {
                    "learning": "Discovering new horizons",
                    "teaching": "Sharing your wisdom",
                    "recognition": "Becoming a guiding light"
                }
            }
        }

    async def create_user_story(self, user_id: str, theme: str) -> Dict[str, Any]:
        """Create personalized story for user"""
        if theme not in self.narrative_themes:
            raise ValueError(f"Invalid theme: {theme}")

        story = {
            "user_id": user_id,
            "theme": theme,
            "started_at": datetime.now(),
            "milestones": {},
            "current_chapter": "beginning",
            "emotional_touchpoints": []
        }

        self.user_stories[user_id] = story
        return story

    async def process_milestones(self):
        """Process user milestones and generate celebrations"""
        try:
            pending_milestones = await self.get_pending_milestones()
            for milestone in pending_milestones:
                await self.celebrate_milestone(milestone)
        except Exception as e:
            self.logger.error(f"Error processing milestones: {e}")

    async def celebrate_milestone(self, milestone: Dict[str, Any]):
        """Create celebration event for milestone"""
        user_id = milestone["user_id"]
        milestone_type = milestone["type"]

        celebration = {
            "user_id": user_id,
            "milestone_type": milestone_type,
            "timestamp": datetime.now(),
            "celebration_theme": self.get_celebration_theme(milestone_type),
            "community_impact": self.calculate_community_impact(milestone)
        }

        self.milestone_celebrations[user_id] = celebration
        await self.trigger_celebration_events(celebration)

    async def trigger_celebration_events(self, celebration: Dict[str, Any]):
        """Trigger celebration events and notifications"""
        await self.send_message(
            "feedback_loop",
            {
                "type": "milestone_celebration",
                "celebration": celebration,
                "priority": "high"
            }
        )

        # Update user's narrative
        user_id = celebration["user_id"]
        if user_id in self.user_stories:
            self.user_stories[user_id]["milestones"][celebration["milestone_type"]] = {
                "achieved_at": celebration["timestamp"],
                "celebration": celebration
            }

    async def update_narratives(self):
        """Update user narratives and story progression"""
        for user_id, story in self.user_stories.items():
            try:
                progress = await self.calculate_story_progress(story)
                new_chapter = self.determine_story_chapter(progress)
                
                if new_chapter != story["current_chapter"]:
                    story["current_chapter"] = new_chapter
                    await self.generate_chapter_transition(user_id, new_chapter)
            except Exception as e:
                self.logger.error(f"Error updating narrative for user {user_id}: {e}")

    async def generate_emotional_touchpoints(self):
        """Generate emotional connection points"""
        try:
            active_users = await self.get_active_users()
            for user_id in active_users:
                engagement = await self.get_user_engagement(user_id)
                if self.needs_emotional_touchpoint(engagement):
                    await self.create_emotional_touchpoint(user_id, engagement)
        except Exception as e:
            self.logger.error(f"Error generating emotional touchpoints: {e}")

    def needs_emotional_touchpoint(self, engagement: Dict[str, Any]) -> bool:
        """Determine if user needs emotional touchpoint"""
        last_touchpoint = engagement.get("last_emotional_touchpoint")
        if not last_touchpoint:
            return True

        time_since_last = datetime.now() - last_touchpoint
        return time_since_last > timedelta(days=3)

    async def create_emotional_touchpoint(self, user_id: str, engagement: Dict[str, Any]):
        """Create emotional touchpoint for user"""
        story = self.user_stories.get(user_id)
        if not story:
            return

        touchpoint = {
            "type": "emotional_touchpoint",
            "timestamp": datetime.now(),
            "theme": story["theme"],
            "chapter": story["current_chapter"],
            "content": self.generate_emotional_content(story)
        }

        story["emotional_touchpoints"].append(touchpoint)
        await self.send_message(
            "feedback_loop",
            {
                "type": "emotional_touchpoint",
                "user_id": user_id,
                "touchpoint": touchpoint
            }
        )

    def generate_emotional_content(self, story: Dict[str, Any]) -> str:
        """Generate emotional content based on user's story"""
        theme = self.narrative_themes[story["theme"]]
        chapter = story["current_chapter"]
        return theme["emotional_anchors"][chapter]

    def get_celebration_theme(self, milestone_type: str) -> Dict[str, Any]:
        """Get celebration theme for milestone type"""
        themes = {
            "first_post": {"style": "welcoming", "intensity": "medium"},
            "collaboration": {"style": "community", "intensity": "high"},
            "expert": {"style": "achievement", "intensity": "high"}
        }
        return themes.get(milestone_type, {"style": "general", "intensity": "medium"})

    def calculate_community_impact(self, milestone: Dict[str, Any]) -> float:
        """Calculate milestone's impact on community"""
        impact_scores = {
            "first_post": 0.3,
            "collaboration": 0.7,
            "expert": 1.0
        }
        return impact_scores.get(milestone["type"], 0.5)

    async def get_pending_milestones(self) -> List[Dict[str, Any]]:
        """Get pending milestones for celebration"""
        # Implementation would fetch from database
        return []

    async def calculate_story_progress(self, story: Dict[str, Any]) -> float:
        """Calculate progress in user's story"""
        theme = self.narrative_themes[story["theme"]]
        completed = len(story["milestones"])
        total = len(theme["milestones"])
        return completed / total if total > 0 else 0

    def determine_story_chapter(self, progress: float) -> str:
        """Determine current story chapter based on progress"""
        if progress < 0.3:
            return "beginning"
        elif progress < 0.7:
            return "progress"
        else:
            return "achievement"

    async def get_active_users(self) -> List[str]:
        """Get list of active users"""
        # Implementation would fetch from database
        return []

    async def get_user_engagement(self, user_id: str) -> Dict[str, Any]:
        """Get user engagement data"""
        # Implementation would fetch from database
        return {}

    async def cleanup(self):
        """Cleanup agent resources"""
        self.logger.info("Cleaning up Emotional Anchoring Agent")
        # Save current state
        await self.save_state()

    async def save_state(self):
        """Save current state to persistent storage"""
        # Implementation would save to database
        pass

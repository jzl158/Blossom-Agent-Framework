from typing import Dict, Any, List
from .base_agent import BaseAgent
import logging
from datetime import datetime, timedelta

class BehaviorMonitoringAgent(BaseAgent):
    def __init__(self):
        super().__init__("behavior_monitoring")
        self.behavior_patterns = {}
        self.engagement_thresholds = {
            "high": 0.8,
            "medium": 0.5,
            "low": 0.2
        }

    async def initialize(self):
        self.logger.info("Initializing Behavior Monitoring Agent")
        await self.load_historical_patterns()

    async def process_cycle(self):
        try:
            # Monitor active users
            active_users = await self.get_active_users()
            for user in active_users:
                await self.analyze_user_behavior(user)
            
            # Check for disengagement signals
            await self.detect_disengagement()
            
            # Update engagement metrics
            await self.update_engagement_metrics()
        except Exception as e:
            self.logger.error(f"Error in behavior monitoring cycle: {e}")

    async def analyze_user_behavior(self, user_id: str):
        """Analyze individual user behavior patterns"""
        try:
            # Get recent activities
            activities = await self.get_user_activities(user_id)
            
            # Calculate engagement metrics
            engagement_score = self.calculate_engagement_score(activities)
            interaction_frequency = self.calculate_interaction_frequency(activities)
            content_depth = self.analyze_content_depth(activities)
            
            # Store behavior pattern
            self.behavior_patterns[user_id] = {
                "engagement_score": engagement_score,
                "interaction_frequency": interaction_frequency,
                "content_depth": content_depth,
                "last_updated": datetime.now()
            }
            
            # Send insights to other agents
            await self.broadcast_behavior_insights(user_id)
            
        except Exception as e:
            self.logger.error(f"Error analyzing behavior for user {user_id}: {e}")

    def calculate_engagement_score(self, activities: List[Dict[str, Any]]) -> float:
        """Calculate user engagement score based on activities"""
        if not activities:
            return 0.0
        
        score = 0.0
        weights = {
            "content_creation": 1.0,
            "interaction": 0.7,
            "reaction": 0.3
        }
        
        for activity in activities:
            activity_type = activity.get("type", "")
            if activity_type in weights:
                score += weights[activity_type]
        
        return min(1.0, score / len(activities))

    def calculate_interaction_frequency(self, activities: List[Dict[str, Any]]) -> float:
        """Calculate frequency of user interactions"""
        if not activities:
            return 0.0
        
        now = datetime.now()
        day_counts = {}
        
        for activity in activities:
            activity_date = activity.get("timestamp", now).date()
            day_counts[activity_date] = day_counts.get(activity_date, 0) + 1
        
        return sum(day_counts.values()) / len(day_counts)

    def analyze_content_depth(self, activities: List[Dict[str, Any]]) -> float:
        """Analyze depth of user engagement with content"""
        if not activities:
            return 0.0
        
        depth_score = 0.0
        for activity in activities:
            # Score based on time spent and interaction type
            time_spent = activity.get("duration", 0)
            interaction_type = activity.get("type", "")
            
            if interaction_type == "content_creation":
                depth_score += min(1.0, time_spent / 300)  # Cap at 5 minutes
            elif interaction_type == "interaction":
                depth_score += min(0.7, time_spent / 180)  # Cap at 3 minutes
            
        return min(1.0, depth_score / len(activities))

    async def detect_disengagement(self):
        """Detect users showing signs of disengagement"""
        threshold = timedelta(days=7)
        now = datetime.now()
        
        for user_id, pattern in self.behavior_patterns.items():
            last_active = pattern.get("last_updated", now)
            if (now - last_active) > threshold:
                await self.send_message(
                    "emotional_anchoring",
                    {
                        "type": "disengagement_risk",
                        "user_id": user_id,
                        "days_inactive": (now - last_active).days
                    }
                )

    async def broadcast_behavior_insights(self, user_id: str):
        """Share behavior insights with other agents"""
        if user_id in self.behavior_patterns:
            pattern = self.behavior_patterns[user_id]
            
            # Share with relevant agents
            await self.send_message(
                "motivation_mapping",
                {
                    "type": "behavior_insight",
                    "user_id": user_id,
                    "pattern": pattern
                }
            )
            
            await self.send_message(
                "habit_formation",
                {
                    "type": "engagement_pattern",
                    "user_id": user_id,
                    "pattern": pattern
                }
            )

    async def get_user_activities(self, user_id: str) -> List[Dict[str, Any]]:
        """Get recent user activities"""
        # Implementation would fetch from database
        return []

    async def get_active_users(self) -> List[str]:
        """Get list of currently active users"""
        # Implementation would fetch from database
        return []

    async def load_historical_patterns(self):
        """Load historical behavior patterns"""
        # Implementation would load from database
        pass

    async def cleanup(self):
        """Cleanup agent resources"""
        self.logger.info("Cleaning up Behavior Monitoring Agent")
        # Save current behavior patterns
        await self.save_behavior_patterns()

    async def save_behavior_patterns(self):
        """Save behavior patterns to persistent storage"""
        # Implementation would save to database
        pass

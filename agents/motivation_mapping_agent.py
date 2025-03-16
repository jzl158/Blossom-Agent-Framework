from typing import Dict, Any
from .base_agent import BaseAgent
import logging
from data.models import UserProfile

class MotivationMappingAgent(BaseAgent):
    def __init__(self):
        super().__init__("motivation_mapping")
        self.user_profiles = {}
        
    async def initialize(self):
        self.logger.info("Initializing Motivation Mapping Agent")
        # Load existing user profiles
        self.user_profiles = await UserProfile.load_all()

    async def process_cycle(self):
        """Analyze user behaviors and update motivation profiles"""
        try:
            users = await self.get_active_users()
            for user in users:
                profile = await self.analyze_user_motivation(user)
                await self.update_user_profile(user, profile)
        except Exception as e:
            self.logger.error(f"Error in motivation mapping cycle: {e}")

    async def analyze_user_motivation(self, user: Dict[str, Any]) -> Dict[str, float]:
        """Analyze user's motivation factors"""
        motivators = {
            'achievement': 0.0,
            'social': 0.0,
            'mastery': 0.0,
            'progress': 0.0
        }
        
        # Analyze recent activities
        activities = await self.get_user_activities(user['id'])
        for activity in activities:
            motivators['achievement'] += self.calculate_achievement_score(activity)
            motivators['social'] += self.calculate_social_score(activity)
            motivators['mastery'] += self.calculate_mastery_score(activity)
            motivators['progress'] += self.calculate_progress_score(activity)
            
        # Normalize scores
        total = sum(motivators.values())
        if total > 0:
            motivators = {k: v/total for k, v in motivators.items()}
            
        return motivators

    async def get_active_users(self):
        """Get list of active users for analysis"""
        # Implementation would connect to user database
        return []

    async def update_user_profile(self, user: Dict[str, Any], profile: Dict[str, float]):
        """Update user's motivation profile"""
        try:
            user_profile = self.user_profiles.get(user['id'])
            if user_profile:
                user_profile.update_motivators(profile)
                await user_profile.save()
            else:
                new_profile = UserProfile(user['id'], profile)
                await new_profile.save()
                self.user_profiles[user['id']] = new_profile
        except Exception as e:
            self.logger.error(f"Failed to update user profile: {e}")

    def calculate_achievement_score(self, activity: Dict[str, Any]) -> float:
        """Calculate achievement motivation score from activity"""
        score = 0.0
        if activity.get('completed_tasks', 0) > 0:
            score += 0.5
        if activity.get('badges_earned', 0) > 0:
            score += 0.3
        return score

    def calculate_social_score(self, activity: Dict[str, Any]) -> float:
        """Calculate social motivation score from activity"""
        score = 0.0
        if activity.get('interactions', 0) > 0:
            score += 0.4
        if activity.get('collaborations', 0) > 0:
            score += 0.6
        return score

    def calculate_mastery_score(self, activity: Dict[str, Any]) -> float:
        """Calculate mastery motivation score from activity"""
        score = 0.0
        if activity.get('skill_progress', 0) > 0:
            score += 0.7
        if activity.get('learning_events', 0) > 0:
            score += 0.3
        return score

    def calculate_progress_score(self, activity: Dict[str, Any]) -> float:
        """Calculate progress motivation score from activity"""
        score = 0.0
        if activity.get('goals_progress', 0) > 0:
            score += 0.6
        if activity.get('milestones_reached', 0) > 0:
            score += 0.4
        return score

    async def cleanup(self):
        """Cleanup agent resources"""
        self.logger.info("Cleaning up Motivation Mapping Agent")
        # Save any pending profile updates
        for profile in self.user_profiles.values():
            await profile.save()

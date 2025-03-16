from typing import Dict, Any, List
from .base_agent import BaseAgent
import logging
from datetime import datetime, timedelta

class HabitFormationAgent(BaseAgent):
    def __init__(self):
        super().__init__("habit_formation")
        self.user_streaks = {}
        self.habit_triggers = {}
        self.engagement_patterns = {}
        
    async def initialize(self):
        self.logger.info("Initializing Habit Formation Agent")
        await self.load_existing_streaks()
        await self.initialize_habit_triggers()
        
    async def process_cycle(self):
        try:
            # Update streaks
            await self.update_streaks()
            # Check and send reminders
            await self.process_reminders()
            # Analyze and optimize habits
            await self.optimize_habits()
        except Exception as e:
            self.logger.error(f"Error in habit formation cycle: {e}")

    async def load_existing_streaks(self):
        """Load existing user streaks"""
        # Implementation would load from database
        pass

    async def initialize_habit_triggers(self):
        """Initialize habit triggers"""
        self.habit_triggers = {
            "daily_check": {
                "interval": timedelta(days=1),
                "reminder_template": "Don't break your daily streak! {streak_count} days and counting!"
            },
            "weekly_engagement": {
                "interval": timedelta(days=7),
                "reminder_template": "Keep up your weekly momentum! You're on week {streak_count}!"
            },
            "contribution": {
                "interval": timedelta(days=3),
                "reminder_template": "Time to share your insights! Last contribution: {last_contribution}"
            }
        }

    async def update_streaks(self):
        """Update user streaks based on activity"""
        try:
            active_users = await self.get_active_users()
            for user_id in active_users:
                activities = await self.get_user_activities(user_id)
                await self.process_user_streaks(user_id, activities)
        except Exception as e:
            self.logger.error(f"Error updating streaks: {e}")

    async def process_user_streaks(self, user_id: str, activities: List[Dict[str, Any]]):
        """Process and update user's streaks"""
        if not user_id in self.user_streaks:
            self.user_streaks[user_id] = {
                "daily": 0,
                "weekly": 0,
                "contribution": 0,
                "last_activity": None
            }

        streak = self.user_streaks[user_id]
        last_activity = streak["last_activity"]
        current_time = datetime.now()

        for activity in activities:
            activity_time = activity["timestamp"]
            
            # Update daily streak
            if not last_activity or self.is_consecutive_day(last_activity, activity_time):
                streak["daily"] += 1
            else:
                streak["daily"] = 1

            # Update weekly streak
            if not last_activity or self.is_same_week(last_activity, activity_time):
                streak["weekly"] += 1
            else:
                streak["weekly"] = 1

            # Update contribution streak
            if activity["type"] == "contribution":
                if not last_activity or self.is_within_days(last_activity, activity_time, 3):
                    streak["contribution"] += 1
                else:
                    streak["contribution"] = 1

            streak["last_activity"] = activity_time

        # Check for streak achievements
        await self.check_streak_achievements(user_id, streak)

    async def process_reminders(self):
        """Process and send habit reminders"""
        try:
            current_time = datetime.now()
            for user_id, streak in self.user_streaks.items():
                for trigger_type, trigger in self.habit_triggers.items():
                    if self.should_send_reminder(streak, trigger, current_time):
                        await self.send_reminder(user_id, trigger_type, streak)
        except Exception as e:
            self.logger.error(f"Error processing reminders: {e}")

    async def optimize_habits(self):
        """Analyze and optimize habit formation strategies"""
        try:
            for user_id in self.user_streaks:
                patterns = await self.analyze_engagement_patterns(user_id)
                self.engagement_patterns[user_id] = patterns
                
                if patterns["needs_optimization"]:
                    await self.adjust_habit_strategy(user_id, patterns)
        except Exception as e:
            self.logger.error(f"Error optimizing habits: {e}")

    async def analyze_engagement_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analyze user engagement patterns"""
        streak = self.user_streaks.get(user_id, {})
        activities = await self.get_user_activities(user_id)
        
        patterns = {
            "peak_activity_times": self.calculate_peak_times(activities),
            "engagement_frequency": self.calculate_frequency(activities),
            "streak_sustainability": self.calculate_streak_sustainability(streak),
            "needs_optimization": False
        }
        
        # Check if optimization is needed
        patterns["needs_optimization"] = self.needs_optimization(patterns)
        return patterns

    async def adjust_habit_strategy(self, user_id: str, patterns: Dict[str, Any]):
        """Adjust habit formation strategy based on patterns"""
        adjustments = {
            "reminder_times": self.optimize_reminder_times(patterns["peak_activity_times"]),
            "trigger_frequency": self.optimize_trigger_frequency(patterns["engagement_frequency"]),
            "motivation_type": self.determine_motivation_type(patterns)
        }

        await self.send_message(
            "motivation_mapping",
            {
                "type": "habit_adjustment",
                "user_id": user_id,
                "adjustments": adjustments
            }
        )

    def calculate_peak_times(self, activities: List[Dict[str, Any]]) -> List[int]:
        """Calculate peak activity times"""
        hour_counts = [0] * 24
        for activity in activities:
            hour = activity["timestamp"].hour
            hour_counts[hour] += 1
        return [i for i, count in enumerate(hour_counts) if count > sum(hour_counts)/24]

    def calculate_frequency(self, activities: List[Dict[str, Any]]) -> float:
        """Calculate average engagement frequency"""
        if not activities:
            return 0.0
        
        time_diffs = []
        sorted_activities = sorted(activities, key=lambda x: x["timestamp"])
        for i in range(1, len(sorted_activities)):
            diff = sorted_activities[i]["timestamp"] - sorted_activities[i-1]["timestamp"]
            time_diffs.append(diff.total_seconds())
        
        return sum(time_diffs) / len(time_diffs) if time_diffs else 0.0

    def calculate_streak_sustainability(self, streak: Dict[str, Any]) -> float:
        """Calculate streak sustainability score"""
        if not streak:
            return 0.0
        
        weights = {"daily": 0.5, "weekly": 0.3, "contribution": 0.2}
        score = 0.0
        
        for streak_type, weight in weights.items():
            streak_value = streak.get(streak_type, 0)
            score += (streak_value * weight)
            
        return min(1.0, score / 100)  # Normalize to 0-1

    def needs_optimization(self, patterns: Dict[str, Any]) -> bool:
        """Determine if habit strategy needs optimization"""
        return (patterns["streak_sustainability"] < 0.5 or
                len(patterns["peak_activity_times"]) < 2 or
                patterns["engagement_frequency"] > 172800)  # 48 hours in seconds

    def optimize_reminder_times(self, peak_times: List[int]) -> List[int]:
        """Optimize reminder timing"""
        if not peak_times:
            return [9, 15, 20]  # Default times
        return sorted(peak_times)

    def optimize_trigger_frequency(self, engagement_frequency: float) -> timedelta:
        """Optimize trigger frequency"""
        if engagement_frequency <= 86400:  # 24 hours
            return timedelta(hours=12)
        elif engagement_frequency <= 172800:  # 48 hours
            return timedelta(days=1)
        else:
            return timedelta(days=2)

    def determine_motivation_type(self, patterns: Dict[str, Any]) -> str:
        """Determine best motivation type based on patterns"""
        if patterns["streak_sustainability"] > 0.7:
            return "achievement"
        elif patterns["engagement_frequency"] < 86400:
            return "consistency"
        else:
            return "recovery"

    async def check_streak_achievements(self, user_id: str, streak: Dict[str, Any]):
        """Check and process streak achievements"""
        achievements = []
        
        if streak["daily"] in [7, 30, 100]:
            achievements.append({"type": "daily_streak", "value": streak["daily"]})
        
        if streak["weekly"] in [4, 12, 52]:
            achievements.append({"type": "weekly_streak", "value": streak["weekly"]})
        
        if streak["contribution"] in [5, 20, 50]:
            achievements.append({"type": "contribution_streak", "value": streak["contribution"]})
            
        for achievement in achievements:
            await self.send_message(
                "feedback_loop",
                {
                    "type": "streak_achievement",
                    "user_id": user_id,
                    "achievement": achievement
                }
            )

    def is_consecutive_day(self, last_time: datetime, current_time: datetime) -> bool:
        """Check if two timestamps are on consecutive days"""
        diff = current_time.date() - last_time.date()
        return diff.days == 1

    def is_same_week(self, last_time: datetime, current_time: datetime) -> bool:
        """Check if two timestamps are in the same week"""
        return last_time.isocalendar()[1] == current_time.isocalendar()[1]

    def is_within_days(self, last_time: datetime, current_time: datetime, days: int) -> bool:
        """Check if two timestamps are within specified days"""
        return (current_time - last_time) <= timedelta(days=days)

    def should_send_reminder(self, streak: Dict[str, Any], trigger: Dict[str, Any], current_time: datetime) -> bool:
        """Determine if reminder should be sent"""
        if not streak["last_activity"]:
            return True
            
        time_since_last = current_time - streak["last_activity"]
        return time_since_last >= trigger["interval"]

    async def send_reminder(self, user_id: str, trigger_type: str, streak: Dict[str, Any]):
        """Send habit reminder to user"""
        trigger = self.habit_triggers[trigger_type]
        message = trigger["reminder_template"].format(
            streak_count=streak.get(trigger_type, 0),
            last_contribution=streak.get("last_activity", "never")
        )
        
        await self.send_message(
            "feedback_loop",
            {
                "type": "habit_reminder",
                "user_id": user_id,
                "message": message,
                "trigger_type": trigger_type
            }
        )

    async def get_active_users(self) -> List[str]:
        """Get list of active users"""
        # Implementation would fetch from database
        return []

    async def get_user_activities(self, user_id: str) -> List[Dict[str, Any]]:
        """Get recent user activities"""
        # Implementation would fetch from database
        return []

    async def cleanup(self):
        """Cleanup agent resources"""
        self.logger.info("Cleaning up Habit Formation Agent")
        # Save current state
        await self.save_state()

    async def save_state(self):
        """Save current state to persistent storage"""
        # Implementation would save to database
        pass

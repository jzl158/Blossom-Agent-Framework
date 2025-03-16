from typing import Dict, Any, List
from .base_agent import BaseAgent
import logging
from datetime import datetime

class FeedbackLoopAgent(BaseAgent):
    def __init__(self):
        super().__init__("feedback_loop")
        self.feedback_queue = []
        self.notification_templates = {}
        self.user_preferences = {}

    async def initialize(self):
        self.logger.info("Initializing Feedback Loop Agent")
        await self.load_notification_templates()
        await self.load_user_preferences()

    async def process_cycle(self):
        try:
            # Process pending feedback
            await self.process_feedback_queue()
            # Generate periodic feedback
            await self.generate_periodic_feedback()
            # Process peer recognition
            await self.process_peer_recognition()
        except Exception as e:
            self.logger.error(f"Error in feedback loop cycle: {e}")

    async def load_notification_templates(self):
        """Load notification templates"""
        self.notification_templates = {
            "achievement": {
                "title": "Achievement Unlocked!",
                "template": "Congratulations! You've earned {achievement_name}"
            },
            "milestone": {
                "title": "Milestone Reached",
                "template": "You've reached {milestone_name}! Keep up the great work!"
            },
            "streak": {
                "title": "Streak Alert",
                "template": "You're on a {streak_count} day streak!"
            },
            "recognition": {
                "title": "Community Recognition",
                "template": "{user} appreciated your contribution: {contribution}"
            }
        }

    async def send_notification(self, user_id: str, notification_type: str, data: Dict[str, Any]):
        """Send notification to user"""
        if notification_type not in self.notification_templates:
            raise ValueError(f"Invalid notification type: {notification_type}")

        template = self.notification_templates[notification_type]
        notification = {
            "user_id": user_id,
            "title": template["title"],
            "message": template["template"].format(**data),
            "timestamp": datetime.now(),
            "type": notification_type,
            "data": data
        }

        # Add to feedback queue
        self.feedback_queue.append(notification)

    async def process_feedback_queue(self):
        """Process pending notifications in queue"""
        while self.feedback_queue:
            notification = self.feedback_queue.pop(0)
            try:
                # Check user preferences
                if self.should_send_notification(notification):
                    await self.deliver_notification(notification)
            except Exception as e:
                self.logger.error(f"Error processing notification: {e}")
                # Put back in queue for retry
                self.feedback_queue.append(notification)

    def should_send_notification(self, notification: Dict[str, Any]) -> bool:
        """Check if notification should be sent based on user preferences"""
        user_id = notification["user_id"]
        if user_id not in self.user_preferences:
            return True  # Default to sending if no preferences set

        prefs = self.user_preferences[user_id]
        notification_type = notification["type"]

        # Check if notification type is enabled
        if not prefs.get(f"enable_{notification_type}", True):
            return False

        # Check frequency limits
        last_notification = prefs.get("last_notification_time", {}).get(notification_type)
        if last_notification:
            time_diff = datetime.now() - last_notification
            min_interval = prefs.get("notification_interval", 300)  # 5 minutes default
            if time_diff.total_seconds() < min_interval:
                return False

        return True

    async def deliver_notification(self, notification: Dict[str, Any]):
        """Deliver notification to user"""
        try:
            # Implementation would integrate with notification service
            self.logger.info(f"Delivering notification to user {notification['user_id']}")
            
            # Update user's last notification time
            user_id = notification["user_id"]
            if user_id in self.user_preferences:
                self.user_preferences[user_id].setdefault("last_notification_time", {})[notification["type"]] = datetime.now()
        except Exception as e:
            self.logger.error(f"Failed to deliver notification: {e}")
            raise

    async def generate_periodic_feedback(self):
        """Generate periodic feedback for users"""
        try:
            active_users = await self.get_active_users()
            for user_id in active_users:
                stats = await self.get_user_stats(user_id)
                if stats["needs_feedback"]:
                    await self.generate_user_feedback(user_id, stats)
        except Exception as e:
            self.logger.error(f"Error generating periodic feedback: {e}")

    async def process_peer_recognition(self):
        """Process peer recognition events"""
        try:
            recognition_events = await self.get_pending_recognition_events()
            for event in recognition_events:
                await self.send_notification(
                    event["recipient_id"],
                    "recognition",
                    {
                        "user": event["sender_name"],
                        "contribution": event["contribution"]
                    }
                )
        except Exception as e:
            self.logger.error(f"Error processing peer recognition: {e}")

    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics for feedback generation"""
        # Implementation would fetch from database
        return {"needs_feedback": False}

    async def get_pending_recognition_events(self) -> List[Dict[str, Any]]:
        """Get pending peer recognition events"""
        # Implementation would fetch from database
        return []

    async def get_active_users(self) -> List[str]:
        """Get list of active users"""
        # Implementation would fetch from database
        return []

    async def load_user_preferences(self):
        """Load user notification preferences"""
        # Implementation would load from database
        pass

    async def cleanup(self):
        """Cleanup agent resources"""
        self.logger.info("Cleaning up Feedback Loop Agent")
        # Save any pending notifications
        await self.save_pending_notifications()

    async def save_pending_notifications(self):
        """Save pending notifications to persistent storage"""
        # Implementation would save to database
        pass

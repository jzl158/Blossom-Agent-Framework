from abc import ABC, abstractmethod
import logging
from typing import Dict, Any
import asyncio
from data.models import EngagementMetrics

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"agent.{name}")
        self.running = False
        self.metrics = EngagementMetrics()
        
    async def start(self):
        """Start the agent's main loop"""
        self.running = True
        try:
            await self.initialize()
            while self.running:
                await self.process_cycle()
                await asyncio.sleep(1)  # Prevent CPU hogging
        except Exception as e:
            self.logger.error(f"Agent {self.name} error: {e}")
            raise

    async def stop(self):
        """Stop the agent"""
        self.running = False
        await self.cleanup()

    @abstractmethod
    async def initialize(self):
        """Initialize agent-specific resources"""
        pass

    @abstractmethod
    async def process_cycle(self):
        """Main processing loop for the agent"""
        pass

    @abstractmethod
    async def cleanup(self):
        """Cleanup agent resources"""
        pass

    async def send_message(self, target_agent: str, message: Dict[str, Any]):
        """Send message to another agent"""
        self.logger.debug(f"Sending message to {target_agent}: {message}")
        # Message bus implementation would go here
        pass

    def update_metrics(self, metric_name: str, value: float):
        """Update agent metrics"""
        self.metrics.update(metric_name, value)

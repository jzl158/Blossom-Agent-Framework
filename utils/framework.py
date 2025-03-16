import logging
from typing import Dict, Any, List
from datetime import datetime
from utils.agent_manager import AgentManager
from utils.display import DisplayManager
from utils.progress import ProgressTracker
from data.cache import EngagementCache
from graph.state_manager import StateManager
from llm.providers import LLMProviderManager

class Framework:
    def __init__(self):
        self.logger = logging.getLogger("framework")
        self.agent_manager = AgentManager()
        self.display_manager = DisplayManager()
        self.progress_tracker = ProgressTracker()
        self.cache = EngagementCache()
        self.state_manager = StateManager()
        self.llm_manager = LLMProviderManager()
        self.metrics = {}
        
    async def initialize(self):
        """Initialize framework components"""
        try:
            self.logger.info("Initializing Skylark Framework")
            
            # Initialize components
            await self.agent_manager.initialize()
            await self.display_manager.initialize()
            await self.progress_tracker.initialize()
            
            # Load initial states
            await self.load_states()
            
            self.logger.info("Framework initialization complete")
            
        except Exception as e:
            self.logger.error(f"Framework initialization failed: {e}")
            raise

    async def load_states(self):
        """Load saved states for all components"""
        try:
            # Load agent states
            agent_states = await self.state_manager.load_state("agents")
            if agent_states:
                await self.agent_manager.restore_state(agent_states)
            
            # Load progress state
            progress_state = await self.state_manager.load_state("progress")
            if progress_state:
                await self.progress_tracker.restore_state(progress_state)
                
        except Exception as e:
            self.logger.error(f"Failed to load states: {e}")

    async def start(self):
        """Start framework operation"""
        try:
            self.logger.info("Starting Skylark Framework")
            
            # Start agents
            await self.agent_manager.start_agents()
            
            # Start monitoring
            await self.start_monitoring()
            
            self.logger.info("Framework started successfully")
            
        except Exception as e:
            self.logger.error(f"Framework start failed: {e}")
            raise

    async def stop(self):
        """Stop framework operation"""
        try:
            self.logger.info("Stopping Skylark Framework")
            
            # Stop agents
            await self.agent_manager.stop_agents()
            
            # Save states
            await self.save_states()
            
            self.logger.info("Framework stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Framework stop failed: {e}")
            raise

    async def save_states(self):
        """Save states for all components"""
        try:
            # Save agent states
            agent_states = await self.agent_manager.get_states()
            await self.state_manager.save_state("agents", agent_states)
            
            # Save progress state
            progress_state = await self.progress_tracker.get_state()
            await self.state_manager.save_state("progress", progress_state)
            
        except Exception as e:
            self.logger.error(f"Failed to save states: {e}")

    async def start_monitoring(self):
        """Start monitoring framework metrics"""
        try:
            # Monitor agent performance
            agent_metrics = await self.agent_manager.get_metrics()
            self.metrics["agents"] = agent_metrics
            
            # Monitor progress
            progress_metrics = await self.progress_tracker.get_metrics()
            self.metrics["progress"] = progress_metrics
            
            # Monitor cache
            cache_metrics = self.cache.get_metrics()
            self.metrics["cache"] = cache_metrics
            
            # Update display
            await self.display_manager.update_metrics(self.metrics)
            
        except Exception as e:
            self.logger.error(f"Monitoring update failed: {e}")

    async def process_event(self, event: Dict[str, Any]):
        """Process framework event"""
        try:
            event_type = event.get("type")
            if not event_type:
                raise ValueError("Event type not specified")
                
            if event_type == "agent_event":
                await self.agent_manager.process_event(event)
            elif event_type == "progress_event":
                await self.progress_tracker.process_event(event)
            elif event_type == "display_event":
                await self.display_manager.process_event(event)
            else:
                self.logger.warning(f"Unknown event type: {event_type}")
                
        except Exception as e:
            self.logger.error(f"Event processing failed: {e}")
            raise

    def get_stats(self) -> Dict[str, Any]:
        """Get framework statistics"""
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": self.metrics,
            "agents": {
                "total": self.agent_manager.get_agent_count(),
                "active": self.agent_manager.get_active_agent_count()
            },
            "cache": {
                "size": len(self.cache.get_metrics()),
                "hit_rate": self.cache.get_metrics().get("hit_rate", 0)
            },
            "llm": {
                "providers": self.llm_manager.get_available_providers()
            }
        }

    async def update_configuration(self, config: Dict[str, Any]):
        """Update framework configuration"""
        try:
            # Update agent configuration
            if "agents" in config:
                await self.agent_manager.update_configuration(config["agents"])
                
            # Update progress tracking
            if "progress" in config:
                await self.progress_tracker.update_configuration(config["progress"])
                
            # Update display
            if "display" in config:
                await self.display_manager.update_configuration(config["display"])
                
            # Save new configuration state
            await self.state_manager.save_state("config", config)
            
        except Exception as e:
            self.logger.error(f"Configuration update failed: {e}")
            raise


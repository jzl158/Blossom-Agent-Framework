import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

class AgentManager:
    def __init__(self):
        self.logger = logging.getLogger("agent_manager")
        self.agents = {}
        self.active_agents = set()
        self.agent_metrics = {}
        
    async def initialize(self):
        """Initialize agent manager"""
        self.logger.info("Initializing Agent Manager")
        await self.load_configurations()
        
    async def load_configurations(self):
        """Load agent configurations"""
        # Implementation would load from config file or database
        pass
        
    async def start_agents(self):
        """Start all registered agents"""
        self.logger.info("Starting agents")
        for agent_id in self.agents:
            await self.start_agent(agent_id)
            
    async def stop_agents(self):
        """Stop all active agents"""
        self.logger.info("Stopping agents")
        for agent_id in list(self.active_agents):
            await self.stop_agent(agent_id)
            
    async def start_agent(self, agent_id: str):
        """Start specific agent"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
            
        agent = self.agents[agent_id]
        await agent.initialize()
        self.active_agents.add(agent_id)
        self.logger.info(f"Started agent: {agent_id}")
            
    async def stop_agent(self, agent_id: str):
        """Stop specific agent"""
        if agent_id not in self.active_agents:
            return
            
        agent = self.agents[agent_id]
        await agent.cleanup()
        self.active_agents.remove(agent_id)
        self.logger.info(f"Stopped agent: {agent_id}")
        
    async def register_agent(self, agent_id: str, agent: Any):
        """Register new agent"""
        if agent_id in self.agents:
            raise ValueError(f"Agent {agent_id} already registered")
            
        self.agents[agent_id] = agent
        self.logger.info(f"Registered agent: {agent_id}")
        
    async def get_agent(self, agent_id: str) -> Optional[Any]:
        """Get registered agent"""
        return self.agents.get(agent_id)
        
    def get_agent_count(self) -> int:
        """Get total number of registered agents"""
        return len(self.agents)
        
    def get_active_agent_count(self) -> int:
        """Get number of active agents"""
        return len(self.active_agents)
        
    async def process_event(self, event: Dict[str, Any]):
        """Process agent-related event"""
        event_type = event.get("type")
        agent_id = event.get("agent_id")
        
        if not agent_id or agent_id not in self.agents:
            return
            
        agent = self.agents[agent_id]
        if event_type == "start":
            await self.start_agent(agent_id)
        elif event_type == "stop":
            await self.stop_agent(agent_id)
        elif event_type == "update":
            await agent.process_cycle()
            
    async def get_metrics(self) -> Dict[str, Any]:
        """Get agent metrics"""
        metrics = {
            "total_agents": self.get_agent_count(),
            "active_agents": self.get_active_agent_count(),
            "agent_statuses": {}
        }
        
        for agent_id, agent in self.agents.items():
            metrics["agent_statuses"][agent_id] = {
                "active": agent_id in self.active_agents,
                "last_update": self.agent_metrics.get(agent_id, {}).get("last_update")
            }
            
        return metrics
        
    async def update_metrics(self, agent_id: str, metrics: Dict[str, Any]):
        """Update agent metrics"""
        self.agent_metrics[agent_id] = {
            **metrics,
            "last_update": datetime.now().isoformat()
        }
        
    async def get_states(self) -> Dict[str, Any]:
        """Get states of all agents"""
        states = {}
        for agent_id, agent in self.agents.items():
            states[agent_id] = await agent.get_state()
        return states
        
    async def restore_state(self, states: Dict[str, Any]):
        """Restore agent states"""
        for agent_id, state in states.items():
            if agent_id in self.agents:
                await self.agents[agent_id].restore_state(state)
                
    async def update_configuration(self, config: Dict[str, Any]):
        """Update agent configurations"""
        for agent_id, agent_config in config.items():
            if agent_id in self.agents:
                await self.agents[agent_id].update_configuration(agent_config)

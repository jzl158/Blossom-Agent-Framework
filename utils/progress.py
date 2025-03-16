import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

class ProgressTracker:
    def __init__(self):
        self.logger = logging.getLogger("progress_tracker")
        self.progress_metrics = {}
        self.progress_history = []
        self.progress_config = {}
        
    async def initialize(self):
        """Initialize progress tracker"""
        self.logger.info("Initializing Progress Tracker")
        await self.load_progress_config()
        
    async def load_progress_config(self):
        """Load progress tracking configuration"""
        # Implementation would load from config file or database
        pass
        
    async def update_progress(self, category: str, metrics: Dict[str, Any]):
        """Update progress metrics for category"""
        try:
            timestamp = datetime.now().isoformat()
            
            if category not in self.progress_metrics:
                self.progress_metrics[category] = []
                
            progress_entry = {
                "metrics": metrics,
                "timestamp": timestamp
            }
            
            self.progress_metrics[category].append(progress_entry)
            self.progress_history.append({
                "category": category,
                **progress_entry
            })
            
            await self.trim_history()
            
        except Exception as e:
            self.logger.error(f"Failed to update progress: {e}")
            
    async def get_progress(self, category: str) -> List[Dict[str, Any]]:
        """Get progress history for category"""
        return self.progress_metrics.get(category, [])
        
    async def get_latest_progress(self, category: str) -> Optional[Dict[str, Any]]:
        """Get latest progress entry for category"""
        progress = self.progress_metrics.get(category, [])
        return progress[-1] if progress else None
        
    async def process_event(self, event: Dict[str, Any]):
        """Process progress-related event"""
        try:
            event_type = event.get("type")
            
            if event_type == "progress_update":
                category = event.get("category")
                metrics = event.get("metrics")
                if category and metrics:
                    await self.update_progress(category, metrics)
                    
        except Exception as e:
            self.logger.error(f"Failed to process progress event: {e}")
            
    async def get_metrics(self) -> Dict[str, Any]:
        """Get progress tracking metrics"""
        metrics = {
            "categories": len(self.progress_metrics),
            "total_updates": len(self.progress_history),
            "latest_updates": {}
        }
        
        for category in self.progress_metrics:
            latest = await self.get_latest_progress(category)
            if latest:
                metrics["latest_updates"][category] = latest
                
        return metrics
        
    async def trim_history(self, max_entries: int = 1000):
        """Trim progress history to prevent memory growth"""
        for category in self.progress_metrics:
            if len(self.progress_metrics[category]) > max_entries:
                self.progress_metrics[category] = self.progress_metrics[category][-max_entries:]
                
        if len(self.progress_history) > max_entries:
            self.progress_history = self.progress_history[-max_entries:]
            
    async def clear_progress(self, category: Optional[str] = None):
        """Clear progress data"""
        if category:
            self.progress_metrics.pop(category, None)
        else:
            self.progress_metrics = {}
            self.progress_history = []
            
    async def get_state(self) -> Dict[str, Any]:
        """Get current progress state"""
        return {
            "metrics": self.progress_metrics,
            "history": self.progress_history,
            "config": self.progress_config
        }
        
    async def restore_state(self, state: Dict[str, Any]):
        """Restore progress state"""
        self.progress_metrics = state.get("metrics", {})
        self.progress_history = state.get("history", [])
        self.progress_config = state.get("config", {})
        
    async def update_configuration(self, config: Dict[str, Any]):
        """Update progress tracking configuration"""
        self.progress_config.update(config)

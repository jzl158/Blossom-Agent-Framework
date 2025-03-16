from typing import Dict, Any, List
from .base_agent import BaseAgent
import logging
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from utils.visualization import EngagementVisualizer

class AnalyticsAgent(BaseAgent):
    def __init__(self):
        super().__init__("analytics")
        self.metrics_history = {}
        self.visualizer = EngagementVisualizer()
        self.analysis_cache = {}
        
    async def initialize(self):
        self.logger.info("Initializing Analytics Agent")
        await self.load_historical_metrics()
        
    async def process_cycle(self):
        try:
            # Collect metrics
            await self.collect_metrics()
            # Analyze trends
            await self.analyze_trends()
            # Generate insights
            await self.generate_insights()
            # Update visualizations
            await self.update_visualizations()
        except Exception as e:
            self.logger.error(f"Error in analytics cycle: {e}")

    async def collect_metrics(self):
        """Collect metrics from all agents"""
        metrics = {}
        agent_types = [
            "motivation_mapping",
            "goal_setting",
            "behavior_monitoring",
            "social_dynamics",
            "emotional_anchoring",
            "habit_formation",
            "evolution"
        ]
        
        for agent_type in agent_types:
            agent_metrics = await self.get_agent_metrics(agent_type)
            metrics[agent_type] = agent_metrics
            
        timestamp = datetime.now()
        self.metrics_history[timestamp] = metrics

    async def analyze_trends(self):
        """Analyze metric trends and patterns"""
        try:
            df = self.create_metrics_dataframe()
            trends = {
                "engagement": self.analyze_engagement_trends(df),
                "retention": self.analyze_retention_trends(df),
                "social": self.analyze_social_trends(df),
                "habits": self.analyze_habit_trends(df)
            }
            
            self.analysis_cache["trends"] = trends
            await self.broadcast_trends(trends)
        except Exception as e:
            self.logger.error(f"Error analyzing trends: {e}")

    def create_metrics_dataframe(self) -> pd.DataFrame:
        """Create DataFrame from metrics history"""
        data = []
        for timestamp, metrics in self.metrics_history.items():
            row = {"timestamp": timestamp}
            for agent_type, agent_metrics in metrics.items():
                for metric_name, value in agent_metrics.items():
                    row[f"{agent_type}_{metric_name}"] = value
            data.append(row)
            
        return pd.DataFrame(data)

    def analyze_engagement_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze engagement metric trends"""
        engagement_cols = [col for col in df.columns if "engagement" in col]
        if not engagement_cols:
            return {}
            
        trends = {
            "overall_trend": self.calculate_trend(df[engagement_cols].mean(axis=1)),
            "peak_times": self.identify_peak_times(df[engagement_cols]),
            "engagement_patterns": self.identify_patterns(df[engagement_cols])
        }
        
        return trends

    def analyze_retention_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze user retention trends"""
        retention_cols = [col for col in df.columns if "retention" in col]
        if not retention_cols:
            return {}
            
        trends = {
            "retention_rate": self.calculate_retention_rate(df[retention_cols]),
            "churn_risk": self.identify_churn_risk(df[retention_cols]),
            "retention_factors": self.identify_retention_factors(df)
        }
        
        return trends

    def analyze_social_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze social interaction trends"""
        social_cols = [col for col in df.columns if "social" in col]
        if not social_cols:
            return {}
            
        trends = {
            "interaction_rate": self.calculate_interaction_rate(df[social_cols]),
            "community_growth": self.calculate_community_growth(df[social_cols]),
            "social_patterns": self.identify_social_patterns(df[social_cols])
        }
        
        return trends

    def analyze_habit_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze habit formation trends"""
        habit_cols = [col for col in df.columns if "habit" in col]
        if not habit_cols:
            return {}
            
        trends = {
            "habit_strength": self.calculate_habit_strength(df[habit_cols]),
            "consistency": self.calculate_consistency(df[habit_cols]),
            "habit_patterns": self.identify_habit_patterns(df[habit_cols])
        }
        
        return trends

    def calculate_trend(self, series: pd.Series) -> float:
        """Calculate trend direction and strength"""
        if len(series) < 2:
            return 0.0
            
        x = np.arange(len(series))
        y = series.values
        z = np.polyfit(x, y, 1)
        return z[0]  # Return slope

    def identify_peak_times(self, df: pd.DataFrame) -> List[int]:
        """Identify peak engagement times"""
        if df.empty:
            return []
            
        hourly_means = df.groupby(df.index.hour).mean()
        threshold = hourly_means.mean() + hourly_means.std()
        peak_hours = hourly_means[hourly_means > threshold].index.tolist()
        
        return peak_hours

    def identify_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identify patterns in metrics"""
        if df.empty:
            return {}
            
        patterns = {
            "weekly": self.analyze_weekly_pattern(df),
            "monthly": self.analyze_monthly_pattern(df),
            "correlation": self.analyze_metric_correlation(df)
        }
        
        return patterns

    async def generate_insights(self):
        """Generate actionable insights from trends"""
        if "trends" not in self.analysis_cache:
            return
            
        trends = self.analysis_cache["trends"]
        insights = {
            "critical_insights": self.identify_critical_insights(trends),
            "opportunities": self.identify_opportunities(trends),
            "recommendations": self.generate_recommendations(trends)
        }
        
        await self.broadcast_insights(insights)

    def identify_critical_insights(self, trends: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify critical insights from trends"""
        insights = []
        
        # Engagement insights
        if "engagement" in trends:
            engagement_trend = trends["engagement"].get("overall_trend", 0)
            if engagement_trend < 0:
                insights.append({
                    "type": "warning",
                    "area": "engagement",
                    "message": "Declining engagement trend detected",
                    "severity": "high"
                })
                
        # Retention insights
        if "retention" in trends:
            churn_risk = trends["retention"].get("churn_risk", 0)
            if churn_risk > 0.6:
                insights.append({
                    "type": "alert",
                    "area": "retention",
                    "message": "High churn risk detected",
                    "severity": "critical"
                })
                
        return insights

    def identify_opportunities(self, trends: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify improvement opportunities"""
        opportunities = []
        
        if "social" in trends:
            interaction_rate = trends["social"].get("interaction_rate", 0)
            if interaction_rate > 0.7:
                opportunities.append({
                    "area": "social",
                    "type": "expansion",
                    "message": "High social engagement - consider expanding social features"
                })
                
        if "habits" in trends:
            habit_strength = trends["habits"].get("habit_strength", 0)
            if habit_strength > 0.8:
                opportunities.append({
                    "area": "habits",
                    "type": "enhancement",
                    "message": "Strong habit formation - consider advanced engagement features"
                })
                
        return opportunities

    def generate_recommendations(self, trends: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Engagement recommendations
        if "engagement" in trends:
            peak_times = trends["engagement"].get("peak_times", [])
            if peak_times:
                recommendations.append({
                    "area": "engagement",
                    "action": "timing_optimization",
                    "message": f"Optimize content delivery for peak times: {peak_times}"
                })
                
        # Retention recommendations
        if "retention" in trends:
            retention_factors = trends["retention"].get("retention_factors", {})
            if retention_factors:
                top_factor = max(retention_factors.items(), key=lambda x: x[1])[0]
                recommendations.append({
                    "area": "retention",
                    "action": "factor_enhancement",
                    "message": f"Focus on enhancing {top_factor} to improve retention"
                })
                
        return recommendations

    async def update_visualizations(self):
        """Update engagement visualizations"""
        try:
            df = self.create_metrics_dataframe()
            
            # Create timeline visualization
            timeline_data = {
                "engagement": df[[col for col in df.columns if "engagement" in col]].mean(axis=1),
                "retention": df[[col for col in df.columns if "retention" in col]].mean(axis=1)
            }
            timeline_viz = self.visualizer.create_engagement_timeline(timeline_data)
            
            # Create heatmap visualization
            heatmap_data = df[[col for col in df.columns if any(x in col for x in ["engagement", "social", "habit"])]].corr()
            heatmap_viz = self.visualizer.create_engagement_heatmap(heatmap_data)
            
            await self.broadcast_visualizations({
                "timeline": timeline_viz,
                "heatmap": heatmap_viz
            })
            
        except Exception as e:
            self.logger.error(f"Error updating visualizations: {e}")

    async def broadcast_trends(self, trends: Dict[str, Any]):
        """Broadcast trend analysis to other agents"""
        await self.send_message(
            "evolution",
            {
                "type": "trend_analysis",
                "trends": trends
            }
        )

    async def broadcast_insights(self, insights: Dict[str, Any]):
        """Broadcast insights to other agents"""
        await self.send_message(
            "agent_manager",
            {
                "type": "analytics_insights",
                "insights": insights
            }
        )

    async def broadcast_visualizations(self, visualizations: Dict[str, str]):
        """Broadcast visualizations to display system"""
        await self.send_message(
            "display",
            {
                "type": "visualization_update",
                "visualizations": visualizations
            }
        )

    async def get_agent_metrics(self, agent_type: str) -> Dict[str, Any]:
        """Get metrics from specific agent"""
        # Implementation would fetch metrics from agent
        return {}

    async def load_historical_metrics(self):
        """Load historical metrics data"""
        # Implementation would load from database
        pass

    async def cleanup(self):
        """Cleanup agent resources"""
        self.logger.info("Cleaning up Analytics Agent")
        # Save current state
        await self.save_state()

    async def save_state(self):
        """Save current state to persistent storage"""
        # Implementation would save to database
        pass

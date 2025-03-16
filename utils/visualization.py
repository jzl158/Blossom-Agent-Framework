import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List
import pandas as pd
from io import BytesIO
import base64

class EngagementVisualizer:
    def __init__(self):
        # Set style
        plt.style.use('seaborn-darkgrid')
        sns.set_palette("husl")

    def create_engagement_timeline(self, 
                                 data: Dict[str, List[float]], 
                                 title: str = "Engagement Timeline") -> str:
        """Create engagement metrics timeline visualization"""
        plt.figure(figsize=(12, 6))
        
        df = pd.DataFrame(data)
        for column in df.columns:
            plt.plot(df.index, df[column], label=column, marker='o')
            
        plt.title(title)
        plt.xlabel("Time")
        plt.ylabel("Engagement Score")
        plt.legend()
        plt.grid(True)
        
        # Convert plot to base64 string
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        
        return base64.b64encode(image_png).decode()

    def create_motivation_radar(self, 
                              motivators: Dict[str, float], 
                              title: str = "Motivation Profile") -> str:
        """Create radar chart of motivation factors"""
        # Prepare data
        categories = list(motivators.keys())
        values = list(motivators.values())
        
        # Create radar chart
        angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False)
        values = np.concatenate((values, [values[0]]))  # complete the circle
        angles = np.concatenate((angles, [angles[0]]))  # complete the circle
        
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
        ax.plot(angles, values)
        ax.fill(angles, values, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        plt.title(title)
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        
        return base64.b64encode(image_png).decode()

    def create_engagement_heatmap(self, 
                                data: pd.DataFrame, 
                                title: str = "Engagement Heatmap") -> str:
        """Create heatmap of engagement patterns"""
        plt.figure(figsize=(10, 8))
        sns.heatmap(data, annot=True, cmap='YlOrRd', fmt='.2f')
        plt.title(title)
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        
        return base64.b64encode(image_png).decode()

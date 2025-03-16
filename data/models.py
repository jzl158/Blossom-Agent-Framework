from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List
import json
import sqlite3
import os

def init_db():
    """Initialize database tables"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
    CREATE TABLE IF NOT EXISTS user_profiles (
        user_id TEXT PRIMARY KEY,
        motivators TEXT,
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    )''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS engagement_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        metric_name TEXT,
        value REAL,
        timestamp TIMESTAMP
    )''')

    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection"""
    db_path = os.path.join(os.path.dirname(__file__), 'engagement.db')
    return sqlite3.connect(db_path)

@dataclass
class UserProfile:
    user_id: str
    motivators: Dict[str, float]
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    @classmethod
    async def load_all(cls) -> Dict[str, 'UserProfile']:
        """Load all user profiles from database"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        profiles = {}
        for row in cur.execute('SELECT * FROM user_profiles'):
            profiles[row[0]] = cls(
                user_id=row[0],
                motivators=json.loads(row[1]),
                created_at=datetime.fromisoformat(row[2]),
                updated_at=datetime.fromisoformat(row[3])
            )
        
        conn.close()
        return profiles

    async def save(self):
        """Save profile to database"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        self.updated_at = datetime.now()
        cur.execute('''
        INSERT OR REPLACE INTO user_profiles (user_id, motivators, created_at, updated_at)
        VALUES (?, ?, ?, ?)
        ''', (
            self.user_id,
            json.dumps(self.motivators),
            self.created_at.isoformat(),
            self.updated_at.isoformat()
        ))
        
        conn.commit()
        conn.close()

    def update_motivators(self, new_motivators: Dict[str, float]):
        """Update motivation factors"""
        self.motivators.update(new_motivators)
        self.updated_at = datetime.now()

@dataclass
class EngagementMetrics:
    metrics: Dict[str, List[float]] = None
    
    def __init__(self):
        self.metrics = {}
    
    def update(self, metric_name: str, value: float):
        """Update metric value"""
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        self.metrics[metric_name].append(value)
        
        # Store in database
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
        INSERT INTO engagement_metrics (metric_name, value, timestamp)
        VALUES (?, ?, ?)
        ''', (metric_name, value, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()

    def get_metric_average(self, metric_name: str) -> float:
        """Get average value for a metric"""
        if metric_name in self.metrics and self.metrics[metric_name]:
            return sum(self.metrics[metric_name]) / len(self.metrics[metric_name])
        return 0.0

import json
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
import logging
from pathlib import Path
import sqlite3

class EngagementCache:
    def __init__(self, cache_duration: int = 3600):
        self.logger = logging.getLogger("engagement_cache")
        self.cache_duration = cache_duration  # Cache duration in seconds
        self.cache_path = Path("data/cache.db")
        self.initialize_cache()

    def initialize_cache(self):
        """Initialize cache database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Create cache table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS engagement_cache (
                key TEXT PRIMARY KEY,
                value TEXT,
                timestamp DATETIME,
                expiry DATETIME
            )
            ''')
            
            conn.commit()
        except Exception as e:
            self.logger.error(f"Failed to initialize cache: {e}")
        finally:
            conn.close()

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        return sqlite3.connect(self.cache_path)

    def set(self, key: str, value: Any, expiry: Optional[int] = None):
        """Set cache value with expiration"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            now = datetime.now()
            expiry_time = now + timedelta(seconds=expiry or self.cache_duration)
            
            cursor.execute('''
            INSERT OR REPLACE INTO engagement_cache (key, value, timestamp, expiry)
            VALUES (?, ?, ?, ?)
            ''', (key, json.dumps(value), now.isoformat(), expiry_time.isoformat()))
            
            conn.commit()
        except Exception as e:
            self.logger.error(f"Failed to set cache value: {e}")
        finally:
            conn.close()

    def get(self, key: str) -> Optional[Any]:
        """Get cache value if not expired"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT value, expiry FROM engagement_cache 
            WHERE key = ? AND datetime('now') < datetime(expiry)
            ''', (key,))
            
            result = cursor.fetchone()
            if result:
                return json.loads(result[0])
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get cache value: {e}")
            return None
        finally:
            conn.close()

    def delete(self, key: str):
        """Delete cache entry"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM engagement_cache WHERE key = ?', (key,))
            conn.commit()
            
        except Exception as e:
            self.logger.error(f"Failed to delete cache entry: {e}")
        finally:
            conn.close()

    def clear_expired(self):
        """Clear expired cache entries"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            DELETE FROM engagement_cache 
            WHERE datetime('now') >= datetime(expiry)
            ''')
            
            conn.commit()
        except Exception as e:
            self.logger.error(f"Failed to clear expired cache: {e}")
        finally:
            conn.close()

    def get_metrics(self) -> Dict[str, Any]:
        """Get cache metrics"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get total entries
            cursor.execute('SELECT COUNT(*) FROM engagement_cache')
            total = cursor.fetchone()[0]
            
            # Get expired entries
            cursor.execute('''
            SELECT COUNT(*) FROM engagement_cache 
            WHERE datetime('now') >= datetime(expiry)
            ''')
            expired = cursor.fetchone()[0]
            
            return {
                "total_entries": total,
                "expired_entries": expired,
                "active_entries": total - expired
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get cache metrics: {e}")
            return {}
        finally:
            conn.close()

from typing import Dict, Any, Optional
import logging
import json
from pathlib import Path
import sqlite3
from datetime import datetime

class StateManager:
    def __init__(self):
        self.logger = logging.getLogger("state_manager")
        self.db_path = Path("graph/states.db")
        self.initialize_database()

    def initialize_database(self):
        """Initialize state database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Create states table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_states (
                agent_id TEXT PRIMARY KEY,
                state TEXT,
                timestamp DATETIME,
                version INTEGER
            )''')
            
            # Create state history table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS state_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT,
                state TEXT,
                timestamp DATETIME,
                version INTEGER
            )''')
            
            conn.commit()
        except Exception as e:
            self.logger.error(f"Failed to initialize state database: {e}")
        finally:
            conn.close()

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    async def save_state(self, agent_id: str, state: Dict[str, Any]):
        """Save agent state"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get current version
            cursor.execute('''
            SELECT version FROM agent_states 
            WHERE agent_id = ?
            ''', (agent_id,))
            
            result = cursor.fetchone()
            version = (result[0] + 1) if result else 1
            
            # Save current state
            now = datetime.now().isoformat()
            cursor.execute('''
            INSERT OR REPLACE INTO agent_states (agent_id, state, timestamp, version)
            VALUES (?, ?, ?, ?)
            ''', (agent_id, json.dumps(state), now, version))
            
            # Save to history
            cursor.execute('''
            INSERT INTO state_history (agent_id, state, timestamp, version)
            VALUES (?, ?, ?, ?)
            ''', (agent_id, json.dumps(state), now, version))
            
            conn.commit()
            
        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")
            raise
        finally:
            conn.close()

    async def load_state(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Load agent state"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT state FROM agent_states 
            WHERE agent_id = ?
            ''', (agent_id,))
            
            result = cursor.fetchone()
            if result:
                return json.loads(result[0])
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to load state: {e}")
            return None
        finally:
            conn.close()

    async def get_state_history(self, agent_id: str, limit: int = 10) -> list:
        """Get state history for agent"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT state, timestamp, version 
            FROM state_history 
            WHERE agent_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
            ''', (agent_id, limit))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    "state": json.loads(row[0]),
                    "timestamp": row[1],
                    "version": row[2]
                })
            
            return history
            
        except Exception as e:
            self.logger.error(f"Failed to get state history: {e}")
            return []
        finally:
            conn.close()

    async def compare_states(self, agent_id: str, version1: int, version2: int) -> Dict[str, Any]:
        """Compare two state versions"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get states
            cursor.execute('''
            SELECT state FROM state_history 
            WHERE agent_id = ? AND version IN (?, ?)
            ''', (agent_id, version1, version2))
            
            states = cursor.fetchall()
            if len(states) != 2:
                return {}
                
            state1 = json.loads(states[0][0])
            state2 = json.loads(states[1][0])
            
            # Compare states
            differences = {
                "added": {},
                "removed": {},
                "modified": {}
            }
            
            # Find differences
            for key in set(state1.keys()) | set(state2.keys()):
                if key not in state1:
                    differences["added"][key] = state2[key]
                elif key not in state2:
                    differences["removed"][key] = state1[key]
                elif state1[key] != state2[key]:
                    differences["modified"][key] = {
                        "from": state1[key],
                        "to": state2[key]
                    }
            
            return differences
            
        except Exception as e:
            self.logger.error(f"Failed to compare states: {e}")
            return {}
        finally:
            conn.close()

    async def clear_history(self, agent_id: str, before_date: Optional[datetime] = None):
        """Clear state history"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if before_date:
                cursor.execute('''
                DELETE FROM state_history 
                WHERE agent_id = ? AND datetime(timestamp) < datetime(?)
                ''', (agent_id, before_date.isoformat()))
            else:
                cursor.execute('''
                DELETE FROM state_history 
                WHERE agent_id = ?
                ''', (agent_id,))
            
            conn.commit()
            
        except Exception as e:
            self.logger.error(f"Failed to clear history: {e}")
        finally:
            conn.close()


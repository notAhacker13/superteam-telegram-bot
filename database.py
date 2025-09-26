"""Database operations for the Superteam Ireland Bot"""

import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()

            # Seen bounties table
            c.execute("""
            CREATE TABLE IF NOT EXISTS seen_bounties (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                deadline TEXT,
                reward TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Subscribers table
            c.execute("""
            CREATE TABLE IF NOT EXISTS subscribers (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1
            )
            """)

            # Bot settings table
            c.execute("""
            CREATE TABLE IF NOT EXISTS bot_settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            conn.commit()
            logger.info("Database initialized successfully")

    def is_new_bounty(self, bounty_id: str) -> bool:
        """Check if bounty is new (not seen before)"""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("SELECT 1 FROM seen_bounties WHERE id = ?", (bounty_id,))
            return c.fetchone() is None

    def mark_bounty_seen(self, bounty: Dict):
        """Mark bounty as seen"""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("""
            INSERT OR IGNORE INTO seen_bounties (id, title, deadline, reward) 
            VALUES (?, ?, ?, ?)
            """, (bounty["id"], bounty["title"], bounty["deadline"], bounty["reward"]))
            conn.commit()

    def add_subscriber(self, user_id: int, username: str = None, first_name: str = None):
        """Add a new subscriber"""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("""
            INSERT OR REPLACE INTO subscribers (user_id, username, first_name, is_active) 
            VALUES (?, ?, ?, 1)
            """, (user_id, username, first_name))
            conn.commit()
            logger.info(f"Added subscriber: {user_id}")

    def remove_subscriber(self, user_id: int):
        """Remove a subscriber"""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("UPDATE subscribers SET is_active = 0 WHERE user_id = ?", (user_id,))
            conn.commit()
            logger.info(f"Removed subscriber: {user_id}")

    def get_active_subscribers(self) -> List[int]:
        """Get list of active subscriber user IDs"""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("SELECT user_id FROM subscribers WHERE is_active = 1")
            return [row[0] for row in c.fetchall()]

    def is_subscribed(self, user_id: int) -> bool:
        """Check if user is subscribed"""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("SELECT 1 FROM subscribers WHERE user_id = ? AND is_active = 1", (user_id,))
            return c.fetchone() is not None

    def get_setting(self, key: str) -> Optional[str]:
        """Get bot setting"""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("SELECT value FROM bot_settings WHERE key = ?", (key,))
            result = c.fetchone()
            return result[0] if result else None

    def set_setting(self, key: str, value: str):
        """Set bot setting"""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("""
            INSERT OR REPLACE INTO bot_settings (key, value, updated_at) 
            VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (key, value))
            conn.commit()

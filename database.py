import aiosqlite
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any
from config import DATABASE_PATH, DEFAULT_CURRENCY, DEFAULT_SEND_TIME, DEFAULT_TEMPLATE

class Database:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path

    async def init_db(self):
        """Initialize database tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # Users table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER UNIQUE NOT NULL,
                    fullname TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    track_code TEXT,
                    reg_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Settings table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY,
                    currency TEXT DEFAULT 'USD',
                    selected_currencies TEXT DEFAULT 'USD',
                    send_time TEXT DEFAULT '09:00',
                    template TEXT DEFAULT '',
                    channels TEXT DEFAULT ''
                )
            ''')
            
            # Insert default settings if not exists
            await db.execute('''
                INSERT OR IGNORE INTO settings (id, currency, selected_currencies, send_time, template, channels)
                VALUES (1, ?, ?, ?, ?, '')
            ''', (DEFAULT_CURRENCY, DEFAULT_CURRENCY, DEFAULT_SEND_TIME, DEFAULT_TEMPLATE))
            
            await db.commit()

    async def add_user(self, user_id: int, fullname: str, phone: str) -> bool:
        """Add new user to database"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT OR REPLACE INTO users (user_id, fullname, phone, reg_date)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, fullname, phone, datetime.now()))
                await db.commit()
                return True
        except Exception as e:
            print(f"Error adding user: {e}")
            return False

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by user_id"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('''
                SELECT * FROM users WHERE user_id = ?
            ''', (user_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def get_user_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """Get user by phone number"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('''
                SELECT * FROM users WHERE phone = ?
            ''', (phone,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def update_track_code(self, phone: str, track_code: str) -> bool:
        """Update track code for user by phone"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    UPDATE users SET track_code = ? WHERE phone = ?
                ''', (track_code, phone))
                await db.commit()
                return True
        except Exception as e:
            print(f"Error updating track code: {e}")
            return False

    async def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT * FROM users ORDER BY reg_date DESC') as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_user_stats(self) -> Dict[str, int]:
        """Get user statistics"""
        async with aiosqlite.connect(self.db_path) as db:
            # Total users
            async with db.execute('SELECT COUNT(*) FROM users') as cursor:
                total_users = (await cursor.fetchone())[0]
            
            # Active users (registered in last 30 days)
            async with db.execute('''
                SELECT COUNT(*) FROM users 
                WHERE reg_date >= datetime('now', '-30 days')
            ''') as cursor:
                active_users = (await cursor.fetchone())[0]
            
            return {
                'total_users': total_users,
                'active_users': active_users
            }

    async def get_settings(self) -> Dict[str, Any]:
        """Get bot settings"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute('SELECT * FROM settings WHERE id = 1') as cursor:
                    row = await cursor.fetchone()
                    result = dict(row) if row else {}
                    print(f"Database settings result: {result}")
                    return result
        except Exception as e:
            print(f"Error getting settings: {e}")
            return {}

    async def update_settings(self, **kwargs) -> bool:
        """Update bot settings"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                for key, value in kwargs.items():
                    if key in ['currency', 'selected_currencies', 'send_time', 'template', 'channels']:
                        await db.execute(f'''
                            UPDATE settings SET {key} = ? WHERE id = 1
                        ''', (value,))
                await db.commit()
                return True
        except Exception as e:
            print(f"Error updating settings: {e}")
            return False

# Global database instance
db = Database()
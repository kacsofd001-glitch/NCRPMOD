"""
Database management for guild settings and user sessions
"""
import sqlite3
import json
import os
from datetime import datetime, timezone
from threading import Lock

DB_FILE = 'dashboard.db'
db_lock = Lock()

def init_db():
    """Initialize SQLite database with schema"""
    with db_lock:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Guild settings table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS guild_settings (
            guild_id TEXT,
            user_id TEXT,
            guild_name TEXT,
            is_admin INTEGER DEFAULT 0,
            moderation_settings TEXT,
            automod_settings TEXT,
            logging_settings TEXT,
            welcome_settings TEXT,
            bad_words TEXT,
            whitelisted_links TEXT,
            custom_commands TEXT,
            role_settings TEXT,
            music_settings TEXT,
            games_settings TEXT,
            language TEXT DEFAULT 'en',
            prefix TEXT DEFAULT '!',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, guild_id)
        )
        ''')
        
        # User sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                user_id TEXT PRIMARY KEY,
                access_token TEXT NOT NULL,
                refresh_token TEXT,
                username TEXT,
                avatar_url TEXT,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User-Guild relationship (tracks admin access)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_guilds (
                user_id TEXT NOT NULL,
                guild_id TEXT NOT NULL,
                guild_name TEXT,
                icon TEXT,
                is_admin INTEGER DEFAULT 0,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, guild_id)
            )
        ''')
        
        # Biztonsági ellenőrzés: oszlopok hozzáadása ha a tábla már létezne
        try:
            cursor.execute('ALTER TABLE user_guilds ADD COLUMN guild_name TEXT')
        except sqlite3.OperationalError:
            pass
            
        try:
            cursor.execute('ALTER TABLE user_guilds ADD COLUMN icon TEXT')
        except sqlite3.OperationalError:
            pass
        
        conn.commit()
        conn.close()
    print("✅ Database initialized successfully.", flush=True)

def get_guild_settings(guild_id):
    """Get all settings for a guild"""
    with db_lock:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM guild_settings WHERE guild_id = ?', (guild_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'guild_id': row['guild_id'],
                'moderation': json.loads(row['moderation_settings'] or '{}'),
                'automod': json.loads(row['automod_settings'] or '{}'),
                'logging': json.loads(row['logging_settings'] or '{}'),
                'welcome': json.loads(row['welcome_settings'] or '{}'),
                'bad_words': json.loads(row['bad_words'] or '[]'),
                'whitelisted_links': json.loads(row['whitelisted_links'] or '[]'),
                'custom_commands': json.loads(row['custom_commands'] or '{}'),
                'role_settings': json.loads(row['role_settings'] or '{}'),
                'music_settings': json.loads(row['music_settings'] or '{}'),
                'games_settings': json.loads(row['games_settings'] or '{}'),
                'language': row['language'] or 'en',
                'prefix': row['prefix'] or '!',
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }
        
        return {
            'guild_id': guild_id,
            'moderation': {}, 'automod': {}, 'logging': {}, 'welcome': {},
            'bad_words': [], 'whitelisted_links': [], 'custom_commands': {},
            'role_settings': {}, 'music_settings': {}, 'games_settings': {},
            'language': 'en', 'prefix': '!'
        }

def update_guild_settings(guild_id, settings_dict):
    """Update guild settings"""
    with db_lock:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO guild_settings 
            (guild_id, moderation_settings, automod_settings, logging_settings, 
             welcome_settings, bad_words, whitelisted_links, custom_commands,
             role_settings, music_settings, games_settings, language, prefix, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            guild_id,
            json.dumps(settings_dict.get('moderation', {})),
            json.dumps(settings_dict.get('automod', {})),
            json.dumps(settings_dict.get('logging', {})),
            json.dumps(settings_dict.get('welcome', {})),
            json.dumps(settings_dict.get('bad_words', [])),
            json.dumps(settings_dict.get('whitelisted_links', [])),
            json.dumps(settings_dict.get('custom_commands', {})),
            json.dumps(settings_dict.get('role_settings', {})),
            json.dumps(settings_dict.get('music_settings', {})),
            json.dumps(settings_dict.get('games_settings', {})),
            settings_dict.get('language', 'en'),
            settings_dict.get('prefix', '!')
        ))
        
        conn.commit()
        conn.close()

def save_user_session(user_id, access_token, refresh_token, username, avatar_url, expires_in):
    """Save user session from Discord OAuth"""
    with db_lock:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        expires_at = datetime.now(timezone.utc).timestamp() + expires_in
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_sessions 
            (user_id, access_token, refresh_token, username, avatar_url, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, access_token, refresh_token, username, avatar_url, expires_at))
        
        conn.commit()
        conn.close()

def get_user_session(user_id):
    """Get user session"""
    with db_lock:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user_sessions WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None

def delete_user_session(user_id):
    """Delete user session (logout)"""
    with db_lock:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM user_sessions WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()

def cache_user_guilds(user_id, guilds_data):
    """Cache user's guild memberships with name and icon"""
    with db_lock:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_guilds WHERE user_id = ?", (user_id,))

        for guild in guilds_data:
            guild_id = guild["id"]
            guild_name = guild["name"]
            icon_hash = guild.get("icon", "")
            permissions = int(guild.get("permissions", 0))
            # Discord admin permission bit ellenőrzése
            is_admin = 1 if (permissions & 0x20) == 0x20 else 0

            cursor.execute(
                """INSERT OR REPLACE INTO user_guilds 
                (user_id, guild_id, guild_name, icon, is_admin) 
                VALUES (?, ?, ?, ?, ?)""",
                (user_id, guild_id, guild_name, icon_hash, is_admin)
            )
        conn.commit()
        conn.close()

def get_user_admin_guilds(user_id):
    """Returns detailed objects for the dashboard"""
    with db_lock:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            'SELECT guild_id, guild_name, icon FROM user_guilds WHERE user_id = ? AND is_admin = 1', 
            (user_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
        
def guild_exists_in_cache(user_id, guild_id):
    """Check if guild is in user's cache and user is admin"""
    with db_lock:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT is_admin FROM user_guilds WHERE user_id = ? AND guild_id = ?', (user_id, guild_id))
        row = cursor.fetchone()
        conn.close()
        return row is not None and row[0] == 1

if __name__ == "__main__":
    init_db()
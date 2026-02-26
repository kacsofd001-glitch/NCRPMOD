import json
import os
import tempfile
import threading
from datetime import datetime

CONFIG_FILE = 'bot_config.json'
CONFIG_BACKUP_FILE = 'bot_config.backup.json'

DEFAULT_CONFIG = {
    'log_channel_id': None,
    'guild_log_channels': {},
    'announcement_channels': {},
    'ticket_category_id': None,
    'ticket_counter': 0,
    'muted_roles': {},
    'min_account_age_days': 7,
    'warnings': {},
    'temp_bans': {},
    'temp_mutes': {},
    'giveaways': {},
    'completed_giveaways': {},
    'role_prefixes': {},
    'webhook_url': None,
    'guild_languages': {},
    'guild_prefixes': {},
    'last_saved': None
}

# Global config cache for faster access
_config_cache = None
_cache_lock = threading.Lock()

def load_config():
    """Load config from file with fallback to backup"""
    global _config_cache
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                _config_cache = config
                return config
        except (json.JSONDecodeError, EOFError):
            print(f"⚠️  Warning: {CONFIG_FILE} corrupted, attempting to recover from backup")
            if os.path.exists(CONFIG_BACKUP_FILE):
                try:
                    with open(CONFIG_BACKUP_FILE, 'r') as f:
                        config = json.load(f)
                        _config_cache = config
                        return config
                except:
                    pass
            print(f"❌ Config recovery failed, returning default config")
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()

def save_config(config_data):
    """Save config atomically to prevent corruption"""
    global _config_cache
    
    try:
        # Update timestamp
        config_data['last_saved'] = datetime.now().isoformat()
        
        # Create backup first
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    backup_data = json.load(f)
                with open(CONFIG_BACKUP_FILE, 'w') as f:
                    json.dump(backup_data, f, indent=4)
            except:
                pass
        
        # Create a temporary file in the same directory
        fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(CONFIG_FILE)), prefix='config_tmp_')
        try:
            with os.fdopen(fd, 'w') as f:
                json.dump(config_data, f, indent=4)
                f.flush()
                os.fsync(f.fileno())
            # Atomic rename
            os.replace(temp_path, CONFIG_FILE)
            _config_cache = config_data
            print(f"✅ Config saved successfully at {config_data['last_saved']}")
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise e
    except Exception as e:
        print(f"❌ Failed to save config: {e}")

def get_config():
    return load_config()

def update_config(key, value):
    config = load_config()
    config[key] = value
    save_config(config)
    return config

def get_guild_prefix(guild_id):
    """Get the prefix for a specific guild"""
    config = load_config()
    guild_prefixes = config.get('guild_prefixes', {})
    return guild_prefixes.get(str(guild_id), '!')

def set_guild_prefix(guild_id, prefix):
    """Set the prefix for a specific guild"""
    config = load_config()
    if 'guild_prefixes' not in config:
        config['guild_prefixes'] = {}
    config['guild_prefixes'][str(guild_id)] = prefix
    save_config(config)
    return prefix
def refresh_config_cache():
    """Force reload config from disk to sync with external changes (e.g., dashboard updates)"""
    global _config_cache
    with _cache_lock:
        _config_cache = None  # Clear cache
        return load_config()  # Reload from disk

def get_cached_config():
    """Get config from cache without reloading (fast access)"""
    global _config_cache
    if _config_cache is None:
        return load_config()
    return _config_cache
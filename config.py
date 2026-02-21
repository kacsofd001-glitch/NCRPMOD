import json
import os
import tempfile

CONFIG_FILE = 'bot_config.json'

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
    'guild_prefixes': {}
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, EOFError):
            # Attempt to recover or return default if corrupted
            print(f"Warning: {CONFIG_FILE} corrupted, returning default config")
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()

def save_config(config_data):
    """Save config atomically to prevent corruption"""
    # Create a temporary file in the same directory
    fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(CONFIG_FILE)), prefix='config_tmp_')
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(config_data, f, indent=4)
            f.flush()
            os.fsync(f.fileno())
        # Atomic rename
        os.replace(temp_path, CONFIG_FILE)
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise e

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

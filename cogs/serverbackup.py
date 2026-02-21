import discord
from discord.ext import commands
import config
import json
from datetime import datetime, timezone

class ServerBackup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def create_backup(self, guild):
        """Create full server backup"""
        backup = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'guild_name': guild.name,
            'guild_id': guild.id,
            'roles': [],
            'channels': [],
            'categories': [],
            'settings': {
                'verification_level': str(guild.verification_level),
                'default_notifications': str(guild.default_notifications),
                'explicit_content_filter': str(guild.explicit_content_filter)
            }
        }
        
        # Backup roles
        for role in guild.roles:
            if role != guild.default_role:
                backup['roles'].append({
                    'name': role.name,
                    'color': role.color.value,
                    'permissions': role.permissions.value,
                    'hoist': role.hoist,
                    'mentionable': role.mentionable,
                    'position': role.position
                })
        
        # Backup categories
        for category in guild.categories:
            backup['categories'].append({
                'name': category.name,
                'position': category.position
            })
        
        # Backup channels
        for channel in guild.channels:
            if isinstance(channel, discord.TextChannel):
                backup['channels'].append({
                    'type': 'text',
                    'name': channel.name,
                    'category': channel.category.name if channel.category else None,
                    'position': channel.position,
                    'topic': channel.topic,
                    'nsfw': channel.nsfw,
                    'slowmode_delay': channel.slowmode_delay
                })
            elif isinstance(channel, discord.VoiceChannel):
                backup['channels'].append({
                    'type': 'voice',
                    'name': channel.name,
                    'category': channel.category.name if channel.category else None,
                    'position': channel.position,
                    'bitrate': channel.bitrate,
                    'user_limit': channel.user_limit
                })
        
        return backup
    
    def save_backup(self, guild_id, backup):
        """Save backup to config"""
        cfg = config.load_config()
        if 'server_backups' not in cfg:
            cfg['server_backups'] = {}
        
        backup_id = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        
        if str(guild_id) not in cfg['server_backups']:
            cfg['server_backups'][str(guild_id)] = {}
        
        cfg['server_backups'][str(guild_id)][backup_id] = backup
        config.save_config(cfg)
        
        return backup_id
    
    def get_backups(self, guild_id):
        """Get all backups for a guild"""
        cfg = config.load_config()
        backups = cfg.get('server_backups', {})
        return backups.get(str(guild_id), {})

async def setup(bot):
    await bot.add_cog(ServerBackup(bot))

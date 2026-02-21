import discord
from discord.ext import commands, tasks
import config
from datetime import datetime, timezone
from collections import defaultdict

class ServerStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_counts = defaultdict(int)
        self.save_stats_task.start()
    
    def cog_unload(self):
        self.save_stats_task.cancel()
    
    def get_server_stats(self, guild_id):
        """Get server statistics"""
        cfg = config.load_config()
        stats = cfg.get('server_stats', {})
        return stats.get(str(guild_id), {
            'total_messages': 0,
            'member_count_history': [],
            'most_active_users': {},
            'most_active_channels': {}
        })
    
    def save_server_stats(self, guild_id, stats):
        """Save server statistics"""
        cfg = config.load_config()
        if 'server_stats' not in cfg:
            cfg['server_stats'] = {}
        cfg['server_stats'][str(guild_id)] = stats
        config.save_config(cfg)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        
        # Track message counts
        guild_key = f"{message.guild.id}"
        user_key = f"{message.guild.id}_{message.author.id}"
        channel_key = f"{message.guild.id}_{message.channel.id}"
        
        self.message_counts[guild_key] += 1
        self.message_counts[user_key] += 1
        self.message_counts[channel_key] += 1
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Track member joins"""
        stats = self.get_server_stats(member.guild.id)
        
        stats['member_count_history'].append({
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'count': member.guild.member_count,
            'type': 'join'
        })
        
        # Keep only last 100 entries
        if len(stats['member_count_history']) > 100:
            stats['member_count_history'] = stats['member_count_history'][-100:]
        
        self.save_server_stats(member.guild.id, stats)
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Track member leaves"""
        stats = self.get_server_stats(member.guild.id)
        
        stats['member_count_history'].append({
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'count': member.guild.member_count,
            'type': 'leave'
        })
        
        # Keep only last 100 entries
        if len(stats['member_count_history']) > 100:
            stats['member_count_history'] = stats['member_count_history'][-100:]
        
        self.save_server_stats(member.guild.id, stats)
    
    @tasks.loop(minutes=10)
    async def save_stats_task(self):
        """Periodically save statistics"""
        for guild in self.bot.guilds:
            stats = self.get_server_stats(guild.id)
            
            # Update total messages
            guild_key = f"{guild.id}"
            if guild_key in self.message_counts:
                stats['total_messages'] += self.message_counts[guild_key]
                self.message_counts[guild_key] = 0
            
            # Update most active users
            for key, count in list(self.message_counts.items()):
                if key.startswith(f"{guild.id}_") and len(key.split('_')) == 2:
                    user_id = key.split('_')[1]
                    if user_id not in stats['most_active_users']:
                        stats['most_active_users'][user_id] = 0
                    stats['most_active_users'][user_id] += count
                    del self.message_counts[key]
            
            # Update most active channels
            for key, count in list(self.message_counts.items()):
                if key.startswith(f"{guild.id}_") and len(key.split('_')) == 2:
                    channel_id = key.split('_')[1]
                    if channel_id not in stats['most_active_channels']:
                        stats['most_active_channels'][channel_id] = 0
                    stats['most_active_channels'][channel_id] += count
                    del self.message_counts[key]
            
            self.save_server_stats(guild.id, stats)
    
    @save_stats_task.before_loop
    async def before_save_stats(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(ServerStats(bot))

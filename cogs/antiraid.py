import discord
from discord.ext import commands
import config
from datetime import datetime, timedelta, timezone
from collections import defaultdict

class AntiRaid(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.join_tracking = defaultdict(list)
    
    def get_antiraid_config(self, guild_id):
        """Get anti-raid settings"""
        cfg = config.load_config()
        antiraid = cfg.get('antiraid', {})
        return antiraid.get(str(guild_id), {
            'enabled': False,
            'join_threshold': 10,
            'time_window': 10,
            'action': 'kick',
            'lockdown_on_raid': True
        })
    
    def save_antiraid_config(self, guild_id, settings):
        """Save anti-raid settings"""
        cfg = config.load_config()
        if 'antiraid' not in cfg:
            cfg['antiraid'] = {}
        cfg['antiraid'][str(guild_id)] = settings
        config.save_config(cfg)
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        settings = self.get_antiraid_config(member.guild.id)
        
        if not settings['enabled']:
            return
        
        now = datetime.now(timezone.utc)
        guild_id = member.guild.id
        
        # Track join
        self.join_tracking[guild_id].append(now)
        
        # Clean old joins
        cutoff = now - timedelta(seconds=settings['time_window'])
        self.join_tracking[guild_id] = [
            join_time for join_time in self.join_tracking[guild_id]
            if join_time > cutoff
        ]
        
        # Check if raid detected
        if len(self.join_tracking[guild_id]) >= settings['join_threshold']:
            await self.handle_raid(member.guild, settings)
    
    async def handle_raid(self, guild, settings):
        """Handle detected raid"""
        # Send alert
        logging_cog = self.bot.get_cog('Logging')
        if logging_cog:
            log_channel_id = logging_cog.get_log_channel(guild.id)
            if log_channel_id:
                channel = guild.get_channel(log_channel_id)
                if channel:
                    embed = discord.Embed(
                        title="🚨 RAID DETECTED!",
                        description=f"**{settings['join_threshold']}** users joined in **{settings['time_window']}** seconds!\n\nAction taken: **{settings['action'].upper()}**",
                        color=0xFF0000,
                        timestamp=discord.utils.utcnow()
                    )
                    await channel.send("@here", embed=embed)
        
        # Take action based on settings
        if settings['action'] == 'kick':
            recent_members = sorted(guild.members, key=lambda m: m.joined_at, reverse=True)[:settings['join_threshold']]
            for member in recent_members:
                try:
                    await member.kick(reason="Anti-raid protection")
                except:
                    pass
        
        elif settings['action'] == 'ban':
            recent_members = sorted(guild.members, key=lambda m: m.joined_at, reverse=True)[:settings['join_threshold']]
            for member in recent_members:
                try:
                    await member.ban(reason="Anti-raid protection")
                except:
                    pass
        
        # Lockdown if enabled
        if settings['lockdown_on_raid']:
            for channel in guild.text_channels:
                try:
                    await channel.set_permissions(guild.default_role, send_messages=False, reason="Raid lockdown")
                except:
                    pass

async def setup(bot):
    await bot.add_cog(AntiRaid(bot))

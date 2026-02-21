import discord
from discord.ext import commands
import config
from datetime import datetime, timezone

class VoiceAnalytics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def get_voice_stats(self, guild_id, user_id=None):
        """Get voice analytics"""
        cfg = config.load_config()
        voice = cfg.get('voice_analytics', {})
        guild_voice = voice.get(str(guild_id), {})
        
        if user_id:
            return guild_voice.get(str(user_id), {
                'total_time': 0,
                'sessions': [],
                'current_session_start': None
            })
        return guild_voice
    
    def save_voice_stats(self, guild_id, user_id, data):
        """Save voice analytics"""
        cfg = config.load_config()
        if 'voice_analytics' not in cfg:
            cfg['voice_analytics'] = {}
        if str(guild_id) not in cfg['voice_analytics']:
            cfg['voice_analytics'][str(guild_id)] = {}
        cfg['voice_analytics'][str(guild_id)][str(user_id)] = data
        config.save_config(cfg)
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return
        
        user_stats = self.get_voice_stats(member.guild.id, member.id)
        
        if before.channel is None and after.channel is not None:
            user_stats['current_session_start'] = datetime.now(timezone.utc).isoformat()
            self.save_voice_stats(member.guild.id, member.id, user_stats)
        
        elif before.channel is not None and after.channel is None:
            if user_stats['current_session_start']:
                start = datetime.fromisoformat(user_stats['current_session_start'])
                duration = (datetime.now(timezone.utc) - start).total_seconds()
                
                user_stats['total_time'] += duration
                user_stats['sessions'].append({
                    'start': user_stats['current_session_start'],
                    'end': datetime.now(timezone.utc).isoformat(),
                    'duration': duration,
                    'channel': before.channel.name
                })
                user_stats['current_session_start'] = None
                
                if len(user_stats['sessions']) > 100:
                    user_stats['sessions'] = user_stats['sessions'][-100:]
                
                self.save_voice_stats(member.guild.id, member.id, user_stats)

async def setup(bot):
    await bot.add_cog(VoiceAnalytics(bot))

import discord
from discord.ext import commands, tasks
import config
import aiohttp

class StreamAlerts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_streams.start()
    
    def cog_unload(self):
        self.check_streams.cancel()
    
    def get_stream_config(self, guild_id):
        """Get stream alert settings"""
        cfg = config.load_config()
        streams = cfg.get('stream_alerts', {})
        return streams.get(str(guild_id), {
            'enabled': False,
            'channel_id': None,
            'streamers': {},
            'currently_live': []
        })
    
    def save_stream_config(self, guild_id, settings):
        """Save stream alert settings"""
        cfg = config.load_config()
        if 'stream_alerts' not in cfg:
            cfg['stream_alerts'] = {}
        cfg['stream_alerts'][str(guild_id)] = settings
        config.save_config(cfg)
    
    @tasks.loop(minutes=5)
    async def check_streams(self):
        """Check for live streams"""
        # Note: This would require Twitch/YouTube API integration
        # For now, it monitors Discord streaming status
        for guild in self.bot.guilds:
            settings = self.get_stream_config(guild.id)
            
            if not settings['enabled'] or not settings['channel_id']:
                continue
            
            channel = guild.get_channel(settings['channel_id'])
            if not channel:
                continue
            
            # Check members for streaming status
            for member in guild.members:
                if member.activity and member.activity.type == discord.ActivityType.streaming:
                    member_key = str(member.id)
                    
                    if member_key not in settings['currently_live']:
                        # Just went live!
                        settings['currently_live'].append(member_key)
                        self.save_stream_config(guild.id, settings)
                        
                        embed = discord.Embed(
                            title="🔴 LIVE NOW!",
                            description=f"{member.mention} is now streaming!",
                            color=0x9146FF
                        )
                        if hasattr(member.activity, 'name'):
                            embed.add_field(name="Game", value=member.activity.name, inline=True)
                        if hasattr(member.activity, 'url'):
                            embed.add_field(name="Watch", value=f"[Click here]({member.activity.url})", inline=True)
                        
                        embed.set_thumbnail(url=member.display_avatar.url)
                        
                        await channel.send(embed=embed)
                else:
                    member_key = str(member.id)
                    if member_key in settings['currently_live']:
                        settings['currently_live'].remove(member_key)
                        self.save_stream_config(guild.id, settings)
    
    @check_streams.before_loop
    async def before_check_streams(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(StreamAlerts(bot))

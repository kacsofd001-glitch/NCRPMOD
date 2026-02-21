import discord
from discord.ext import commands, tasks
import config
from datetime import datetime, timezone

class GrowthTracking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.record_growth.start()
    
    def cog_unload(self):
        self.record_growth.cancel()
    
    def get_growth_data(self, guild_id):
        """Get growth tracking data"""
        cfg = config.load_config()
        growth = cfg.get('growth_tracking', {})
        return growth.get(str(guild_id), {
            'member_history': [],
            'message_history': [],
            'voice_history': []
        })
    
    def save_growth_data(self, guild_id, data):
        """Save growth tracking data"""
        cfg = config.load_config()
        if 'growth_tracking' not in cfg:
            cfg['growth_tracking'] = {}
        cfg['growth_tracking'][str(guild_id)] = data
        config.save_config(cfg)
    
    @tasks.loop(hours=1)
    async def record_growth(self):
        """Record growth metrics every hour"""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        for guild in self.bot.guilds:
            data = self.get_growth_data(guild.id)
            
            # Record member count
            data['member_history'].append({
                'timestamp': timestamp,
                'count': guild.member_count
            })
            
            # Keep only last 30 days (720 data points)
            if len(data['member_history']) > 720:
                data['member_history'] = data['member_history'][-720:]
            
            self.save_growth_data(guild.id, data)
    
    @record_growth.before_loop
    async def before_record_growth(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(GrowthTracking(bot))

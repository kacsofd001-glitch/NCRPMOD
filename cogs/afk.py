import discord
from discord.ext import commands
import config
from datetime import datetime, timezone

class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def get_afk_users(self):
        """Get all AFK users"""
        cfg = config.load_config()
        return cfg.get('afk_users', {})
    
    def save_afk_users(self, afk_users):
        """Save AFK users"""
        cfg = config.load_config()
        cfg['afk_users'] = afk_users
        config.save_config(cfg)
    
    def set_afk(self, user_id, reason):
        """Set user as AFK"""
        afk_users = self.get_afk_users()
        afk_users[str(user_id)] = {
            'reason': reason,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        self.save_afk_users(afk_users)
    
    def remove_afk(self, user_id):
        """Remove AFK status"""
        afk_users = self.get_afk_users()
        if str(user_id) in afk_users:
            del afk_users[str(user_id)]
            self.save_afk_users(afk_users)
            return True
        return False
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        
        afk_users = self.get_afk_users()
        
        # Check if user is returning from AFK
        if str(message.author.id) in afk_users:
            afk_data = afk_users[str(message.author.id)]
            afk_time = datetime.fromisoformat(afk_data['timestamp'])
            time_diff = datetime.now(timezone.utc) - afk_time
            
            hours = int(time_diff.total_seconds() // 3600)
            minutes = int((time_diff.total_seconds() % 3600) // 60)
            
            time_str = ""
            if hours > 0:
                time_str = f"{hours}h {minutes}m"
            else:
                time_str = f"{minutes}m"
            
            self.remove_afk(message.author.id)
            
            try:
                await message.channel.send(
                    f" Welcome back {message.author.mention}! You were AFK for {time_str}",
                    delete_after=10
                )
            except:
                pass
        
        # Check if mentioned users are AFK
        for mention in message.mentions:
            if str(mention.id) in afk_users:
                afk_data = afk_users[str(mention.id)]
                
                try:
                    await message.channel.send(
                        f"💤 {mention.name} is currently AFK: {afk_data['reason']}",
                        delete_after=10
                    )
                except:
                    pass

async def setup(bot):
    await bot.add_cog(AFK(bot))

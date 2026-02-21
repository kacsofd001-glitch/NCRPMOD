import discord
from discord.ext import commands, tasks
import config
from datetime import datetime, timezone

class TempBans(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_bans.start()
    
    def cog_unload(self):
        self.check_bans.cancel()
    
    def get_tempban_list(self):
        """Get all temporary bans"""
        cfg = config.load_config()
        return cfg.get('tempbans', [])
    
    def save_tempban_list(self, tempbans):
        """Save temporary bans"""
        cfg = config.load_config()
        cfg['tempbans'] = tempbans
        config.save_config(cfg)
    
    def add_tempban(self, guild_id, user_id, unban_at):
        """Add temporary ban"""
        tempbans = self.get_tempban_list()
        tempbans.append({
            'guild_id': guild_id,
            'user_id': user_id,
            'unban_at': unban_at.isoformat()
        })
        self.save_tempban_list(tempbans)
    
    @tasks.loop(minutes=1)
    async def check_bans(self):
        """Check for expired temp bans"""
        tempbans = self.get_tempban_list()
        now = datetime.now(timezone.utc)
        
        to_remove = []
        
        for ban in tempbans:
            unban_at = datetime.fromisoformat(ban['unban_at'])
            
            if now >= unban_at:
                # Unban user
                try:
                    guild = self.bot.get_guild(ban['guild_id'])
                    if guild:
                        await guild.unban(discord.Object(id=ban['user_id']), reason="Temporary ban expired")
                except:
                    pass
                
                to_remove.append(ban)
        
        # Remove expired bans
        for ban in to_remove:
            tempbans.remove(ban)
        
        if to_remove:
            self.save_tempban_list(tempbans)
    
    @check_bans.before_loop
    async def before_check_bans(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(TempBans(bot))

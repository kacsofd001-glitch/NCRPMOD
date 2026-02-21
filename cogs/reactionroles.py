import discord
from discord.ext import commands
import config

class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def get_reaction_roles(self):
        """Get all reaction role configurations"""
        cfg = config.load_config()
        return cfg.get('reaction_roles', {})
    
    def save_reaction_roles(self, data):
        """Save reaction role configurations"""
        cfg = config.load_config()
        cfg['reaction_roles'] = data
        config.save_config(cfg)
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # Get guild and member (payload.member may be None for uncached users)
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
        
        try:
            member = payload.member or await guild.fetch_member(payload.user_id)
        except:
            return
        
        if not member or member.bot:
            return
        
        reaction_roles = self.get_reaction_roles()
        message_key = f"{payload.message_id}"
        
        if message_key not in reaction_roles:
            return
        
        emoji_key = str(payload.emoji)
        role_id = reaction_roles[message_key].get(emoji_key)
        
        if role_id:
            role = guild.get_role(role_id)
            
            if role:
                try:
                    await member.add_roles(role, reason="Reaction role")
                except:
                    pass
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
        
        reaction_roles = self.get_reaction_roles()
        message_key = f"{payload.message_id}"
        
        if message_key not in reaction_roles:
            return
        
        emoji_key = str(payload.emoji)
        role_id = reaction_roles[message_key].get(emoji_key)
        
        if role_id:
            try:
                member = guild.get_member(payload.user_id) or await guild.fetch_member(payload.user_id)
            except:
                return
            
            if not member or member.bot:
                return
            
            role = guild.get_role(role_id)
            
            if role:
                try:
                    await member.remove_roles(role, reason="Reaction role removed")
                except:
                    pass

async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))

import discord
from discord.ext import commands
import config

class RolePersist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def get_persist_config(self, guild_id):
        """Get role persistence settings"""
        cfg = config.load_config()
        persist = cfg.get('role_persist', {})
        return persist.get(str(guild_id), {
            'enabled': False,
            'saved_roles': {}
        })
    
    def save_persist_config(self, guild_id, settings):
        """Save role persistence settings"""
        cfg = config.load_config()
        if 'role_persist' not in cfg:
            cfg['role_persist'] = {}
        cfg['role_persist'][str(guild_id)] = settings
        config.save_config(cfg)
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        settings = self.get_persist_config(member.guild.id)
        
        if not settings['enabled']:
            return
        
        # Save user's roles
        role_ids = [role.id for role in member.roles if role != member.guild.default_role]
        settings['saved_roles'][str(member.id)] = role_ids
        self.save_persist_config(member.guild.id, settings)
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        settings = self.get_persist_config(member.guild.id)
        
        if not settings['enabled']:
            return
        
        user_key = str(member.id)
        if user_key in settings['saved_roles']:
            # Restore roles
            roles_to_add = []
            for role_id in settings['saved_roles'][user_key]:
                role = member.guild.get_role(role_id)
                if role:
                    roles_to_add.append(role)
            
            if roles_to_add:
                try:
                    await member.add_roles(*roles_to_add, reason="Role persistence")
                except:
                    pass

async def setup(bot):
    await bot.add_cog(RolePersist(bot))

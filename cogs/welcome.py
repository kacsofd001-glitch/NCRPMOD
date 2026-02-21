import discord
from discord.ext import commands
import config
import translations

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def get_welcome_config(self, guild_id):
        """Get welcome settings"""
        cfg = config.load_config()
        welcome = cfg.get('welcome', {})
        return welcome.get(str(guild_id), {
            'enabled': False,
            'channel_id': None,
            'message': 'Welcome {user} to {server}!',
            'embed': True,
            'dm_enabled': False,
            'dm_message': 'Welcome to {server}!',
            'auto_role': None,
            'goodbye_enabled': False,
            'goodbye_message': 'Goodbye {user}!'
        })
    
    def save_welcome_config(self, guild_id, settings):
        """Save welcome settings"""
        cfg = config.load_config()
        if 'welcome' not in cfg:
            cfg['welcome'] = {}
        cfg['welcome'][str(guild_id)] = settings
        config.save_config(cfg)
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        settings = self.get_welcome_config(member.guild.id)
        
        if not settings['enabled']:
            return
        
        # Send welcome message
        if settings['channel_id']:
            channel = self.bot.get_channel(settings['channel_id'])
            if channel:
                message = settings['message'].format(
                    user=member.mention,
                    server=member.guild.name,
                    count=member.guild.member_count
                )
                
                if settings['embed']:
                    embed = discord.Embed(
                        title="✨ New Member!",
                        description=message,
                        color=0x00F3FF
                    )
                    embed.set_thumbnail(url=member.display_avatar.url)
                    embed.set_footer(text=f"Member #{member.guild.member_count}")
                    await channel.send(embed=embed)
                else:
                    await channel.send(message)
        
        # Send DM
        if settings['dm_enabled']:
            try:
                dm_message = settings['dm_message'].format(
                    user=member.name,
                    server=member.guild.name
                )
                await member.send(dm_message)
            except:
                pass
        
        # Auto-role
        if settings['auto_role']:
            try:
                role = member.guild.get_role(settings['auto_role'])
                if role:
                    await member.add_roles(role, reason="Auto-role on join")
            except:
                pass
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        settings = self.get_welcome_config(member.guild.id)
        
        if not settings['goodbye_enabled'] or not settings['channel_id']:
            return
        
        channel = self.bot.get_channel(settings['channel_id'])
        if channel:
            message = settings['goodbye_message'].format(
                user=member.name,
                server=member.guild.name
            )
            
            embed = discord.Embed(
                title="👋 Member Left",
                description=message,
                color=0xFF006E
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Welcome(bot))

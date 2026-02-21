import discord
from discord.ext import commands, tasks
import config
from datetime import datetime, timezone

class Birthdays(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_birthdays.start()
    
    def cog_unload(self):
        self.check_birthdays.cancel()
    
    def get_birthday_config(self, guild_id):
        """Get birthday settings"""
        cfg = config.load_config()
        birthdays = cfg.get('birthdays', {})
        return birthdays.get(str(guild_id), {
            'enabled': False,
            'channel_id': None,
            'role_id': None,
            'message': '🎂 Happy Birthday {user}! 🎉',
            'birthdays': {}
        })
    
    def save_birthday_config(self, guild_id, settings):
        """Save birthday settings"""
        cfg = config.load_config()
        if 'birthdays' not in cfg:
            cfg['birthdays'] = {}
        cfg['birthdays'][str(guild_id)] = settings
        config.save_config(cfg)
    
    @tasks.loop(hours=1)
    async def check_birthdays(self):
        """Check for birthdays every hour"""
        now = datetime.now(timezone.utc)
        
        for guild in self.bot.guilds:
            settings = self.get_birthday_config(guild.id)
            
            if not settings['enabled'] or not settings['channel_id']:
                continue
            
            for user_id, birthday_str in settings['birthdays'].items():
                try:
                    bday = datetime.strptime(birthday_str, '%m-%d')
                    
                    # Check if today is birthday
                    if bday.month == now.month and bday.day == now.day and now.hour == 0:
                        channel = guild.get_channel(settings['channel_id'])
                        member = guild.get_member(int(user_id))
                        
                        if channel and member:
                            message = settings['message'].format(user=member.mention)
                            
                            embed = discord.Embed(
                                title="🎂 Happy Birthday! 🎉",
                                description=message,
                                color=0xFF69B4
                            )
                            embed.set_thumbnail(url=member.display_avatar.url)
                            
                            await channel.send(f"{member.mention}", embed=embed)
                            
                            # Add birthday role
                            if settings['role_id']:
                                role = guild.get_role(settings['role_id'])
                                if role:
                                    try:
                                        await member.add_roles(role, reason="Birthday!")
                                    except:
                                        pass
                except:
                    continue
    
    @check_birthdays.before_loop
    async def before_check_birthdays(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Birthdays(bot))

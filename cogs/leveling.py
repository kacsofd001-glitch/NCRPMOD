import discord
from discord.ext import commands
import config
import random
from datetime import datetime, timedelta, timezone

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.xp_cooldown = {}
    
    def get_leveling_config(self, guild_id):
        """Get leveling settings"""
        cfg = config.load_config()
        leveling = cfg.get('leveling', {})
        return leveling.get(str(guild_id), {
            'enabled': True,
            'xp_per_message': (15, 25),
            'cooldown': 60,
            'level_up_channel': None,
            'level_up_message': 'GG {user}, you reached level {level}!',
            'role_rewards': {}
        })
    
    def save_leveling_config(self, guild_id, settings):
        """Save leveling settings"""
        cfg = config.load_config()
        if 'leveling' not in cfg:
            cfg['leveling'] = {}
        cfg['leveling'][str(guild_id)] = settings
        config.save_config(cfg)
    
    def get_user_xp(self, guild_id, user_id):
        """Get user XP and level"""
        cfg = config.load_config()
        user_data = cfg.get('user_xp', {}).get(str(guild_id), {}).get(str(user_id), {
            'xp': 0,
            'level': 0,
            'total_xp': 0
        })
        return user_data
    
    def save_user_xp(self, guild_id, user_id, xp, level, total_xp):
        """Save user XP"""
        cfg = config.load_config()
        if 'user_xp' not in cfg:
            cfg['user_xp'] = {}
        if str(guild_id) not in cfg['user_xp']:
            cfg['user_xp'][str(guild_id)] = {}
        
        cfg['user_xp'][str(guild_id)][str(user_id)] = {
            'xp': xp,
            'level': level,
            'total_xp': total_xp
        }
        config.save_config(cfg)
    
    def xp_for_level(self, level):
        """Calculate XP needed for a level"""
        return 5 * (level ** 2) + 50 * level + 100
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        
        settings = self.get_leveling_config(message.guild.id)
        
        if not settings['enabled']:
            return
        
        # Check cooldown
        user_key = f"{message.guild.id}_{message.author.id}"
        now = datetime.now(timezone.utc)
        
        if user_key in self.xp_cooldown:
            if (now - self.xp_cooldown[user_key]).total_seconds() < settings['cooldown']:
                return
        
        self.xp_cooldown[user_key] = now
        
        # Award XP
        xp_gain = random.randint(*settings['xp_per_message'])
        user_data = self.get_user_xp(message.guild.id, message.author.id)
        
        new_xp = user_data['xp'] + xp_gain
        new_total_xp = user_data['total_xp'] + xp_gain
        current_level = user_data['level']
        
        # Check for level up
        xp_needed = self.xp_for_level(current_level + 1)
        
        if new_xp >= xp_needed:
            new_level = current_level + 1
            new_xp = new_xp - xp_needed
            
            # Save
            self.save_user_xp(message.guild.id, message.author.id, new_xp, new_level, new_total_xp)
            
            # Send level up message
            level_msg = settings['level_up_message'].format(
                user=message.author.mention,
                level=new_level
            )
            
            if settings['level_up_channel']:
                channel = self.bot.get_channel(settings['level_up_channel'])
                if channel:
                    embed = discord.Embed(
                        title="🎉 Level Up!",
                        description=level_msg,
                        color=0x00F3FF
                    )
                    embed.set_thumbnail(url=message.author.display_avatar.url)
                    await channel.send(embed=embed)
            else:
                await message.channel.send(level_msg)
            
            # Check for role rewards
            if str(new_level) in settings['role_rewards']:
                role_id = settings['role_rewards'][str(new_level)]
                role = message.guild.get_role(role_id)
                if role:
                    try:
                        await message.author.add_roles(role, reason=f"Level {new_level} reward")
                    except:
                        pass
        else:
            # Save XP
            self.save_user_xp(message.guild.id, message.author.id, new_xp, current_level, new_total_xp)

    @commands.hybrid_command(name="xp-toggle", description="Toggle the XP system for this server")
    @commands.has_permissions(manage_guild=True)
    async def xp_toggle(self, ctx):
        settings = self.get_leveling_config(ctx.guild.id)
        settings['enabled'] = not settings['enabled']
        self.save_leveling_config(ctx.guild.id, settings)
        
        status = "enabled" if settings['enabled'] else "disabled"
        await ctx.send(f"✅ XP system has been **{status}** for this server.")

async def setup(bot):
    await bot.add_cog(Leveling(bot))

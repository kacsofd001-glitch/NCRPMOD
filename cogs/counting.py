import discord
from discord.ext import commands
import config

class Counting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def get_counting_config(self, guild_id):
        """Get counting game settings"""
        cfg = config.load_config()
        counting = cfg.get('counting', {})
        return counting.get(str(guild_id), {
            'enabled': False,
            'channel_id': None,
            'current_number': 0,
            'last_user_id': None,
            'high_score': 0
        })
    
    def save_counting_config(self, guild_id, settings):
        """Save counting game settings"""
        cfg = config.load_config()
        if 'counting' not in cfg:
            cfg['counting'] = {}
        cfg['counting'][str(guild_id)] = settings
        config.save_config(cfg)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        
        settings = self.get_counting_config(message.guild.id)
        
        if not settings['enabled'] or message.channel.id != settings['channel_id']:
            return
        
        # Try to parse number
        try:
            number = int(message.content.strip())
        except:
            return
        
        expected = settings['current_number'] + 1
        
        # Check if correct number
        if number == expected and message.author.id != settings['last_user_id']:
            # Correct!
            settings['current_number'] = number
            settings['last_user_id'] = message.author.id
            
            if number > settings['high_score']:
                settings['high_score'] = number
            
            await message.add_reaction('✅')
            
            # Milestone celebrations
            if number % 100 == 0:
                await message.channel.send(f"🎉 Milestone reached! **{number}** 🎉")
            
            self.save_counting_config(message.guild.id, settings)
        else:
            # Wrong!
            await message.add_reaction('❌')
            
            fail_msg = None
            if message.author.id == settings['last_user_id']:
                fail_msg = f"❌ {message.author.mention} You can't count twice in a row!"
            else:
                fail_msg = f"❌ {message.author.mention} Wrong number! Expected **{expected}** but got **{number}**"
            
            fail_msg += f"\n**Count reset!** High score was: **{settings['current_number']}**"
            if settings['current_number'] >= settings['high_score']:
                fail_msg += " 🏆 **NEW RECORD!**"
            
            await message.channel.send(fail_msg)
            
            # Reset
            settings['current_number'] = 0
            settings['last_user_id'] = None
            self.save_counting_config(message.guild.id, settings)

async def setup(bot):
    await bot.add_cog(Counting(bot))

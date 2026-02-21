import discord
from discord.ext import commands, tasks
import random

class BotStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.status_messages = [
            ("watching", "🌐 /help | Futuristic Bot"),
            ("playing", "with 46 features 🎮"),
            ("listening", "to your commands 🎧"),
            ("watching", "{guilds} servers"),
            ("playing", "games with {users} users"),
            ("watching", "{channels} channels"),
            ("playing", "💰 Economy System"),
            ("playing", "🎮 Mini-Games"),
            ("watching", "for raids 🚨"),
            ("listening", "to your suggestions 💡"),
        ]
        self.rotate_status.start()
    
    def cog_unload(self):
        self.rotate_status.cancel()
    
    @tasks.loop(minutes=5)
    async def rotate_status(self):
        """Rotate bot status messages"""
        try:
            status_type, message = random.choice(self.status_messages)
            
            total_members = sum(guild.member_count or 0 for guild in self.bot.guilds)
            total_channels = sum(len(guild.channels) for guild in self.bot.guilds)
            
            message = message.format(
                guilds=len(self.bot.guilds),
                users=total_members,
                channels=total_channels
            )
            
            activity_map = {
                "playing": discord.ActivityType.playing,
                "watching": discord.ActivityType.watching,
                "listening": discord.ActivityType.listening,
                "competing": discord.ActivityType.competing
            }
            
            activity = discord.Activity(
                type=activity_map.get(status_type, discord.ActivityType.watching),
                name=message
            )
            
            await self.bot.change_presence(activity=activity)
        except Exception as e:
            print(f"Error rotating bot status: {e}")
    
    @rotate_status.before_loop
    async def before_rotate_status(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(BotStatus(bot))

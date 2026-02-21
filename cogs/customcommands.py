import discord
from discord.ext import commands
import json
import os

CONFIG_FILE = 'bot_config.json'

class CustomCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.custom_commands = self.load_custom_commands()
    
    def load_custom_commands(self):
        """Load custom commands from config"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    return config.get('custom_commands', {})
            except:
                return {}
        return {}
    
    def save_custom_commands(self):
        """Save custom commands to config"""
        config = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
            except:
                pass
        
        config['custom_commands'] = self.custom_commands
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen for custom command triggers"""
        if message.author.bot:
            return
        
        # Check if message starts with any guild prefix or default
        if not message.guild:
            return
        
        # Import config to get guild prefix
        import config
        prefix = config.get_guild_prefix(message.guild.id)
        
        if not message.content.startswith(prefix):
            return
        
        # Extract command name (remove prefix)
        content_after_prefix = message.content[len(prefix):].split()
        
        # If user just sent the prefix without any command, ignore
        if not content_after_prefix:
            return
        
        command_name = content_after_prefix[0].lower()
        
        # Check if it's a custom command
        if command_name in self.custom_commands:
            response = self.custom_commands[command_name]
            
            embed = discord.Embed(
                description=response,
                color=0x00F3FF
            )
            embed.set_footer(text=f"Custom Command: {command_name}")
            
            await message.channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CustomCommands(bot))

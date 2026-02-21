import discord
from discord.ext import commands
import config
from datetime import datetime, timezone

class CommandStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def get_command_stats(self, guild_id=None):
        """Get command usage statistics"""
        cfg = config.load_config()
        stats = cfg.get('command_stats', {})
        
        if guild_id:
            return stats.get(str(guild_id), {})
        return stats
    
    def record_command(self, guild_id, command_name, user_id):
        """Record command usage"""
        cfg = config.load_config()
        if 'command_stats' not in cfg:
            cfg['command_stats'] = {}
        if str(guild_id) not in cfg['command_stats']:
            cfg['command_stats'][str(guild_id)] = {
                'total_commands': 0,
                'commands': {},
                'users': {},
                'history': []
            }
        
        guild_stats = cfg['command_stats'][str(guild_id)]
        
        # Total count
        guild_stats['total_commands'] += 1
        
        # Command count
        if command_name not in guild_stats['commands']:
            guild_stats['commands'][command_name] = 0
        guild_stats['commands'][command_name] += 1
        
        # User count
        user_key = str(user_id)
        if user_key not in guild_stats['users']:
            guild_stats['users'][user_key] = 0
        guild_stats['users'][user_key] += 1
        
        # History (keep last 1000)
        guild_stats['history'].append({
            'command': command_name,
            'user_id': user_id,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
        if len(guild_stats['history']) > 1000:
            guild_stats['history'] = guild_stats['history'][-1000:]
        
        config.save_config(cfg)
    
    @commands.Cog.listener()
    async def on_command(self, ctx):
        """Track command usage"""
        if ctx.guild:
            self.record_command(ctx.guild.id, ctx.command.name, ctx.author.id)
    
    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        """Track slash command usage"""
        if interaction.type == discord.InteractionType.application_command and interaction.guild:
            self.record_command(interaction.guild.id, interaction.command.name, interaction.user.id)

async def setup(bot):
    await bot.add_cog(CommandStats(bot))

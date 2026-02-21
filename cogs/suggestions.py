import discord
from discord.ext import commands
import config

class Suggestions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def get_suggestion_config(self, guild_id):
        """Get suggestion settings"""
        cfg = config.load_config()
        suggestions = cfg.get('suggestions', {})
        return suggestions.get(str(guild_id), {
            'enabled': False,
            'channel_id': None,
            'counter': 0,
            'suggestions': {}
        })
    
    def save_suggestion_config(self, guild_id, settings):
        """Save suggestion settings"""
        cfg = config.load_config()
        if 'suggestions' not in cfg:
            cfg['suggestions'] = {}
        cfg['suggestions'][str(guild_id)] = settings
        config.save_config(cfg)
    
    async def create_suggestion(self, guild, user, suggestion_text):
        """Create a new suggestion"""
        settings = self.get_suggestion_config(guild.id)
        
        if not settings['enabled'] or not settings['channel_id']:
            return None
        
        channel = self.bot.get_channel(settings['channel_id'])
        if not channel:
            return None
        
        # Increment counter
        settings['counter'] += 1
        suggestion_id = settings['counter']
        
        # Create embed
        embed = discord.Embed(
            title=f"💡 Suggestion #{suggestion_id}",
            description=suggestion_text,
            color=0x00F3FF,
            timestamp=discord.utils.utcnow()
        )
        embed.set_author(name=user.name, icon_url=user.display_avatar.url)
        embed.add_field(name="Status", value="⏳ Pending", inline=True)
        embed.add_field(name="Votes", value="👍 0 | 👎 0", inline=True)
        
        # Send message
        message = await channel.send(embed=embed)
        await message.add_reaction("👍")
        await message.add_reaction("👎")
        
        # Save suggestion
        settings['suggestions'][str(suggestion_id)] = {
            'user_id': user.id,
            'text': suggestion_text,
            'message_id': message.id,
            'status': 'pending',
            'upvotes': 0,
            'downvotes': 0
        }
        
        self.save_suggestion_config(guild.id, settings)
        
        return suggestion_id
    
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
        
        # Check all guilds for suggestions
        for guild in self.bot.guilds:
            settings = self.get_suggestion_config(guild.id)
            
            # Find suggestion by message ID
            for sugg_id, sugg_data in settings['suggestions'].items():
                if sugg_data['message_id'] == payload.message_id:
                    # Update vote counts
                    if str(payload.emoji) == "👍":
                        sugg_data['upvotes'] += 1
                    elif str(payload.emoji) == "👎":
                        sugg_data['downvotes'] += 1
                    else:
                        return
                    
                    # Update embed
                    try:
                        channel = self.bot.get_channel(settings['channel_id'])
                        message = await channel.fetch_message(payload.message_id)
                        
                        embed = message.embeds[0]
                        embed.set_field_at(
                            1,
                            name="Votes",
                            value=f"👍 {sugg_data['upvotes']} | 👎 {sugg_data['downvotes']}",
                            inline=True
                        )
                        await message.edit(embed=embed)
                    except:
                        pass
                    
                    self.save_suggestion_config(guild.id, settings)
                    return
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        # Get guild and member (payload.member not available in remove event)
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
        
        try:
            member = await guild.fetch_member(payload.user_id)
        except:
            return
        
        if not member or member.bot:
            return
        
        # Check all guilds for suggestions
        for guild in self.bot.guilds:
            settings = self.get_suggestion_config(guild.id)
            
            # Find suggestion by message ID
            for sugg_id, sugg_data in settings['suggestions'].items():
                if sugg_data['message_id'] == payload.message_id:
                    # Update vote counts
                    if str(payload.emoji) == "👍" and sugg_data['upvotes'] > 0:
                        sugg_data['upvotes'] -= 1
                    elif str(payload.emoji) == "👎" and sugg_data['downvotes'] > 0:
                        sugg_data['downvotes'] -= 1
                    else:
                        return
                    
                    # Update embed
                    try:
                        channel = self.bot.get_channel(settings['channel_id'])
                        message = await channel.fetch_message(payload.message_id)
                        
                        embed = message.embeds[0]
                        embed.set_field_at(
                            1,
                            name="Votes",
                            value=f"👍 {sugg_data['upvotes']} | 👎 {sugg_data['downvotes']}",
                            inline=True
                        )
                        await message.edit(embed=embed)
                    except:
                        pass
                    
                    self.save_suggestion_config(guild.id, settings)
                    return

async def setup(bot):
    await bot.add_cog(Suggestions(bot))

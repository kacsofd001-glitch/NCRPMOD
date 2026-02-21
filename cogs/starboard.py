import discord
from discord.ext import commands
import config

class Starboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def get_starboard_config(self, guild_id):
        """Get starboard settings"""
        cfg = config.load_config()
        starboards = cfg.get('starboards', {})
        return starboards.get(str(guild_id), {
            'enabled': False,
            'channel_id': None,
            'threshold': 5,
            'emoji': '⭐',
            'starred_messages': {}
        })
    
    def save_starboard_config(self, guild_id, settings):
        """Save starboard settings"""
        cfg = config.load_config()
        if 'starboards' not in cfg:
            cfg['starboards'] = {}
        cfg['starboards'][str(guild_id)] = settings
        config.save_config(cfg)
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member and payload.member.bot:
            return
        
        settings = self.get_starboard_config(payload.guild_id)
        
        if not settings['enabled'] or str(payload.emoji) != settings['emoji']:
            return
        
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
        
        try:
            channel = guild.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
        except:
            return
        
        # Count star reactions
        star_count = 0
        for reaction in message.reactions:
            if str(reaction.emoji) == settings['emoji']:
                star_count = reaction.count
                break
        
        if star_count >= settings['threshold']:
            starboard_channel = guild.get_channel(settings['channel_id'])
            if not starboard_channel:
                return
            
            message_key = str(payload.message_id)
            
            # Check if already starred
            if message_key in settings['starred_messages']:
                # Update existing starboard message
                try:
                    starboard_msg = await starboard_channel.fetch_message(settings['starred_messages'][message_key])
                    embed = starboard_msg.embeds[0]
                    embed.title = f"{settings['emoji']} {star_count} | #{channel.name}"
                    await starboard_msg.edit(embed=embed)
                except:
                    pass
            else:
                # Create new starboard message
                embed = discord.Embed(
                    title=f"{settings['emoji']} {star_count} | #{channel.name}",
                    description=message.content or "*No text content*",
                    color=0xFFD700,
                    timestamp=message.created_at
                )
                embed.set_author(name=message.author.name, icon_url=message.author.display_avatar.url)
                embed.add_field(name="Source", value=f"[Jump to Message]({message.jump_url})", inline=False)
                
                if message.attachments:
                    embed.set_image(url=message.attachments[0].url)
                
                starboard_msg = await starboard_channel.send(embed=embed)
                settings['starred_messages'][message_key] = starboard_msg.id
                self.save_starboard_config(payload.guild_id, settings)

async def setup(bot):
    await bot.add_cog(Starboard(bot))

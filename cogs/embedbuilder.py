import discord
from discord.ext import commands
import config
import json

class EmbedBuilder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def create_embed_from_data(self, data):
        """Create embed from JSON data"""
        embed = discord.Embed()
        
        if 'title' in data:
            embed.title = data['title']
        if 'description' in data:
            embed.description = data['description']
        if 'color' in data:
            embed.color = int(data['color'].replace('#', ''), 16) if isinstance(data['color'], str) else data['color']
        if 'footer' in data:
            embed.set_footer(text=data['footer'])
        if 'thumbnail' in data:
            embed.set_thumbnail(url=data['thumbnail'])
        if 'image' in data:
            embed.set_image(url=data['image'])
        if 'author' in data:
            embed.set_author(name=data['author'])
        if 'fields' in data:
            for field in data['fields']:
                embed.add_field(
                    name=field.get('name', 'Field'),
                    value=field.get('value', 'Value'),
                    inline=field.get('inline', True)
                )
        
        return embed
    
    def get_saved_embeds(self, guild_id):
        """Get saved embeds"""
        cfg = config.load_config()
        embeds = cfg.get('saved_embeds', {})
        return embeds.get(str(guild_id), {})
    
    def save_embed(self, guild_id, name, embed_data):
        """Save embed template"""
        cfg = config.load_config()
        if 'saved_embeds' not in cfg:
            cfg['saved_embeds'] = {}
        if str(guild_id) not in cfg['saved_embeds']:
            cfg['saved_embeds'][str(guild_id)] = {}
        
        cfg['saved_embeds'][str(guild_id)][name] = embed_data
        config.save_config(cfg)

async def setup(bot):
    await bot.add_cog(EmbedBuilder(bot))

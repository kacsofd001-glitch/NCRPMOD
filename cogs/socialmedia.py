import discord
from discord.ext import commands
import config

class SocialMedia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def get_social_config(self, guild_id):
        """Get social media integration settings"""
        cfg = config.load_config()
        social = cfg.get('social_media', {})
        return social.get(str(guild_id), {
            'enabled': False,
            'announcement_channel_id': None,
            'twitter_enabled': False,
            'instagram_enabled': False,
            'post_format': '{content}'
        })
    
    def save_social_config(self, guild_id, settings):
        """Save social media settings"""
        cfg = config.load_config()
        if 'social_media' not in cfg:
            cfg['social_media'] = {}
        cfg['social_media'][str(guild_id)] = settings
        config.save_config(cfg)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Monitor announcement channel for social media posts"""
        if message.author.bot or not message.guild:
            return
        
        settings = self.get_social_config(message.guild.id)
        
        if not settings['enabled'] or message.channel.id != settings['announcement_channel_id']:
            return
        
        # This would integrate with Twitter/Instagram APIs
        # For now, we log the intent
        embed = discord.Embed(
            title="📱 Social Media Post Ready",
            description=f"This message would be posted to social media:\n\n{message.content}",
            color=0x1DA1F2
        )
        
        if settings['twitter_enabled']:
            embed.add_field(name="Twitter", value="✅ Enabled", inline=True)
        if settings['instagram_enabled']:
            embed.add_field(name="Instagram", value="✅ Enabled", inline=True)
        
        await message.channel.send(embed=embed, delete_after=15)

async def setup(bot):
    await bot.add_cog(SocialMedia(bot))

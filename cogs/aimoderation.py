import discord
from discord.ext import commands
import config
import os
import aiohttp

class AIMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv('OPENAI_API_KEY')
    
    def get_aimod_config(self, guild_id):
        """Get AI moderation settings"""
        cfg = config.load_config()
        aimod = cfg.get('aimod', {})
        return aimod.get(str(guild_id), {
            'enabled': False,
            'toxicity_threshold': 0.7,
            'auto_delete': True,
            'warn_users': True,
            'excluded_channels': []
        })
    
    def save_aimod_config(self, guild_id, settings):
        """Save AI moderation settings"""
        cfg = config.load_config()
        if 'aimod' not in cfg:
            cfg['aimod'] = {}
        cfg['aimod'][str(guild_id)] = settings
        config.save_config(cfg)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        
        settings = self.get_aimod_config(message.guild.id)
        
        if not settings['enabled']:
            return
        
        if message.channel.id in settings['excluded_channels']:
            return
        
        if not self.api_key:
            return
        
        is_toxic = await self.check_toxicity(message.content)
        
        if is_toxic:
            if settings['auto_delete']:
                try:
                    await message.delete()
                except:
                    pass
            
            if settings['warn_users']:
                embed = discord.Embed(
                    title="⚠️ Message Warning",
                    description=f"{message.author.mention}, your message was flagged for inappropriate content.",
                    color=0xFF0000
                )
                await message.channel.send(embed=embed, delete_after=10)
            
            logging_cog = self.bot.get_cog('Logging')
            if logging_cog:
                log_channel_id = logging_cog.get_log_channel(message.guild.id)
                if log_channel_id:
                    channel = message.guild.get_channel(log_channel_id)
                    if channel:
                        log_embed = discord.Embed(
                            title="🤖 AI Mod: Toxic Message Detected",
                            description=f"**User:** {message.author.mention}\n**Channel:** {message.channel.mention}",
                            color=0xFF0000
                        )
                        log_embed.add_field(name="Content", value=message.content[:1024], inline=False)
                        await channel.send(embed=log_embed)
    
    async def check_toxicity(self, text):
        """Use OpenAI to check message toxicity"""
        if not self.api_key or len(text) < 5:
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
                
                data = {
                    'model': 'gpt-3.5-turbo',
                    'messages': [
                        {
                            'role': 'system',
                            'content': 'You are a content moderation assistant. Respond with only "toxic" or "safe".'
                        },
                        {
                            'role': 'user',
                            'content': f'Is this message toxic, hateful, or inappropriate? Message: "{text}"'
                        }
                    ],
                    'max_tokens': 10,
                    'temperature': 0.3
                }
                
                async with session.post(
                    'https://api.openai.com/v1/chat/completions',
                    headers=headers,
                    json=data
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        response = result['choices'][0]['message']['content'].lower()
                        return 'toxic' in response
        except:
            pass
        
        return False

async def setup(bot):
    await bot.add_cog(AIMod(bot))

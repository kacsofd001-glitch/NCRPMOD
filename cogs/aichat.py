import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import config
from translations import get_text, get_guild_language
import os

class AIChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
    
    @app_commands.command(name="aichat", description="Configure AI chat for a channel / AI csevegés beállítása")
    @app_commands.describe(
        channel="Channel for AI chat / Csatorna az AI csevegéshez",
        language="AI response language (en/hu) / AI válasz nyelve",
        enabled="Enable or disable / Bekapcsolás vagy kikapcsolás"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def aichat_config(
        self, 
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        language: str,
        enabled: bool
    ):
        await interaction.response.defer()
        
        if language not in ['en', 'hu']:
            await interaction.followup.send("❌ Language must be 'en' or 'hu'", ephemeral=True)
            return
        
        if not self.openai_api_key:
            await interaction.followup.send("❌ OpenAI API key not configured! Please contact the bot owner.", ephemeral=True)
            return
        
        cfg = config.load_config()
        if 'ai_chat_channels' not in cfg:
            cfg['ai_chat_channels'] = {}
        
        channel_id = str(channel.id)
        
        if enabled:
            cfg['ai_chat_channels'][channel_id] = {
                'guild_id': str(interaction.guild.id),
                'language': language,
                'enabled': True
            }
            config.save_config(cfg)
            
            embed = discord.Embed(
                title="✅ AI Chat Enabled",
                description=f"AI chat enabled in {channel.mention}\n\nThe bot will respond to all messages in this channel with AI-powered responses.",
                color=discord.Color.green()
            )
            embed.add_field(name="Language", value=language.upper(), inline=True)
            embed.add_field(name="Status", value="✅ Enabled", inline=True)
            embed.add_field(name="Note", value="Messages starting with ! or / will be ignored", inline=False)
            
            await interaction.followup.send(embed=embed)
        else:
            if channel_id in cfg.get('ai_chat_channels', {}):
                del cfg['ai_chat_channels'][channel_id]
                config.save_config(cfg)
            
            embed = discord.Embed(
                title="🔇 AI Chat Disabled",
                description=f"AI chat disabled in {channel.mention}",
                color=discord.Color.red()
            )
            
            await interaction.followup.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        if not message.content or not message.content.strip():
            return
        
        if message.content.startswith('!') or message.content.startswith('/'):
            return
        
        if not self.openai_api_key:
            return
        
        is_bot_mentioned = self.bot.user.mentioned_in(message) and not message.mention_everyone
        
        if not is_bot_mentioned:
            return
        
        guild_lang = get_guild_language(str(message.guild.id))
        ai_language = guild_lang if guild_lang in ['en', 'hu'] else 'en'
        
        async with message.channel.typing():
            try:
                clean_content = message.content.replace(f'<@{self.bot.user.id}>', '').replace(f'<@!{self.bot.user.id}>', '').strip()
                
                response_text = await self.get_ai_response(
                    clean_content,
                    ai_language
                )
                
                if len(response_text) > 2000:
                    chunks = [response_text[i:i+2000] for i in range(0, len(response_text), 2000)]
                    for chunk in chunks:
                        await message.reply(chunk, mention_author=False)
                else:
                    await message.reply(response_text, mention_author=False)
                    
            except Exception as e:
                print(f"AI Chat Error: {type(e).__name__}: {str(e)}")
                error_msg = "❌ Sorry, I couldn't process that message."
                error_str = str(e).lower()
                
                if "429" in str(e) or "quota" in error_str or "insufficient_quota" in error_str:
                    error_msg = "❌ AI chat is temporarily unavailable (API quota exceeded). Please contact the bot owner to add OpenAI credits."
                elif "rate_limit" in error_str or "rate limit" in error_str:
                    error_msg = "❌ Rate limit reached. Please try again in a few moments."
                elif "invalid" in error_str or "401" in str(e):
                    error_msg = "❌ API key issue. Please contact an administrator."
                elif "timeout" in error_str:
                    error_msg = "❌ Request timed out. Please try again."
                
                await message.reply(error_msg, mention_author=False)
    
    async def get_ai_response(self, user_message: str, language: str) -> str:
        """Get AI response from OpenAI API"""
        
        system_prompt = {
            'en': "You are a helpful and friendly Discord bot assistant. Keep responses concise and helpful.",
            'hu': "Egy segítőkész és barátságos Discord bot asszisztens vagy. Tömör és hasznos válaszokat adj."
        }
        
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": system_prompt.get(language, system_prompt['en'])},
                {"role": "user", "content": user_message}
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['message']['content']
                else:
                    error_text = await response.text()
                    print(f"OpenAI API Error {response.status}: {error_text}")
                    raise Exception(f"OpenAI API error {response.status}: {error_text[:100]}")

async def setup(bot):
    await bot.add_cog(AIChat(bot))

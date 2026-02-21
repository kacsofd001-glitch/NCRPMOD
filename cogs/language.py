import discord
from discord import app_commands
from discord.ext import commands
import translations

class Language(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='setlang')
    @commands.has_permissions(administrator=True)
    async def set_language(self, ctx, lang: str):
        """Set the server language (en/hu)"""
        lang = lang.lower()
        
        if lang not in ['en', 'hu']:
            await ctx.send(translations.get_text(ctx.guild.id, 'invalid_language'))
            return
        
        if translations.set_guild_language(ctx.guild.id, lang):
            lang_name = translations.get_text(ctx.guild.id, f'language_{lang}', lang=lang)
            
            embed = discord.Embed(
                title=translations.get_text(ctx.guild.id, 'language_set', lang=lang),
                description=translations.get_text(ctx.guild.id, 'language_set_desc', lang_name, lang=lang),
                color=discord.Color.green()
            )
            
            embed.add_field(
                name=translations.get_text(ctx.guild.id, 'current_language', lang=lang),
                value="🇬🇧 English" if lang == 'en' else "🇭🇺 Magyar",
                inline=False
            )
            
            await ctx.send(embed=embed)
            # Sync commands to update descriptions if needed (though discord handles slash choices dynamically)
        else:
            await ctx.send(translations.get_text(ctx.guild.id, 'error_setting_language'))
    
    @app_commands.command(name="setlang", description="Set server language / Szerver nyelv beállítása")
    @app_commands.describe(
        language="Language to use / Használandó nyelv (en/hu)"
    )
    @app_commands.choices(language=[
        app_commands.Choice(name="🇬🇧 English", value="en"),
        app_commands.Choice(name="🇭🇺 Magyar", value="hu")
    ])
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_setlang(self, interaction: discord.Interaction, language: app_commands.Choice[str]):
        lang = language.value
        
        if translations.set_guild_language(interaction.guild.id, lang):
            lang_name = translations.get_text(interaction.guild.id, f'language_{lang}', lang=lang)
            
            embed = discord.Embed(
                title=translations.get_text(interaction.guild.id, 'language_set', lang=lang),
                description=translations.get_text(interaction.guild.id, 'language_set_desc', lang_name, lang=lang),
                color=discord.Color.green()
            )
            
            embed.add_field(
                name=translations.get_text(interaction.guild.id, 'current_language', lang=lang),
                value="🇬🇧 English" if lang == 'en' else "🇭🇺 Magyar",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(translations.get_text(interaction.guild.id, 'error_setting_language'), ephemeral=True)

async def setup(bot):
    await bot.add_cog(Language(bot))

import discord
from discord.ext import commands
from discord import app_commands
import config

class TempVoice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def get_tempvoice_config(self, guild_id):
        """Get temp voice settings"""
        cfg = config.load_config()
        tempvoice = cfg.get('tempvoice', {})
        return tempvoice.get(str(guild_id), {
            'enabled': False,
            'create_channel_id': None,
            'category_id': None,
            'channel_name': '{user}\'s Channel',
            'temp_channels': []
        })
    
    def save_tempvoice_config(self, guild_id, settings):
        """Save temp voice settings"""
        cfg = config.load_config()
        if 'tempvoice' not in cfg:
            cfg['tempvoice'] = {}
        cfg['tempvoice'][str(guild_id)] = settings
        config.save_config(cfg)
    
    @app_commands.command(name="setupvoice", description="Setup temporary voice channels / Ideiglenes hangcsatornák beállítása")
    @app_commands.describe(channel="The 'Join to Create' voice channel / A 'Csatlakozz a létrehozáshoz' csatorna", category="The category for new channels / Az új csatornák kategóriája")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_setupvoice(self, interaction: discord.Interaction, channel: discord.VoiceChannel, category: discord.CategoryChannel = None):
        settings = self.get_tempvoice_config(interaction.guild.id)
        settings['enabled'] = True
        settings['create_channel_id'] = channel.id
        settings['category_id'] = category.id if category else None
        self.save_tempvoice_config(interaction.guild.id, settings)
        
        embed = discord.Embed(
            title="🔊 Temp Voice Setup / Hangcsatorna beállítás",
            description=f"✅ System enabled! Join {channel.mention} to create a channel.\n✅ Rendszer aktiválva! Csatlakozz a(z) {channel.mention} csatornához.",
            color=0x00F3FF
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="voicename", description="Change your temp channel name / Ideiglenes csatorna nevének módosítása")
    @app_commands.describe(name="New name for the channel / A csatorna új neve")
    async def slash_voicename(self, interaction: discord.Interaction, name: str):
        if not isinstance(interaction.user, discord.Member):
            return
            
        settings = self.get_tempvoice_config(interaction.guild.id)
        if interaction.user.voice and interaction.user.voice.channel and interaction.user.voice.channel.id in settings.get('temp_channels', []):
            await interaction.user.voice.channel.edit(name=name)
            await interaction.response.send_message(f"✅ Channel name updated to: **{name}**", ephemeral=True)
        else:
            await interaction.response.send_message("❌ You must be in your own temporary channel! / Saját ideiglenes csatornádban kell lenned!", ephemeral=True)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        settings = self.get_tempvoice_config(member.guild.id)
        
        if not settings['enabled']:
            return
        
        # User joined the "create channel" voice channel
        if after.channel and after.channel.id == settings['create_channel_id']:
            category = member.guild.get_channel(settings['category_id'])
            
            channel_name = settings['channel_name'].format(user=member.name)
            
            # Create temp channel
            temp_channel = await member.guild.create_voice_channel(
                name=channel_name,
                category=category,
                reason="Temporary voice channel"
            )
            
            # Move user to temp channel
            try:
                await member.move_to(temp_channel)
            except:
                pass
            
            # Track temp channel
            settings['temp_channels'].append(temp_channel.id)
            self.save_tempvoice_config(member.guild.id, settings)
        
        # Check if temp channel is now empty
        if before.channel and before.channel.id in settings['temp_channels']:
            if len(before.channel.members) == 0:
                try:
                    await before.channel.delete(reason="Temporary voice channel empty")
                    settings['temp_channels'].remove(before.channel.id)
                    self.save_tempvoice_config(member.guild.id, settings)
                except:
                    pass

async def setup(bot):
    await bot.add_cog(TempVoice(bot))

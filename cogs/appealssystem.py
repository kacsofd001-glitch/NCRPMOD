import discord
from discord.ext import commands
import config
from datetime import datetime, timezone

class Appeals(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def get_appeals_config(self, guild_id):
        """Get appeals settings"""
        cfg = config.load_config()
        appeals = cfg.get('appeals', {})
        return appeals.get(str(guild_id), {
            'enabled': False,
            'channel_id': None,
            'appeals': {},
            'next_id': 1
        })
    
    def save_appeals_config(self, guild_id, settings):
        """Save appeals settings"""
        cfg = config.load_config()
        if 'appeals' not in cfg:
            cfg['appeals'] = {}
        cfg['appeals'][str(guild_id)] = settings
        config.save_config(cfg)
    
    async def submit_appeal(self, guild_id, user_id, reason):
        """Submit a ban appeal"""
        settings = self.get_appeals_config(guild_id)
        
        if not settings['enabled']:
            return None, "Appeals system is not enabled on this server!"
        
        appeal_id = settings['next_id']
        settings['next_id'] += 1
        
        appeal_data = {
            'user_id': user_id,
            'reason': reason,
            'status': 'pending',
            'submitted_at': datetime.now(timezone.utc).isoformat(),
            'votes': {'approve': [], 'deny': []}
        }
        
        settings['appeals'][str(appeal_id)] = appeal_data
        self.save_appeals_config(guild_id, settings)
        
        guild = self.bot.get_guild(guild_id)
        if guild and settings['channel_id']:
            channel = guild.get_channel(settings['channel_id'])
            if channel:
                embed = discord.Embed(
                    title=f"📋 Ban Appeal #{appeal_id}",
                    description=f"**User ID:** {user_id}\n**Reason:** {reason}",
                    color=0xFFA500,
                    timestamp=datetime.now(timezone.utc)
                )
                
                view = AppealVoteView(appeal_id, guild_id, self)
                await channel.send(embed=embed, view=view)
        
        return appeal_id, "Appeal submitted successfully!"

class AppealVoteView(discord.ui.View):
    def __init__(self, appeal_id, guild_id, cog):
        super().__init__(timeout=None)
        self.appeal_id = appeal_id
        self.guild_id = guild_id
        self.cog = cog
    
    @discord.ui.button(label="✅ Approve", style=discord.ButtonStyle.success)
    async def approve_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message("❌ You need Ban Members permission to vote!", ephemeral=True)
            return
        
        settings = self.cog.get_appeals_config(self.guild_id)
        appeal = settings['appeals'].get(str(self.appeal_id))
        
        if not appeal:
            await interaction.response.send_message("❌ Appeal not found!", ephemeral=True)
            return
        
        user_id = str(interaction.user.id)
        
        if user_id in appeal['votes']['approve']:
            await interaction.response.send_message("❌ You already voted to approve!", ephemeral=True)
            return
        
        if user_id in appeal['votes']['deny']:
            appeal['votes']['deny'].remove(user_id)
        
        appeal['votes']['approve'].append(user_id)
        self.cog.save_appeals_config(self.guild_id, settings)
        
        await interaction.response.send_message(f"✅ Vote recorded! Approvals: {len(appeal['votes']['approve'])}", ephemeral=True)
    
    @discord.ui.button(label="❌ Deny", style=discord.ButtonStyle.danger)
    async def deny_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message("❌ You need Ban Members permission to vote!", ephemeral=True)
            return
        
        settings = self.cog.get_appeals_config(self.guild_id)
        appeal = settings['appeals'].get(str(self.appeal_id))
        
        if not appeal:
            await interaction.response.send_message("❌ Appeal not found!", ephemeral=True)
            return
        
        user_id = str(interaction.user.id)
        
        if user_id in appeal['votes']['deny']:
            await interaction.response.send_message("❌ You already voted to deny!", ephemeral=True)
            return
        
        if user_id in appeal['votes']['approve']:
            appeal['votes']['approve'].remove(user_id)
        
        appeal['votes']['deny'].append(user_id)
        self.cog.save_appeals_config(self.guild_id, settings)
        
        await interaction.response.send_message(f"✅ Vote recorded! Denials: {len(appeal['votes']['deny'])}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Appeals(bot))

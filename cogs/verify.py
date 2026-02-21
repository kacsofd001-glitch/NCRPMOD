import discord
from discord.ext import commands
from discord import app_commands
import config
from translations import get_text
from datetime import datetime, timezone, timedelta

class VerifyButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Verify", style=discord.ButtonStyle.green, emoji="✅", custom_id="verify_button")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        cfg = config.load_config()
        guild_id = str(interaction.guild.id)
        
        verify_config = cfg.get('verify_config', {}).get(guild_id)
        if not verify_config:
            await interaction.response.send_message("❌ Verification not configured!", ephemeral=True)
            return
        
        min_account_age = cfg.get('min_account_age_days', {}).get(guild_id, 7)
        
        account_age = (datetime.now(timezone.utc) - interaction.user.created_at).days
        
        if account_age < min_account_age:
            await interaction.response.send_message(
                f"❌ Your account is too new! Minimum age: {min_account_age} days. Your account: {account_age} days.",
                ephemeral=True
            )
            return
        
        roles_to_add = verify_config.get('roles_to_add', [])
        roles_to_remove = verify_config.get('roles_to_remove', [])
        
        added_roles = []
        removed_roles = []
        
        for role_id in roles_to_add:
            role = interaction.guild.get_role(int(role_id))
            if role and role not in interaction.user.roles:
                try:
                    await interaction.user.add_roles(role)
                    added_roles.append(role.name)
                except:
                    pass
        
        for role_id in roles_to_remove:
            role = interaction.guild.get_role(int(role_id))
            if role and role in interaction.user.roles:
                try:
                    await interaction.user.remove_roles(role)
                    removed_roles.append(role.name)
                except:
                    pass
        
        embed = discord.Embed(
            title="✅ Verified Successfully!",
            description=f"Welcome {interaction.user.mention}! You have been verified.",
            color=0x00F3FF
        )
        
        if added_roles:
            embed.add_field(name="Roles Added", value=", ".join(added_roles), inline=False)
        if removed_roles:
            embed.add_field(name="Roles Removed", value=", ".join(removed_roles), inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        log_embed = discord.Embed(
            title="✅ Member Verified",
            description=f"{interaction.user.mention} has been verified",
            color=0x00F3FF,
            timestamp=datetime.now(timezone.utc)
        )
        log_embed.add_field(name="User", value=f"{interaction.user} ({interaction.user.id})", inline=False)
        log_embed.add_field(name="Account Age", value=f"{account_age} days", inline=True)
        
        log_channel_id = cfg.get('log_channel_id')
        if log_channel_id:
            log_channel = interaction.guild.get_channel(log_channel_id)
            if log_channel:
                await log_channel.send(embed=log_embed)

class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_view(VerifyButton())
    
    @app_commands.command(name="setupverify", description="Setup verification system / Ellenőrzési rendszer beállítása")
    @app_commands.describe(
        channel="Channel for verification panel / Csatorna az ellenőrző panelhez",
        roles_to_add="Roles to add (comma separated) / Hozzáadandó szerepek (vesszővel elválasztva)",
        roles_to_remove="Roles to remove (comma separated) / Eltávolítandó szerepek (vesszővel elválasztva)"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_verify(
        self, 
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        roles_to_add: str = "",
        roles_to_remove: str = ""
    ):
        await interaction.response.defer()
        
        cfg = config.load_config()
        guild_id = str(interaction.guild.id)
        
        if 'verify_config' not in cfg:
            cfg['verify_config'] = {}
        
        add_role_ids = []
        remove_role_ids = []
        
        if roles_to_add.strip():
            for role_mention in roles_to_add.split(','):
                role_mention = role_mention.strip()
                if role_mention.startswith('<@&') and role_mention.endswith('>'):
                    role_id = role_mention[3:-1]
                    role = interaction.guild.get_role(int(role_id))
                    if role:
                        add_role_ids.append(str(role.id))
        
        if roles_to_remove.strip():
            for role_mention in roles_to_remove.split(','):
                role_mention = role_mention.strip()
                if role_mention.startswith('<@&') and role_mention.endswith('>'):
                    role_id = role_mention[3:-1]
                    role = interaction.guild.get_role(int(role_id))
                    if role:
                        remove_role_ids.append(str(role.id))
        
        cfg['verify_config'][guild_id] = {
            'channel_id': str(channel.id),
            'roles_to_add': add_role_ids,
            'roles_to_remove': remove_role_ids
        }
        config.save_config(cfg)
        
        min_age = cfg.get('min_account_age_days', {}).get(guild_id, 7)
        
        verify_embed = discord.Embed(
            title="✅ Verification",
            description=f"Click the button below to verify yourself!\n\n**Requirements:**\n• Account must be at least {min_age} days old",
            color=0x8B00FF
        )
        verify_embed.add_field(
            name="What happens when you verify?",
            value="You will gain access to the server and receive your member roles.",
            inline=False
        )
        
        view = VerifyButton()
        await channel.send(embed=verify_embed, view=view)
        
        config_embed = discord.Embed(
            title="✅ Verification System Configured",
            description=f"Verification panel sent to {channel.mention}",
            color=0x00F3FF
        )
        config_embed.add_field(name="Minimum Account Age", value=f"{min_age} days", inline=False)
        
        if add_role_ids:
            role_names = [interaction.guild.get_role(int(rid)).name for rid in add_role_ids if interaction.guild.get_role(int(rid))]
            config_embed.add_field(name="Roles to Add", value=", ".join(role_names) if role_names else "None", inline=False)
        
        if remove_role_ids:
            role_names = [interaction.guild.get_role(int(rid)).name for rid in remove_role_ids if interaction.guild.get_role(int(rid))]
            config_embed.add_field(name="Roles to Remove", value=", ".join(role_names) if role_names else "None", inline=False)
        
        await interaction.followup.send(embed=config_embed)
    
    @commands.command(name='setupverify')
    @commands.has_permissions(administrator=True)
    async def setup_verify_prefix(self, ctx, channel: discord.TextChannel, *, roles: str = ""):
        await ctx.send("⚠️ Please use the slash command `/setupverify` for easier configuration!")

async def setup(bot):
    await bot.add_cog(Verify(bot))

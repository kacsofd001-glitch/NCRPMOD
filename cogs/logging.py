import discord
from discord.ext import commands
from datetime import datetime, timezone
import config

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def get_log_channel_id(self, guild_id):
        cfg = config.load_config()
        guild_logs = cfg.get('guild_log_channels', {})
        return guild_logs.get(str(guild_id))

    async def send_log(self, guild, embed):
        log_channel_id = self.get_log_channel_id(guild.id)
        
        if log_channel_id:
            log_channel = self.bot.get_channel(log_channel_id)
            if log_channel:
                await log_channel.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot or not message.guild:
            return
        
        embed = discord.Embed(
            title="🗑️ Message Deleted",
            description=f"**Author:** {message.author.mention}\n**Channel:** {message.channel.mention}",
            color=0xFF006E,
            timestamp=datetime.now(timezone.utc)
        )
        embed.add_field(
            name="Content",
            value=message.content[:1024] if message.content else "*No content*",
            inline=False
        )
        embed.set_footer(text=f"User ID: {message.author.id}")
        
        await self.send_log(message.guild, embed)
    
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or not before.guild or before.content == after.content:
            return
        
        embed = discord.Embed(
            title="📝 Message Edited",
            description=f"**Author:** {before.author.mention}\n**Channel:** {before.channel.mention}",
            color=0xFF006E,
            timestamp=datetime.now(timezone.utc)
        )
        embed.add_field(
            name="Before",
            value=before.content[:512] if before.content else "*No content*",
            inline=False
        )
        embed.add_field(
            name="After",
            value=after.content[:512] if after.content else "*No content*",
            inline=False
        )
        embed.set_footer(text=f"User ID: {before.author.id}")
        
        await self.send_log(before.guild, embed)
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        cfg = config.load_config()
        min_age_days = cfg.get('min_account_age_days', 7)
        
        account_age = datetime.now(timezone.utc) - member.created_at
        age_in_days = account_age.days
        
        is_alt = age_in_days < min_age_days
        
        embed = discord.Embed(
            title="🚨 Possible Alt Account Detected - Member Joined" if is_alt else "📥 Member Joined",
            description=f"**User:** {member.mention} ({member})",
            color=0xFF006E if is_alt else 0x00F3FF,
            timestamp=datetime.now(timezone.utc)
        )
        embed.add_field(
            name="Account Created",
            value=f"{member.created_at.strftime('%Y-%m-%d %H:%M:%S')} UTC",
            inline=True
        )
        embed.add_field(
            name="Account Age",
            value=f"{age_in_days} days old" + (f" ⚠️ (Required: {min_age_days}+ days)" if is_alt else ""),
            inline=True
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"User ID: {member.id} | Total Members: {member.guild.member_count}")
        
        await self.send_log(member.guild, embed)
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        embed = discord.Embed(
            title="📤 Member Left",
            description=f"**User:** {member.mention} ({member})",
            color=0xFF006E,
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"User ID: {member.id} | Total Members: {member.guild.member_count}")
        
        await self.send_log(member.guild, embed)
    
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        embed = discord.Embed(
            title="🔨 Member Banned",
            description=f"**User:** {user.mention} ({user})",
            color=discord.Color.dark_red(),
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f"User ID: {user.id}")
        
        await self.send_log(guild, embed)
    
    @commands.command(name='setlog')
    @commands.has_permissions(administrator=True)
    async def set_log_channel(self, ctx, channel: discord.TextChannel):
        cfg = config.load_config()
        if 'guild_log_channels' not in cfg:
            cfg['guild_log_channels'] = {}
        cfg['guild_log_channels'][str(ctx.guild.id)] = channel.id
        config.save_config(cfg)
        
        embed = discord.Embed(
            title="✅ Log Channel Set",
            description=f"Log channel has been set to {channel.mention} for this server.",
            color=0x00F3FF
        )
        await ctx.send(embed=embed)
        
        welcome_embed = discord.Embed(
            title="📋 Logging System Activated",
            description="This channel will now receive all bot logs for this server, including:\n• Message deletions and edits\n• Member joins and leaves\n• Bans and kicks\n• Anti-alt detections\n• Moderation actions",
            color=0x8B00FF
        )
        await channel.send(embed=welcome_embed)

async def setup(bot):
    await bot.add_cog(Logging(bot))

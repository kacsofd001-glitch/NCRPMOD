import discord
from discord.ext import commands
import config

class AdvancedLogging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def get_log_config(self, guild_id):
        """Get advanced logging settings"""
        cfg = config.load_config()
        logs = cfg.get('advanced_logging', {})
        return logs.get(str(guild_id), {
            'enabled': False,
            'message_edits': True,
            'message_deletes': True,
            'voice_activity': True,
            'role_changes': True,
            'username_changes': True,
            'channel_id': None
        })
    
    def save_log_config(self, guild_id, settings):
        """Save advanced logging settings"""
        cfg = config.load_config()
        if 'advanced_logging' not in cfg:
            cfg['advanced_logging'] = {}
        cfg['advanced_logging'][str(guild_id)] = settings
        config.save_config(cfg)
    
    async def send_log(self, guild_id, embed):
        """Send log to channel"""
        settings = self.get_log_config(guild_id)
        if not settings['enabled'] or not settings['channel_id']:
            return
        
        channel = self.bot.get_channel(settings['channel_id'])
        if channel:
            try:
                await channel.send(embed=embed)
            except:
                pass
    
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content:
            return
        
        settings = self.get_log_config(before.guild.id)
        if not settings['message_edits']:
            return
        
        embed = discord.Embed(
            title="✏️ Message Edited",
            color=0xFFA500,
            timestamp=discord.utils.utcnow()
        )
        embed.set_author(name=before.author.name, icon_url=before.author.display_avatar.url)
        embed.add_field(name="Before", value=before.content[:1024] or "*No content*", inline=False)
        embed.add_field(name="After", value=after.content[:1024] or "*No content*", inline=False)
        embed.add_field(name="Channel", value=before.channel.mention, inline=True)
        embed.add_field(name="Jump", value=f"[Link]({after.jump_url})", inline=True)
        
        await self.send_log(before.guild.id, embed)
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        
        settings = self.get_log_config(message.guild.id)
        if not settings['message_deletes']:
            return
        
        embed = discord.Embed(
            title="🗑️ Message Deleted",
            description=message.content[:2048] or "*No content*",
            color=0xFF0000,
            timestamp=discord.utils.utcnow()
        )
        embed.set_author(name=message.author.name, icon_url=message.author.display_avatar.url)
        embed.add_field(name="Channel", value=message.channel.mention, inline=True)
        embed.add_field(name="User ID", value=message.author.id, inline=True)
        
        if message.attachments:
            embed.add_field(name="Attachments", value=f"{len(message.attachments)} file(s)", inline=True)
        
        await self.send_log(message.guild.id, embed)
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        settings = self.get_log_config(member.guild.id)
        if not settings['voice_activity']:
            return
        
        if before.channel != after.channel:
            if before.channel is None:
                # Joined voice
                embed = discord.Embed(
                    title="🔊 Voice Channel Joined",
                    description=f"{member.mention} joined {after.channel.mention}",
                    color=0x00FF00,
                    timestamp=discord.utils.utcnow()
                )
            elif after.channel is None:
                # Left voice
                embed = discord.Embed(
                    title="🔇 Voice Channel Left",
                    description=f"{member.mention} left {before.channel.mention}",
                    color=0xFF0000,
                    timestamp=discord.utils.utcnow()
                )
            else:
                # Moved channels
                embed = discord.Embed(
                    title="🔄 Voice Channel Moved",
                    description=f"{member.mention} moved from {before.channel.mention} to {after.channel.mention}",
                    color=0xFFA500,
                    timestamp=discord.utils.utcnow()
                )
            
            embed.set_author(name=member.name, icon_url=member.display_avatar.url)
            await self.send_log(member.guild.id, embed)
    
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        settings = self.get_log_config(before.guild.id)
        
        # Role changes
        if settings['role_changes'] and before.roles != after.roles:
            added = set(after.roles) - set(before.roles)
            removed = set(before.roles) - set(after.roles)
            
            embed = discord.Embed(
                title="🎭 Role Update",
                color=0x8B00FF,
                timestamp=discord.utils.utcnow()
            )
            embed.set_author(name=after.name, icon_url=after.display_avatar.url)
            
            if added:
                embed.add_field(name="✅ Roles Added", value=" ".join(r.mention for r in added), inline=False)
            if removed:
                embed.add_field(name="❌ Roles Removed", value=" ".join(r.mention for r in removed), inline=False)
            
            await self.send_log(before.guild.id, embed)
        
        # Username changes
        if settings['username_changes'] and (before.name != after.name or before.nick != after.nick):
            embed = discord.Embed(
                title="👤 User Update",
                color=0x00F3FF,
                timestamp=discord.utils.utcnow()
            )
            embed.set_author(name=after.name, icon_url=after.display_avatar.url)
            
            if before.name != after.name:
                embed.add_field(name="Username Change", value=f"{before.name} → {after.name}", inline=False)
            if before.nick != after.nick:
                embed.add_field(name="Nickname Change", value=f"{before.nick or 'None'} → {after.nick or 'None'}", inline=False)
            
            await self.send_log(before.guild.id, embed)

async def setup(bot):
    await bot.add_cog(AdvancedLogging(bot))

import discord
from discord.ext import commands
from datetime import datetime, timezone
import platform
import os

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Use Render domain for production
        self.custom_domain = 'https://shadowmod.onrender.com'
        # Add /dashboard path to URL
        self.dashboard_url = f'{self.custom_domain}/dashboard'
    
    @commands.command(name='serverinfo', aliases=['si'])
    async def serverinfo(self, ctx):
        """Show server information"""
        from translations import get_text
        guild = ctx.guild
        
        # Count channels by type
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        
        # Get boost info
        boost_level = guild.premium_tier
        boost_count = guild.premium_subscription_count
        
        # Get role count (excluding @everyone)
        role_count = len(guild.roles) - 1
        
        # Create embed
        embed = discord.Embed(
            title=f"⚡ {guild.name} " + get_text(guild.id, 'servers_title'),
            description=f"**ID:** `{guild.id}`",
            color=0x00F3FF,
            timestamp=datetime.now(timezone.utc)
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        # Server Stats
        embed.add_field(
            name="👑 " + get_text(guild.id, 'moderator'),
            value=f"{guild.owner.mention}\n`{guild.owner}`",
            inline=True
        )
        embed.add_field(
            name="📅 " + get_text(guild.id, 'invite_expires'),
            value=f"<t:{int(guild.created_at.timestamp())}:R>",
            inline=True
        )
        embed.add_field(
            name="🌟 Boost Level",
            value=f"Level {boost_level}\n{boost_count} boosts",
            inline=True
        )
        
        # Member Stats
        embed.add_field(
            name="👥 Members",
            value=f"**Total:** {guild.member_count}\n**Humans:** {len([m for m in guild.members if not m.bot])}\n**Bots:** {len([m for m in guild.members if m.bot])}",
            inline=True
        )
        
        # Channel Stats
        embed.add_field(
            name="💬 " + get_text(guild.id, 'channel') + " ({})".format(text_channels + voice_channels),
            value=f"**Text:** {text_channels}\n**Voice:** {voice_channels}\n**Categories:** {categories}",
            inline=True
        )
        
        # Role Stats
        embed.add_field(
            name="🎭 Roles",
            value=f"{role_count} roles",
            inline=True
        )
        
        # Verification level
        verification = str(guild.verification_level).replace('_', ' ').title()
        embed.add_field(
            name="🔒 Security",
            value=f"**Verification:** {verification}\n**2FA Required:** {'Yes' if guild.mfa_level else 'No'}",
            inline=True
        )
        
        # Features
        features = []
        if "COMMUNITY" in guild.features:
            features.append("✅ Community")
        if "VERIFIED" in guild.features:
            features.append("✅ Verified")
        if "PARTNERED" in guild.features:
            features.append("✅ Partnered")
        if "DISCOVERABLE" in guild.features:
            features.append("✅ Discoverable")
        
        if features:
            embed.add_field(
                name="✨ Features",
                value="\n".join(features),
                inline=True
            )
        
        if guild.banner:
            embed.set_image(url=guild.banner.url)
        
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='botinfo', aliases=['bi'])
    async def botinfo(self, ctx):
        """Show bot information and statistics"""
        from translations import get_text
        # Calculate uptime
        uptime = datetime.now(timezone.utc) - self.bot.start_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        
        uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
        
        # Calculate stats
        total_members = sum(guild.member_count for guild in self.bot.guilds)
        total_channels = sum(len(guild.channels) for guild in self.bot.guilds)
        
        embed = discord.Embed(
            title="⚡ SHADOW-MOD ✨ | Bot Info",
            description="**Made by MoonlightVFX**\nFuturistic bot with AI integration & real-time web dashboard",
            color=0x8B00FF,
            timestamp=datetime.now(timezone.utc)
        )
        
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        # Bot Stats
        embed.add_field(
            name="📊 Statistics",
            value=f"**Servers:** {len(self.bot.guilds)}\n**Users:** {total_members:,}\n**Channels:** {total_channels:,}",
            inline=True
        )
        
        embed.add_field(
            name="⏱️ Uptime",
            value=uptime_str,
            inline=True
        )
        
        embed.add_field(
            name="🐍 Python Version",
            value=platform.python_version(),
            inline=True
        )
        
        # Features
        features = [
            "✅ Dual Prefix (!  and /)",
            "✅ 20+ Slash Commands",
            "✅ Multilingual (EN/HU)",
            "✅ AI Chat Assistant",
            "✅ Ticket System",
            "✅ Anti-Alt Detection",
            "✅ Advanced Moderation",
            "✅ Interactive Games",
            "✅ Poll & Giveaway System",
            "✅ Role Management",
            "✅ Webhook Logging",
            "✅ Member Verification",
            "✅ Live Web Dashboard"
        ]
        
        embed.add_field(
            name="✨ Features",
            value="\n".join(features[:7]),
            inline=True
        )
        
        embed.add_field(
            name="🚀 More Features",
            value="\n".join(features[7:]),
            inline=True
        )
        
        embed.add_field(
            name="🔗 Links",
            value=f"[📖 Command List]({self.custom_domain}/help)\n[📊 Web Dashboard]({self.dashboard_url})\n[💬 Support Server](https://discord.gg/w6s6qA4E7E)\n[➕ Add Bot](https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands)",
            inline=True
        )
        
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='userinfo', aliases=['ui', 'whois'])
    async def userinfo(self, ctx, member: discord.Member = None):
        """Show detailed user information with badges"""
        member = member or ctx.author
        
        # Create embed
        embed = discord.Embed(
            title=f"⚡ User Information",
            color=0x00F3FF,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Set user avatar as main image (top)
        embed.set_author(name=str(member), icon_url=member.display_avatar.url)
        embed.set_thumbnail(url=member.display_avatar.url)
        
        # Basic Info
        embed.add_field(
            name="👤 User Info",
            value=f"**Username:** {member.name}\n**Display Name:** {member.display_name}\n**ID:** `{member.id}`\n**Bot:** {'Yes ✅' if member.bot else 'No ❌'}",
            inline=True
        )
        
        # Account Creation
        account_age = datetime.now(timezone.utc) - member.created_at
        embed.add_field(
            name="📅 Account Created",
            value=f"<t:{int(member.created_at.timestamp())}:F>\n({account_age.days} days ago)",
            inline=True
        )
        
        # Join Date
        if member.joined_at:
            join_age = datetime.now(timezone.utc) - member.joined_at
            embed.add_field(
                name="📥 Joined Server",
                value=f"<t:{int(member.joined_at.timestamp())}:F>\n({join_age.days} days ago)",
                inline=True
            )
        
        # Badges
        badges = []
        flags = member.public_flags
        
        if flags.staff:
            badges.append("<:staff:> Discord Staff")
        if flags.partner:
            badges.append("<:partner:> Partnered Server Owner")
        if flags.hypesquad:
            badges.append("<:hypesquad:> HypeSquad Events")
        if flags.hypesquad_balance:
            badges.append("⚖️ HypeSquad Balance")
        if flags.hypesquad_bravery:
            badges.append("🛡️ HypeSquad Bravery")
        if flags.hypesquad_brilliance:
            badges.append("💎 HypeSquad Brilliance")
        if flags.bug_hunter:
            badges.append("🐛 Bug Hunter")
        if flags.bug_hunter_level_2:
            badges.append("🐛 Bug Hunter Level 2")
        if flags.verified_bot_developer:
            badges.append("⚙️ Early Verified Bot Developer")
        if flags.early_supporter:
            badges.append("💖 Early Supporter")
        if flags.active_developer:
            badges.append("🔧 Active Developer")
        if member.premium_since:
            badges.append(f"💎 Server Booster (since <t:{int(member.premium_since.timestamp())}:R>)")
        
        if badges:
            embed.add_field(
                name="🏅 Badges",
                value="\n".join(badges),
                inline=False
            )
        
        # Roles
        if len(member.roles) > 1:  # Exclude @everyone
            roles = [role.mention for role in reversed(member.roles[1:])]  # Skip @everyone
            roles_text = ", ".join(roles[:10])  # Show first 10 roles
            if len(member.roles) > 11:
                roles_text += f" ... and {len(member.roles) - 11} more"
            
            embed.add_field(
                name=f"🎭 Roles ({len(member.roles) - 1})",
                value=roles_text,
                inline=False
            )
        
        # Key Permissions
        perms = []
        if member.guild_permissions.administrator:
            perms.append("👑 Administrator")
        if member.guild_permissions.manage_guild:
            perms.append("⚙️ Manage Server")
        if member.guild_permissions.manage_channels:
            perms.append("📝 Manage Channels")
        if member.guild_permissions.manage_roles:
            perms.append("🎭 Manage Roles")
        if member.guild_permissions.ban_members:
            perms.append("🔨 Ban Members")
        if member.guild_permissions.kick_members:
            perms.append("👢 Kick Members")
        
        if perms:
            embed.add_field(
                name="🔑 Key Permissions",
                value="\n".join(perms),
                inline=False
            )
        
        # Status
        status_emoji = {
            discord.Status.online: "🟢 Online",
            discord.Status.idle: "🟡 Idle",
            discord.Status.dnd: "🔴 Do Not Disturb",
            discord.Status.offline: "⚫ Offline"
        }
        
        embed.add_field(
            name="📱 Status",
            value=status_emoji.get(member.status, "⚫ Unknown"),
            inline=True
        )
        
        # Top role color
        if member.top_role.color.value != 0:
            embed.color = member.top_role.color
        
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='support')
    async def support(self, ctx):
        """Get the support server invite link"""
        embed = discord.Embed(
            title="💬 Support Server",
            description="Join our support server for help, updates, and more!",
            color=0x8B00FF
        )
        
        embed.add_field(
            name="🔗 Invite Link",
            value="[Click here to join!](https://discord.gg/w6s6qA4E7E)",
            inline=False
        )
        
        embed.add_field(
            name="✨ What you'll find:",
            value="• Get help with bot commands\n• Report bugs and issues\n• Suggest new features\n• Get updates and announcements\n• Chat with other users",
            inline=False
        )
        
        embed.set_footer(text="We'd love to see you there! 💜")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='webpage', aliases=['web', 'dashboard'])
    async def webpage(self, ctx):
        """Get the link to the bot's live web dashboard"""
        embed = discord.Embed(
            title="🌐 Live Web Dashboard",
            description="Check out the bot's real-time statistics on our futuristic web page!",
            color=0x00F3FF
        )
        
        embed.add_field(
            name="🔗 Dashboard Link",
            value=f"[Click here to view]({self.dashboard_url})",
            inline=False
        )
        
        embed.add_field(
            name="📊 Features:",
            value="• Real-time bot statistics\n• Server, user & channel counts\n• Live uptime tracking\n• Futuristic cyberpunk theme\n• Auto-refreshing data",
            inline=False
        )
        
        embed.set_footer(text="Dashboard updates every 5 seconds ⚡")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Info(bot))

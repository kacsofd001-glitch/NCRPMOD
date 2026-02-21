print("🔄 Loading bot modules...", flush=True)

import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
import json
import config

print("📁 Loading environment variables...", flush=True)
load_dotenv()
print("✅ Environment variables loaded", flush=True)

intents = discord.Intents.all()

# Shared stats file for web server
STATS_FILE = 'bot_stats.json'

def get_prefix(bot, message):
    """Dynamic prefix per guild"""
    if message.guild:
        return config.get_guild_prefix(message.guild.id)
    return '!'

class DiscordBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=get_prefix,
            intents=intents,
            help_command=None
        )
        self.start_time = datetime.now(timezone.utc)
        
    async def setup_hook(self):
        # TEMPORARY: Only load slash_commands to test if cogs are the issue
        print("⚠️ TESTING MODE: Only loading slash_commands cog")
        cogs_to_load = [
            'cogs.tickets',
            'cogs.antialt',
            'cogs.logging',
            'cogs.moderation',
            'cogs.games',
            'cogs.fun',
            'cogs.polls',
            'cogs.roles',
            'cogs.giveaways',
            'cogs.nameauto',
            'cogs.webhook_logging',
            'cogs.language',
            'cogs.aichat',
            'cogs.verify',
            'cogs.info',
            'cogs.music',
            'cogs.admin',
            'cogs.customcommands',
            'cogs.automod',
            'cogs.welcome',
            'cogs.reactionroles',
            'cogs.leveling',
            'cogs.reminders',
            'cogs.afk',
            'cogs.serverstats',
            'cogs.suggestions',
            'cogs.economy',
            'cogs.starboard',
            'cogs.counting',
            'cogs.birthdays',
            'cogs.confessions',
            'cogs.modmail',
            'cogs.antiraid',
            'cogs.advancedlogging',
            'cogs.rolepersist',
            'cogs.tempbans',
            'cogs.embedbuilder',
            'cogs.tempvoice',
            'cogs.streamalerts',
            'cogs.serverbackup',
            'cogs.playlists',
            'cogs.growthtracking',
            'cogs.achievements',
            'cogs.socialmedia',
            'cogs.commandstats',
            'cogs.minigames',
            'cogs.connectfour',
            'cogs.reputation',
            'cogs.events',
            'cogs.setupwizard',
            'cogs.interactivehelp',
            'cogs.advancedeconomy',
            'cogs.aimoderation',
            'cogs.voiceanalytics',
            'cogs.appealssystem',
            'cogs.memeeconomy',
            'cogs.botstatus',
            'cogs.webhooks',
            'cogs.hungariandefense',
            'cogs.slash_commands'
        ]
        
        loaded_count = 0
        for cog in cogs_to_load:
            try:
                await self.load_extension(cog)
                loaded_count += 1
                print(f"✅ Loaded: {cog}")
            except Exception as e:
                print(f"❌ Failed to load {cog}: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n✅ All cogs loaded! ({loaded_count}/{len(cogs_to_load)})")
        
    async def on_ready(self):
        print(f'✅ Bot is ready! Logged in as {self.user}')
        print(f'✅ Bot ID: {self.user.id}')
        print('------')
        print(f'📊 Connected to {len(self.guilds)} guilds')
        
        try:
            synced = await self.tree.sync()
            print(f'✅ Synced {len(synced)} slash commands')
        except Exception as e:
            print(f'❌ Failed to sync commands: {e}')
        
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="🌐 /help | Futuristic Bot"
            )
        )
        
        # Update stats file for web server
        self.update_stats_file()
    
    def update_stats_file(self):
        """Update bot stats for web server"""
        total_members = sum(guild.member_count or 0 for guild in self.guilds)
        total_channels = sum(len(guild.channels) for guild in self.guilds)
        
        stats = {
            'start_time': self.start_time.isoformat(),
            'guilds': len(self.guilds),
            'users': total_members,
            'channels': total_channels,
            'status': 'online'
        }
        
        try:
            with open(STATS_FILE, 'w') as f:
                json.dump(stats, f)
        except:
            pass

bot = DiscordBot()

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    """Global error handler for slash commands"""
    print(f"❌ Slash command error: {error}")
    try:
        if interaction.response.is_done():
            await interaction.followup.send(f"Error: {str(error)}", ephemeral=True)
        else:
            await interaction.response.send_message(f"Error: {str(error)}", ephemeral=True)
    except Exception as e:
        print(f"Could not send error message: {e}")

@bot.event
async def on_interaction(interaction: discord.Interaction):
    """Debug: Log all interactions"""
    print(f"🔵 Interaction received: {interaction.type} - {interaction.data if hasattr(interaction, 'data') else 'Unknown'}")

@bot.command(name='help')
async def help_command(ctx):
    # Get current prefix for this server
    prefix = config.get_guild_prefix(ctx.guild.id) if ctx.guild else '!'
    
    # Get language and check if we should use interactive help
    from translations import get_text, get_guild_language
    guild_id = ctx.guild.id
    lang = get_guild_language(guild_id)
    
    interactive_help = bot.get_cog('InteractiveHelp')
    if interactive_help:
        embed = discord.Embed(
            title=get_text(guild_id, 'help_title', lang=lang),
            description=get_text(guild_id, 'help_description', lang=lang),
            color=0x00F3FF
        )
        embed.set_thumbnail(url=bot.user.display_avatar.url)
        embed.add_field(
            name=get_text(guild_id, 'help_engagement', lang=lang),
            value=(
                "Click a button below to explore commands by category!\n\n"
                "🛡️ **Moderation** - Manage your server\n"
                "💰 **Economy** - Currency & shop system\n"
                "🎮 **Games** - Fun mini-games\n"
                "🎭 **Fun** - Entertainment commands\n"
                "⚙️ **Utility** - Helpful tools\n"
                "📊 **Stats** - Analytics & tracking"
            ),
            inline=False
        )
        embed.set_footer(text=get_text(guild_id, 'help_footer', lang=lang))
        
        from cogs.interactivehelp import HelpView
        view = HelpView(bot, guild_id)
        await ctx.send(embed=embed, view=view)
        return

    # Fallback legacy help (if cog not loaded)
    embed = discord.Embed(
        title="⚡ SHADOW-MOD ✨ | COMMAND DATABASE",
        description=f"━━━━━━━━━━━━━━━━━━━━━━━━━\n`Next-Gen Discord Moderation System`\n**Current Prefix:** `{prefix}` | **Slash:** `/`\n━━━━━━━━━━━━━━━━━━━━━━━━━",
        color=0x00F3FF  # Neon cyan
    )
    
    embed.add_field(
        name="📊 INFORMATION SYSTEMS",
        value="`/serverinfo` - Server statistics & details\n`/botinfo` - Bot features & uptime\n`/userinfo [@user]` - User profile with badges\n`/support` - Support server link\n`/webpage` - Live web dashboard",
        inline=False
    )
    
    embed.add_field(
        name="🔐 SECURITY & VERIFICATION",
        value="`/setupverify` - Deploy verification system\n`/setlog #channel` - Set log channel for alerts",
        inline=False
    )
    
    embed.add_field(
        name="🛡️ ANTI-ALT SYSTEM",
        value="`Auto-detects new accounts on join`\n`/setaltage <days>` - Set min account age (default: 7d)\nAlerts sent to log channel automatically",
        inline=False
    )
    
    embed.add_field(
        name="⚔️ MODERATION MATRIX",
        value="`/ban` - Ban user\n`/kick` - Kick user\n`/mute` `/unmute` - Mute/unmute user\n`/tempmute <user> <time>` - Discord timeout (max 28d)\n`/purge <1-100>` - Bulk message deletion\n`/warn` - Warn user\n`/lock` `/unlock` - Lock/unlock channel",
        inline=False
    )
    
    embed.add_field(
        name="🧠 AI NEURAL LINK",
        value="**@mention me** to activate AI assistant\n`Responds in EN/HU based on server language`",
        inline=False
    )
    
    embed.add_field(
        name="🎵 MUSIC SYSTEM (🎥 YouTube • 🟢 Spotify • ☁️ SoundCloud)",
        value=f"`/play <song>` - Play music from any platform\n`/pause` `/resume` - Pause/resume playback\n`/skip` - Skip to next song\n`/stop` - Stop and disconnect\n`/queue` - Show music queue\n`/nowplaying` - Current track info\n`/loop` - Toggle loop mode\n`/volume <0-100>` - Adjust volume\n*Also supports `{prefix}` prefix for all commands*",
        inline=False
    )
    
    embed.add_field(
        name="🎮 ENTERTAINMENT SYSTEMS",
        value="`/rps` - Rock-Paper-Scissors\n`/tictactoe` - Tic-Tac-Toe\n`/meme` - Generate memes\n`/8ball` - Magic 8-ball\n`/coinflip` - Flip coin\n`/dice` - Roll dice",
        inline=False
    )
    
    embed.add_field(
        name="🎁 ENGAGEMENT PROTOCOLS",
        value="`/poll` - Interactive polls\n`/giveaway` - Prize systems\n`/ticket` - Support tickets\n`/createrole` - Role management",
        inline=False
    )
    
    embed.add_field(
        name="🏷️ NAME AUTOMATION",
        value="`/setprefix <@role> <prefix>` - Set role prefix\n`/removeprefix <@role>` - Remove role prefix\n`/viewprefixes` - View all prefixes",
        inline=False
    )
    
    embed.add_field(
        name="🛡️ AUTO-MODERATION",
        value="`/automod enable` - Enable auto-moderation\n`/automod settings` - View configuration\n`Auto-detects: spam, bad words, links, caps, emoji spam`",
        inline=False
    )
    
    embed.add_field(
        name="👋 WELCOME & GOODBYE",
        value="`/setwelcome #channel [message]` - Setup welcomes\n`/setgoodbye <enabled> [message]` - Setup goodbyes\n`Supports: {user}, {server}, {count} placeholders`",
        inline=False
    )
    
    embed.add_field(
        name="🎭 REACTION ROLES",
        value="`/reactionrole <msg_id> <emoji> <@role>` - Setup reaction roles\n`Users get roles by reacting to messages`",
        inline=False
    )
    
    embed.add_field(
        name="⭐ LEVELING & XP SYSTEM",
        value="`/rank [@user]` - Check level & XP\n`/leaderboard` - Server top 10 rankings\n`Earn XP by chatting, level up to unlock rewards!`",
        inline=False
    )
    
    embed.add_field(
        name="⏰ REMINDERS & AFK",
        value="`/remind <time> <message>` - Set reminder (1h, 30m, 2d)\n`/afk [reason]` - Set AFK status\n`Auto-notifies when mentioned while AFK`",
        inline=False
    )
    
    embed.add_field(
        name="📊 SERVER ANALYTICS",
        value="`/serverstats` - Full server statistics\n`Tracks: messages, activity, top users, growth`",
        inline=False
    )
    
    embed.add_field(
        name="💡 SUGGESTION SYSTEM",
        value="`/setupsuggestions #channel` - Enable suggestions\n`/suggest <idea>` - Submit suggestion\n`Community votes with 👍 👎 reactions`",
        inline=False
    )
    
    embed.add_field(
        name="🌐 SYSTEM CONFIGURATION",
        value="`/setlang <en/hu>` - Language switch\n`/setbotprefix <prefix>` - Change bot prefix\n`/setwebhook <url>` - Logging webhook\n`/ping` - Check latency",
        inline=False
    )
    
    embed.add_field(
        name="👑 OWNER COMMANDS (Bot Owner Only)",
        value="`/servers` - List all servers (name + ID)\n`/createinvite <server_id>` - Create permanent invite\n`/addcc <name> <response>` - Add custom command\n`/rcc <name>` - Remove custom command\n`/mcc <name> <response>` - Modify custom command",
        inline=False
    )
    
    embed.add_field(
        name="🌐 WEB RESOURCES",
        value="[📖 Full Command List](https://shadowmod.onrender.com/help)\n[📊 Live Dashboard](https://shadowmod.onrender.com/dashboard)",
        inline=False
    )
    
    embed.set_footer(text="⚡ Made by MoonlightVFX | 75+ Slash Commands Ready ⚡")
    embed.set_thumbnail(url=ctx.bot.user.display_avatar.url)
    
    await ctx.send(embed=embed)

@bot.command(name='ping')
async def ping_command(ctx):
    latency = round(bot.latency * 1000)
    
    # Determine latency color
    if latency < 100:
        color = 0x00F3FF  # Neon cyan - excellent
        status = "⚡ OPTIMAL"
    elif latency < 200:
        color = 0x8B00FF  # Neon purple - good
        status = "✅ STABLE"
    else:
        color = 0xFF006E  # Neon pink - slow
        status = "⚠️ DEGRADED"
    
    embed = discord.Embed(
        title=f"📡 SYSTEM RESPONSE | {status}",
        description=f"```ansi\n\u001b[1;36mLatency: {latency}ms\u001b[0m\n```",
        color=color
    )
    embed.add_field(name="Status", value=status, inline=True)
    embed.add_field(name="Response Time", value=f"{latency}ms", inline=True)
    embed.set_footer(text="⚡ Neural Network Active")
    
    await ctx.send(embed=embed)

# ... a többi kódod felette változatlan ...

if __name__ == '__main__':
    print("\n🚀 Starting bot standalone mode...", flush=True)
    TOKEN = os.getenv('DISCORD_TOKEN')
    if not TOKEN:
        print("❌ ERROR: DISCORD_TOKEN not found!", flush=True)
        exit(1)
    
    try:
        # Ez a sor CSAK akkor fut le, ha a python main.py-t indítod
        bot.run(TOKEN)
    except Exception as e:
        print(f"❌ Bot crashed: {e}", flush=True)
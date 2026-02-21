import discord
from discord import app_commands
from discord.ext import commands
import config
import translations
from datetime import datetime, timezone, timedelta

class SlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print(f"✅ SlashCommands cog initialized")
    
    @app_commands.command(name="ping", description="Check bot response time")
    async def slash_ping(self, interaction: discord.Interaction):
        """Simple ping command to test bot responsiveness"""
        try:
            latency = round(self.bot.latency * 1000)
            guild_id = interaction.guild.id if interaction.guild else 0
            lang = translations.get_guild_language(guild_id)
            print(f"🔵 /ping command received from {interaction.user}")
            await interaction.response.send_message(translations.get_text(guild_id, 'pong', latency, lang=lang))
            print(f"✅ /ping response sent")
        except Exception as e:
            print(f"❌ Error in ping: {e}")
            import traceback
            traceback.print_exc()
    
    @app_commands.command(name="help", description="Show help menu / Súgó menü")
    async def slash_help(self, interaction: discord.Interaction):
        # Defer immediately to avoid timeout
        await interaction.response.defer()
        
        try:
            help_cog = self.bot.get_cog('InteractiveHelp')
            if help_cog:
                # Call the help function but use followup instead
                from translations import get_text, get_guild_language
                guild_id = interaction.guild.id
                lang = get_guild_language(guild_id)
                
                embed = discord.Embed(
                    title=get_text(guild_id, 'help_title', lang=lang),
                    description=get_text(guild_id, 'help_description', lang=lang),
                    color=0x00F3FF
                )
                
                embed.set_thumbnail(url=self.bot.user.display_avatar.url)
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
                view = HelpView(self.bot, guild_id)
                await interaction.followup.send(embed=embed, view=view)
            else:
                await interaction.followup.send(translations.get_text(guild_id, 'help_unavailable'), ephemeral=True)
        except Exception as e:
            print(f"Error in help command: {e}")
            await interaction.followup.send(translations.get_text(guild_id, 'error_loading_help', str(e)), ephemeral=True)
    
    @app_commands.command(name="ticket", description="Create a ticket panel / Jegy panel létrehozása")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_ticket(self, interaction: discord.Interaction):
        ticket_cog = self.bot.get_cog('Tickets')
        if ticket_cog:
            view = ticket_cog.TicketView()
            self.bot.add_view(view)
            
            guild_id = interaction.guild.id
            
            embed = discord.Embed(
                title=translations.get_text(guild_id, 'ticket_title'),
                description=translations.get_text(guild_id, 'ticket_description'),
                color=0x8B00FF
            )
            embed.add_field(
                name=translations.get_text(guild_id, 'ticket_how_it_works'),
                value=translations.get_text(guild_id, 'ticket_steps'),
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, view=view)
    
    @app_commands.command(name="meme", description="Get a random meme / Véletlen meme lekérése")
    async def slash_meme(self, interaction: discord.Interaction):
        import random
        from urllib.parse import quote
        import aiohttp
        
        guild_id = interaction.guild.id
        await interaction.response.defer()
        
        # Use a more reliable public meme API for random memes
        meme_apis = [
            "https://meme-api.com/gimme",
            "https://meme-api.com/gimme/wholesomememes",
            "https://meme-api.com/gimme/memes"
        ]
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(random.choice(meme_apis), timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        data = await response.json()
                        meme_url = data.get('url')
                        meme_title = data.get('title', translations.get_text(guild_id, 'meme_title'))
                        
                        embed = discord.Embed(
                            title=meme_title,
                            color=discord.Color.random()
                        )
                        embed.set_image(url=meme_url)
                        embed.set_footer(text=f"r/{data.get('subreddit')} | {translations.get_text(guild_id, 'generated_meme')}")
                        
                        await interaction.followup.send(embed=embed)
                        return
                    else:
                        raise Exception("Meme API error")
        except Exception as e:
            # Fallback to local templates if API fails
            lang = translations.get_guild_language(guild_id)
            fun_cog = self.bot.get_cog('Fun')
            
            if fun_cog:
                templates = fun_cog.meme_templates_hu if lang == 'hu' else fun_cog.meme_templates_en
                template_name, top_text, bottom_text = random.choice(templates)
                
                top_text_encoded = quote(top_text, safe='')
                bottom_text_encoded = quote(bottom_text, safe='')
                
                meme_url = f"https://api.memegen.link/images/{template_name}/{top_text_encoded}/{bottom_text_encoded}.png"
                
                embed = discord.Embed(
                    title=translations.get_text(guild_id, 'meme_title'),
                    color=discord.Color.random()
                )
                embed.set_image(url=meme_url)
                embed.set_footer(text=translations.get_text(guild_id, 'generated_meme'))
                
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send("❌ Meme feature unavailable")
    
    @app_commands.command(name="8ball", description="Ask the magic 8-ball / Kérdezd a varázs labdát")
    @app_commands.describe(question="Your question / A kérdésed")
    async def slash_8ball(self, interaction: discord.Interaction, question: str):
        import random
        
        guild_id = interaction.guild.id
        responses = translations.get_text(guild_id, '8ball_responses')
        
        embed = discord.Embed(
            title=translations.get_text(guild_id, 'magic_8ball'),
            color=discord.Color.purple()
        )
        embed.add_field(name=translations.get_text(guild_id, 'question'), value=question, inline=False)
        embed.add_field(name=translations.get_text(guild_id, 'answer'), value=random.choice(responses), inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="coinflip", description="Flip a coin / Pénzfeldobás")
    async def slash_coinflip(self, interaction: discord.Interaction):
        import random
        
        guild_id = interaction.guild.id
        lang = translations.get_guild_language(guild_id)
        
        result_key = 'heads' if random.choice([True, False]) else 'tails'
        result = translations.get_text(guild_id, result_key)
        
        embed = discord.Embed(
            title=translations.get_text(guild_id, 'coin_flip'),
            description=translations.get_text(guild_id, 'coin_result', result),
            color=discord.Color.gold()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="ban", description="Ban a user / Felhasználó kitiltása")
    @app_commands.describe(user="User mention or ID / Felhasználó mention vagy ID", reason="Reason / Indok")
    @app_commands.checks.has_permissions(ban_members=True)
    async def slash_ban(self, interaction: discord.Interaction, user: str, reason: str = None):
        guild_id = interaction.guild.id
        
        try:
            # Try to convert string to user ID or extract from mention
            user_id = None
            if user.startswith('<@') and user.endswith('>'):
                user_id = int(user.strip('<@!>'))
            else:
                try:
                    user_id = int(user)
                except ValueError:
                    await interaction.response.send_message(translations.get_text(guild_id, 'invalid_user'), ephemeral=True)
                    return
            
            # Fetch the user
            try:
                target_user = await interaction.guild.fetch_member(user_id)
            except:
                target_user = await self.bot.fetch_user(user_id)
            
            await interaction.guild.ban(target_user, reason=reason)
            
            embed = discord.Embed(
                title=translations.get_text(guild_id, 'user_banned'),
                description=translations.get_text(guild_id, 'user_banned_desc', target_user.mention),
                color=0xFF006E
            )
            if reason:
                embed.add_field(name=translations.get_text(guild_id, 'reason'), value=reason, inline=False)
            embed.add_field(name=translations.get_text(guild_id, 'moderator'), value=interaction.user.mention, inline=True)
            
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(translations.get_text(guild_id, 'ban_failed', str(e)), ephemeral=True)
    
    @app_commands.command(name="kick", description="Kick a user / Felhasználó kirúgása")
    @app_commands.describe(user="User mention or ID / Felhasználó mention vagy ID", reason="Reason / Indok")
    @app_commands.checks.has_permissions(kick_members=True)
    async def slash_kick(self, interaction: discord.Interaction, user: str, reason: str = None):
        guild_id = interaction.guild.id
        
        try:
            # Try to convert string to user ID or extract from mention
            user_id = None
            if user.startswith('<@') and user.endswith('>'):
                user_id = int(user.strip('<@!>'))
            else:
                try:
                    user_id = int(user)
                except ValueError:
                    await interaction.response.send_message(translations.get_text(guild_id, 'invalid_user'), ephemeral=True)
                    return
            
            # Fetch the member
            target_user = await interaction.guild.fetch_member(user_id)
            
            await target_user.kick(reason=reason)
            
            embed = discord.Embed(
                title=translations.get_text(guild_id, 'user_kicked'),
                description=translations.get_text(guild_id, 'user_kicked_desc', target_user.mention),
                color=0xFF006E
            )
            if reason:
                embed.add_field(name=translations.get_text(guild_id, 'reason'), value=reason, inline=False)
            embed.add_field(name=translations.get_text(guild_id, 'moderator'), value=interaction.user.mention, inline=True)
            
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(translations.get_text(guild_id, 'kick_failed', str(e)), ephemeral=True)
    
    @app_commands.command(name="mute", description="Mute a user / Felhasználó némítása")
    @app_commands.describe(user="User mention or ID / Felhasználó mention vagy ID")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def slash_mute(self, interaction: discord.Interaction, user: str):
        guild_id_int = interaction.guild.id
        guild_id = str(guild_id_int)
        
        try:
            # Try to convert string to user ID or extract from mention
            user_id = None
            if user.startswith('<@') and user.endswith('>'):
                user_id = int(user.strip('<@!>'))
            else:
                try:
                    user_id = int(user)
                except ValueError:
                    await interaction.response.send_message(translations.get_text(guild_id_int, 'invalid_user'), ephemeral=True)
                    return
            
            # Fetch the member
            target_user = await interaction.guild.fetch_member(user_id)
            
            cfg = config.load_config()
            muted_role_id = cfg.get('muted_roles', {}).get(guild_id)
            
            if not muted_role_id:
                muted_role = await interaction.guild.create_role(name="Muted", color=discord.Color.dark_gray())
                cfg.setdefault('muted_roles', {})[guild_id] = muted_role.id
                config.save_config(cfg)
                
                for channel in interaction.guild.channels:
                    await channel.set_permissions(muted_role, send_messages=False, speak=False)
            else:
                muted_role = interaction.guild.get_role(muted_role_id)
            
            await target_user.add_roles(muted_role)
            
            embed = discord.Embed(
                title=translations.get_text(guild_id_int, 'user_muted'),
                description=translations.get_text(guild_id_int, 'user_muted_desc', target_user.mention),
                color=discord.Color.dark_gray()
            )
            
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="unmute", description="Unmute a user / Felhasználó visszahangosítása")
    @app_commands.describe(user="User mention or ID / Felhasználó mention vagy ID")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def slash_unmute(self, interaction: discord.Interaction, user: str):
        guild_id_int = interaction.guild.id
        guild_id = str(guild_id_int)
        
        try:
            # Try to convert string to user ID or extract from mention
            user_id = None
            if user.startswith('<@') and user.endswith('>'):
                user_id = int(user.strip('<@!>'))
            else:
                try:
                    user_id = int(user)
                except ValueError:
                    await interaction.response.send_message(translations.get_text(guild_id_int, 'invalid_user'), ephemeral=True)
                    return
            
            # Fetch the member
            target_user = await interaction.guild.fetch_member(user_id)
            
            cfg = config.load_config()
            muted_role_id = cfg.get('muted_roles', {}).get(guild_id)
            
            if not muted_role_id:
                await interaction.response.send_message(translations.get_text(guild_id_int, 'no_muted_role'), ephemeral=True)
                return
            
            muted_role = interaction.guild.get_role(muted_role_id)
            if muted_role in target_user.roles:
                await target_user.remove_roles(muted_role)
                
                embed = discord.Embed(
                    title=translations.get_text(guild_id_int, 'user_unmuted'),
                    description=translations.get_text(guild_id_int, 'user_unmuted_desc', target_user.mention),
                    color=0x00F3FF
                )
                
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(translations.get_text(guild_id_int, 'user_not_muted'), ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="lock", description="Lock the channel / Csatorna lezárása")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def slash_lock(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        
        await interaction.channel.set_permissions(
            interaction.guild.default_role,
            send_messages=False
        )
        
        embed = discord.Embed(
            title=translations.get_text(guild_id, 'channel_locked'),
            description=translations.get_text(guild_id, 'channel_locked_desc'),
            color=0xFF006E
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="unlock", description="Unlock the channel / Csatorna feloldása")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def slash_unlock(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        
        await interaction.channel.set_permissions(
            interaction.guild.default_role,
            send_messages=True
        )
        
        embed = discord.Embed(
            title=translations.get_text(guild_id, 'channel_unlocked'),
            description=translations.get_text(guild_id, 'channel_unlocked_desc'),
            color=0x00F3FF
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="warn", description="Warn a user / Felhasználó figyelmeztetése")
    @app_commands.describe(user="User mention or ID / Felhasználó mention vagy ID", reason="Reason / Indok")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def slash_warn(self, interaction: discord.Interaction, user: str, reason: str = None):
        guild_id = interaction.guild.id
        
        try:
            # Try to convert string to user ID or extract from mention
            user_id_int = None
            if user.startswith('<@') and user.endswith('>'):
                user_id_int = int(user.strip('<@!>'))
            else:
                try:
                    user_id_int = int(user)
                except ValueError:
                    await interaction.response.send_message(translations.get_text(guild_id, 'invalid_user'), ephemeral=True)
                    return
            
            # Fetch the member
            target_user = await interaction.guild.fetch_member(user_id_int)
            
            cfg = config.load_config()
            warnings = cfg.get('warnings', {})
            user_id = str(target_user.id)
            
            if user_id not in warnings:
                warnings[user_id] = []
            
            warnings[user_id].append({
                'reason': reason or translations.get_text(guild_id, 'no_reason_provided'),
                'moderator': str(interaction.user),
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            cfg['warnings'] = warnings
            config.save_config(cfg)
            
            embed = discord.Embed(
                title=translations.get_text(guild_id, 'user_warned'),
                description=translations.get_text(guild_id, 'user_warned_desc', target_user.mention),
                color=discord.Color.yellow()
            )
            embed.add_field(name=translations.get_text(guild_id, 'reason'), value=reason or translations.get_text(guild_id, 'no_reason_provided'), inline=False)
            embed.add_field(name=translations.get_text(guild_id, 'total_warnings'), value=str(len(warnings[user_id])), inline=True)
            
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="setlog", description="Set log channel / Napló csatorna beállítása")
    @app_commands.describe(channel="The channel / A csatorna")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_setlog(self, interaction: discord.Interaction, channel: discord.TextChannel):
        guild_id = interaction.guild.id
        
        # 1. Load the most recent config from the file
        cfg = config.load_config()
        
        # 2. Ensure the specific dictionary for guild logs exists
        if 'guild_log_channels' not in cfg:
            cfg['guild_log_channels'] = {}
            
        # 3. Save using Guild ID as a string (JSON requirement)
        cfg['guild_log_channels'][str(guild_id)] = channel.id
        
        # 4. Write back to bot_config.json immediately
        config.save_config(cfg)
        
        # 5. Build the confirmation embed using your translation system
        embed = discord.Embed(
            title=translations.get_text(guild_id, 'log_channel_set'),
            description=translations.get_text(guild_id, 'log_channel_desc', channel.mention),
            color=0x00F3FF
        )
        
        # 6. Send response
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="setwebhook", description="Set webhook for logging / Webhook beállítása")
    @app_commands.describe(webhook_url="Discord webhook URL / Discord webhook URL")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_setwebhook(self, interaction: discord.Interaction, webhook_url: str):
        guild_id = interaction.guild.id
        webhook_cog = self.bot.get_cog('WebhookLogging')
        if webhook_cog:
            webhook_cog.webhook_url = webhook_url
            config.update_config('webhook_url', webhook_url)
            
            test_embed = discord.Embed(
                title=translations.get_text(guild_id, 'webhook_set'),
                description=translations.get_text(guild_id, 'webhook_set_desc'),
                color=0x00F3FF,
                timestamp=datetime.now(timezone.utc)
            )
            test_embed.add_field(
                name=translations.get_text(guild_id, 'test_message'),
                value=translations.get_text(guild_id, 'webhook_working'),
                inline=False
            )
            
            await webhook_cog.send_to_webhook(test_embed)
            await interaction.response.send_message(translations.get_text(guild_id, 'webhook_configured'))
    
    @app_commands.command(name="testwebhook", description="Test webhook / Webhook tesztelése")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_testwebhook(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        webhook_cog = self.bot.get_cog('WebhookLogging')
        if webhook_cog:
            test_embed = discord.Embed(
                title=translations.get_text(guild_id, 'webhook_test'),
                description=translations.get_text(guild_id, 'webhook_test_desc'),
                color=0x8B00FF,
                timestamp=datetime.now(timezone.utc)
            )
            test_embed.add_field(name=translations.get_text(guild_id, 'tested_by'), value=str(interaction.user), inline=True)
            test_embed.add_field(name=translations.get_text(guild_id, 'channel'), value=interaction.channel.mention, inline=True)
            
            await webhook_cog.send_to_webhook(test_embed)
            await interaction.response.send_message(translations.get_text(guild_id, 'test_webhook_sent'))
    
    @app_commands.command(name="say", description="Make the bot say something / Bot rábeszélése üzenetküldésre")
    @app_commands.describe(message="The message to send / Az elküldendő üzenet")
    async def slash_say(self, interaction: discord.Interaction, message: str):
        # Check if user is bot owner or has permissions
        is_owner = await self.bot.is_owner(interaction.user)
        guild_id = interaction.guild.id if interaction.guild else 0
        if not is_owner and not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(translations.get_text(guild_id, 'permission_denied'), ephemeral=True)
            return
            
        await interaction.response.send_message(translations.get_text(guild_id, 'message_sent'), ephemeral=True)
        await interaction.channel.send(message)

    @app_commands.command(name="embedsay", description="Make the bot say something in an embed / Bot rábeszélése embed küldésére")
    @app_commands.describe(title="Embed title / Embed címe", description="Embed description / Embed leírása", color="Embed color (hex, e.g. #00F3FF) / Embed színe")
    async def slash_embedsay(self, interaction: discord.Interaction, description: str, title: str = None, color: str = "#00F3FF"):
        # Check if user is bot owner or has permissions
        is_owner = await self.bot.is_owner(interaction.user)
        guild_id = interaction.guild.id if interaction.guild else 0
        if not is_owner and not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(translations.get_text(guild_id, 'permission_denied'), ephemeral=True)
            return
            
        try:
            # Parse color
            color_int = int(color.lstrip('#'), 16)
            embed = discord.Embed(
                title=title,
                description=description,
                color=color_int
            )
            guild_id = interaction.guild.id if interaction.guild else 0
            await interaction.response.send_message(translations.get_text(guild_id, 'embed_sent'), ephemeral=True)
            await interaction.channel.send(embed=embed)
        except ValueError:
            await interaction.response.send_message("❌ Invalid color format! Use hex (e.g. #00F3FF) / Érvénytelen színformátum! Használj hex kódot (pl. #00F3FF)", ephemeral=True)

    @app_commands.command(name="ping", description="Check bot latency / Bot késleltetés ellenőrzése")
    async def slash_ping(self, interaction: discord.Interaction):
        await interaction.response.defer()
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Bot latency: **{latency}ms**",
            color=0x00F3FF
        )
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="setannouncement", description="Set the announcement channel / Bejelentési csatorna beállítása")
    @app_commands.describe(channel="The channel for announcements / A bejelentések csatornája")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_setannouncement(self, interaction: discord.Interaction, channel: discord.TextChannel):
        guild_id = interaction.guild.id
        cfg = config.load_config()
        if 'announcement_channels' not in cfg:
            cfg['announcement_channels'] = {}
        cfg['announcement_channels'][str(guild_id)] = channel.id
        config.save_config(cfg)
        
        embed = discord.Embed(
            title="📢 Announcement Channel Set / Bejelentési csatorna beállítva",
            description=f"Announcements will now be sent to {channel.mention} / A bejelentések mostantól ide érkeznek: {channel.mention}",
            color=0x00F3FF
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="announce", description="Send a global bot announcement (Owner only) / Bot bejelentés küldése (Csak tulajdonos)")
    @app_commands.describe(message="The announcement message / A bejelentés üzenete", title="Announcement title / Bejelentés címe")
    async def slash_announce(self, interaction: discord.Interaction, message: str, title: str = "Bot Announcement / Bot Bejelentés"):
        # Check if user is bot owner
        is_owner = await self.bot.is_owner(interaction.user)
        if not is_owner:
            await interaction.response.send_message("❌ This command is restricted to the bot owner! / Ez a parancs csak a bot tulajdonosának érhető el!", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        cfg = config.load_config()
        channels = cfg.get('announcement_channels', {})
        
        count = 0
        embed = discord.Embed(
            title=title,
            description=message,
            color=0xFF006E,
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
        embed.set_footer(text="Shadow-MOD Global Announcement System")

        for guild_str, channel_id in channels.items():
            try:
                channel = self.bot.get_channel(channel_id)
                if channel:
                    await channel.send(embed=embed)
                    count += 1
            except Exception:
                continue

        await interaction.followup.send(f"✅ Announcement sent to {count} servers! / Bejelentés elküldve {count} szerverre!", ephemeral=True)

    @app_commands.command(name="purge", description="Delete multiple messages / Több üzenet törlése")
    @app_commands.describe(amount="Number of messages to delete (1-100) / Törölni kívánt üzenetek száma")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def slash_purge(self, interaction: discord.Interaction, amount: int):
        import asyncio
        from datetime import datetime, timezone
        guild_id = interaction.guild.id
        if amount < 1 or amount > 100:
            await interaction.response.send_message(translations.get_text(guild_id, 'purge_invalid'), ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        try:
            deleted = await interaction.channel.purge(limit=amount)
            embed = discord.Embed(
                title=translations.get_text(guild_id, 'messages_purged'),
                description=translations.get_text(guild_id, 'messages_purged_desc', len(deleted)),
                color=0xFF006E,
                timestamp=datetime.now(timezone.utc)
            )
            embed.add_field(name=translations.get_text(guild_id, 'moderator'), value=interaction.user.mention)
            await interaction.followup.send(embed=embed, ephemeral=True)
            mod_cog = self.bot.get_cog('Moderation')
            if mod_cog:
                await mod_cog.send_log(embed)
        except discord.Forbidden:
            await interaction.followup.send("❌ I don't have permission to delete messages!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

    @app_commands.command(name="serverinfo", description="Show server information / Szerver információk megjelenítése")
    async def slash_serverinfo(self, interaction: discord.Interaction):
        await interaction.response.defer()
        info_cog = self.bot.get_cog('Info')
        if info_cog:
            ctx = await self.bot.get_context(interaction)
            ctx.author = interaction.user
            ctx.guild = interaction.guild
            ctx.send = interaction.followup.send
            await info_cog.serverinfo(ctx)
        else:
            await interaction.followup.send("❌ Feature unavailable", ephemeral=True)
    
    @app_commands.command(name="botinfo", description="Show bot information / Bot információk megjelenítése")
    async def slash_botinfo(self, interaction: discord.Interaction):
        await interaction.response.defer()
        info_cog = self.bot.get_cog('Info')
        if info_cog:
            ctx = await self.bot.get_context(interaction)
            ctx.author = interaction.user
            ctx.guild = interaction.guild
            ctx.send = interaction.followup.send
            await info_cog.botinfo(ctx)
        else:
            await interaction.followup.send("❌ Feature unavailable", ephemeral=True)
    
    @app_commands.command(name="userinfo", description="Show user information / Felhasználó információk megjelenítése")
    async def slash_userinfo(self, interaction: discord.Interaction, member: discord.Member = None):
        await interaction.response.defer()
        info_cog = self.bot.get_cog('Info')
        if info_cog:
            ctx = await self.bot.get_context(interaction)
            ctx.author = interaction.user
            ctx.guild = interaction.guild
            ctx.send = interaction.followup.send
            await info_cog.userinfo(ctx, member)
        else:
            await interaction.followup.send("❌ Feature unavailable", ephemeral=True)
    
    @app_commands.command(name="support", description="Get support server invite / Support szerver meghívó")
    async def slash_support(self, interaction: discord.Interaction):
        await interaction.response.defer()
        info_cog = self.bot.get_cog('Info')
        if info_cog:
            ctx = await self.bot.get_context(interaction)
            ctx.author = interaction.user
            ctx.send = interaction.followup.send
            await info_cog.support(ctx)
        else:
            await interaction.followup.send("❌ Feature unavailable", ephemeral=True)
    
    @app_commands.command(name="webpage", description="Get web dashboard link / Web irányítópult link")
    async def slash_webpage(self, interaction: discord.Interaction):
        await interaction.response.defer()
        info_cog = self.bot.get_cog('Info')
        if info_cog:
            ctx = await self.bot.get_context(interaction)
            ctx.author = interaction.user
            ctx.send = interaction.followup.send
            await info_cog.webpage(ctx)
        else:
            await interaction.followup.send("❌ Feature unavailable", ephemeral=True)
    
    @app_commands.command(name="setprefix", description="Set role prefix for nicknames / Szerep prefix beállítása")
    @app_commands.describe(role="The role to set prefix for / Szerep", prefix="Prefix text (max 10 chars) / Prefix szöveg")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_setprefix(self, interaction: discord.Interaction, role: discord.Role, prefix: str):
        await interaction.response.defer()
        nameauto_cog = self.bot.get_cog('NameAutomation')
        if nameauto_cog:
            if len(prefix) > 10:
                await interaction.followup.send("❌ Prefix must be 10 characters or less!", ephemeral=True)
                return
            import config as cfg_module
            cfg = cfg_module.load_config()
            if 'role_prefixes' not in cfg:
                cfg['role_prefixes'] = {}
            cfg['role_prefixes'][str(role.id)] = prefix
            cfg_module.save_config(cfg)
            embed = discord.Embed(
                title="✅ Prefix Set",
                description=f"Members with {role.mention} will have `{prefix}` prefix in their nickname!",
                color=0x00F3FF
            )
            embed.add_field(name="Example", value=f"{prefix} Username", inline=False)
            await interaction.followup.send(embed=embed)
            count = 0
            for member in interaction.guild.members:
                if role in member.roles:
                    await nameauto_cog.update_member_nickname(member)
                    count += 1
            embed.add_field(name="Updated", value=f"{count} members updated!", inline=False)
            await interaction.edit_original_response(embed=embed)
        else:
            await interaction.followup.send("❌ Feature unavailable", ephemeral=True)
    
    @app_commands.command(name="removeprefix", description="Remove role prefix / Szerep prefix eltávolítása")
    @app_commands.describe(role="The role to remove prefix from / Szerep")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_removeprefix(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.defer()
        nameauto_cog = self.bot.get_cog('NameAutomation')
        if nameauto_cog:
            import config as cfg_module
            cfg = cfg_module.load_config()
            role_prefixes = cfg.get('role_prefixes', {})
            if str(role.id) not in role_prefixes:
                await interaction.followup.send(f"❌ {role.mention} doesn't have a prefix set!", ephemeral=True)
                return
            del cfg['role_prefixes'][str(role.id)]
            cfg_module.save_config(cfg)
            embed = discord.Embed(title="✅ Prefix Removed", description=f"Prefix removed from {role.mention}", color=0x00F3FF)
            await interaction.followup.send(embed=embed)
            count = 0
            for member in interaction.guild.members:
                if role in member.roles:
                    await nameauto_cog.update_member_nickname(member)
                    count += 1
            embed.add_field(name="Updated", value=f"{count} members updated!", inline=False)
            await interaction.edit_original_response(embed=embed)
        else:
            await interaction.followup.send("❌ Feature unavailable", ephemeral=True)
    
    @app_commands.command(name="viewprefixes", description="View all role prefixes / Összes szerep prefix megtekintése")
    async def slash_viewprefixes(self, interaction: discord.Interaction):
        import config as cfg_module
        cfg = cfg_module.load_config()
        role_prefixes = cfg.get('role_prefixes', {})
        if not role_prefixes:
            await interaction.response.send_message("❌ No role prefixes configured!", ephemeral=True)
            return
        embed = discord.Embed(title="📋 Role Prefixes", description="Current role prefix configuration:", color=0x8B00FF)
        for role_id, prefix in role_prefixes.items():
            role = interaction.guild.get_role(int(role_id))
            if role:
                embed.add_field(name=role.name, value=f"Prefix: `{prefix}`", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="setaltage", description="Set minimum account age / Minimális fiók kor beállítása")
    @app_commands.describe(days="Minimum account age in days / Minimális fiók kor napokban")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_setaltage(self, interaction: discord.Interaction, days: int):
        if days < 0:
            await interaction.response.send_message("❌ Days must be a positive number!", ephemeral=True)
            return
        import config as cfg_module
        cfg_module.update_config('min_account_age_days', days)
        embed = discord.Embed(title="✅ Anti-Alt Configuration Updated", description=f"Minimum account age set to **{days} days**", color=0x00F3FF)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="tempmute", description="Temporarily mute a user / Felhasználó ideiglenes némítása")
    @app_commands.describe(user="User to mute / Némítandó felhasználó", duration="Duration (e.g., 1h, 30m, 1d) / Időtartam")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def slash_tempmute(self, interaction: discord.Interaction, user: discord.Member, duration: str):
        from datetime import timedelta
        moderation_cog = self.bot.get_cog('Moderation')
        if moderation_cog:
            try:
                time_dict = moderation_cog.parse_time(duration)
                delta = timedelta(**time_dict)
                if delta.total_seconds() > 2419200:
                    await interaction.response.send_message("❌ Maximum timeout duration is 28 days!", ephemeral=True)
                    return
                await user.timeout(delta, reason=f"Timed out by {interaction.user}")
                embed = discord.Embed(title="🔇 User Timed Out", description=f"{user.mention} has been timed out", color=0xFF006E)
                embed.add_field(name="Duration", value=duration, inline=True)
                embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
                await interaction.response.send_message(embed=embed)
            except ValueError:
                await interaction.response.send_message(f"❌ Invalid time format! Use: 1h, 30m, 1d, etc.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Feature unavailable", ephemeral=True)
    
    @app_commands.command(name="dice", description="Roll a dice / Kockadobás")
    @app_commands.describe(sides="Number of sides (default: 6) / Oldalak száma")
    async def slash_dice(self, interaction: discord.Interaction, sides: int = 6):
        fun_cog = self.bot.get_cog('Fun')
        if fun_cog:
            await interaction.response.defer()
            import random
            result = random.randint(1, sides)
            embed = discord.Embed(title="🎲 Dice Roll", description=f"You rolled a **{result}** on a {sides}-sided dice!", color=0x8B00FF)
            embed.set_footer(text=f"Rolled by {interaction.user.display_name}")
            await interaction.followup.send(embed=embed)
        else:
            await interaction.response.send_message("❌ Feature unavailable", ephemeral=True)
    
    @app_commands.command(name="rps", description="Play Rock-Paper-Scissors / Kő-Papír-Olló játék")
    @app_commands.describe(choice="Your choice / Választásod")
    @app_commands.choices(choice=[
        app_commands.Choice(name="🪨 Rock / Kő", value="rock"),
        app_commands.Choice(name="📄 Paper / Papír", value="paper"),
        app_commands.Choice(name="✂️ Scissors / Olló", value="scissors")
    ])
    async def slash_rps(self, interaction: discord.Interaction, choice: str):
        games_cog = self.bot.get_cog('Games')
        if games_cog:
            import random
            choices = ['rock', 'paper', 'scissors']
            bot_choice = random.choice(choices)
            emoji_map = {'rock': '🪨', 'paper': '📄', 'scissors': '✂️'}
            if choice == bot_choice:
                result, color = "It's a tie!", 0x8B00FF
            elif (choice == 'rock' and bot_choice == 'scissors') or (choice == 'paper' and bot_choice == 'rock') or (choice == 'scissors' and bot_choice == 'paper'):
                result, color = "You win!", 0x00F3FF
            else:
                result, color = "I win!", 0xFF006E
            embed = discord.Embed(title="🎮 Rock-Paper-Scissors", description=f"**You:** {emoji_map[choice]}\n**Bot:** {emoji_map[bot_choice]}\n\n**{result}**", color=color)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Feature unavailable", ephemeral=True)
    
    @app_commands.command(name="tictactoe", description="Play Tic-Tac-Toe / Amőba játék")
    @app_commands.describe(opponent="Player to challenge / Kihívandó játékos")
    async def slash_tictactoe(self, interaction: discord.Interaction, opponent: discord.Member):
        games_cog = self.bot.get_cog('Games')
        if games_cog:
            if opponent == interaction.user:
                await interaction.response.send_message("❌ You can't play against yourself!", ephemeral=True)
                return
            if opponent.bot:
                await interaction.response.send_message("❌ You can't play against a bot!", ephemeral=True)
                return
            view = games_cog.TicTacToeView(interaction.user, opponent)
            embed = discord.Embed(title="⭕ Tic-Tac-Toe", description=f"{interaction.user.mention} vs {opponent.mention}\n\n{interaction.user.mention}'s turn (⭕)", color=0x8B00FF)
            await interaction.response.send_message(embed=embed, view=view)
        else:
            await interaction.response.send_message("❌ Feature unavailable", ephemeral=True)
    
    @app_commands.command(name="poll", description="Create a poll / Szavazás létrehozása")
    @app_commands.describe(question="Poll question / Kérdés", option1="First option / Első lehetőség", option2="Second option / Második lehetőség", option3="Third option (optional) / Harmadik lehetőség", option4="Fourth option (optional) / Negyedik lehetőség")
    async def slash_poll(self, interaction: discord.Interaction, question: str, option1: str, option2: str, option3: str = None, option4: str = None):
        polls_cog = self.bot.get_cog('Polls')
        if polls_cog:
            options = [option1, option2]
            if option3: options.append(option3)
            if option4: options.append(option4)
            view = polls_cog.PollView(options)
            embed = discord.Embed(title="📊 " + question, description="Click the buttons below to vote!", color=0x8B00FF)
            for i, option in enumerate(options, 1):
                embed.add_field(name=f"Option {i}", value=option, inline=False)
            embed.set_footer(text=f"Poll by {interaction.user.display_name}")
            await interaction.response.send_message(embed=embed, view=view)
        else:
            await interaction.response.send_message("❌ Feature unavailable", ephemeral=True)
    
    @app_commands.command(name="giveaway", description="Create a giveaway / Nyereményjáték létrehozása")
    @app_commands.describe(prize="Prize to give away / Nyeremény", duration="Duration (e.g., 1h, 1d) / Időtartam", winners="Number of winners / Nyertesek száma")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def slash_giveaway(self, interaction: discord.Interaction, prize: str, duration: str, winners: int = 1):
        from datetime import timedelta, datetime, timezone
        giveaway_cog = self.bot.get_cog('Giveaways')
        if giveaway_cog:
            try:
                time_dict = giveaway_cog.parse_time(duration)
                end_time = datetime.now(timezone.utc) + timedelta(**time_dict)
                embed = discord.Embed(title="🎁 GIVEAWAY", description=f"**Prize:** {prize}\n**Winners:** {winners}\n**Ends:** <t:{int(end_time.timestamp())}:R>", color=0xFF006E)
                embed.set_footer(text=f"Hosted by {interaction.user.display_name}")
                giveaway_id = f"giveaway_{interaction.channel.id}_{int(datetime.now(timezone.utc).timestamp())}"
                view = giveaway_cog.GiveawayView(end_time, winners, prize, giveaway_id)
                await interaction.response.send_message(embed=embed, view=view)
                message = await interaction.original_response()
                self.bot.loop.create_task(giveaway_cog.end_giveaway(message, end_time, winners, prize))
            except ValueError:
                await interaction.response.send_message("❌ Invalid time format! Use: 1h, 30m, 1d, etc.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Feature unavailable", ephemeral=True)
    
    @app_commands.command(name="createrole", description="Create a new role / Új szerep létrehozása")
    @app_commands.describe(
        name="Role name / Szerep neve",
        color="Hex color (e.g., #FF0000) / Szín"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def slash_createrole(self, interaction: discord.Interaction, name: str, color: str = None):
        try:
            role_color = discord.Color.default()
            if color:
                color = color.lstrip('#')
                role_color = discord.Color(int(color, 16))
            
            role = await interaction.guild.create_role(name=name, color=role_color)
            
            embed = discord.Embed(
                title="✅ Role Created",
                description=f"Role {role.mention} has been created!",
                color=0x00F3FF
            )
            
            await interaction.response.send_message(embed=embed)
        except ValueError:
            await interaction.response.send_message("❌ Invalid color format! Use hex format like #FF0000", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error creating role: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="closeticket", description="Close a ticket / Jegy lezárása")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def slash_closeticket(self, interaction: discord.Interaction):
        ticket_cog = self.bot.get_cog('Tickets')
        if ticket_cog:
            if not interaction.channel.name.startswith('ticket-'):
                await interaction.response.send_message("❌ This command can only be used in ticket channels!", ephemeral=True)
                return
            
            embed = discord.Embed(
                title="🎫 Ticket Closed",
                description="This ticket has been closed.",
                color=0xFF006E
            )
            
            await interaction.response.send_message(embed=embed)
            await interaction.channel.delete(reason="Ticket closed")
        else:
            await interaction.response.send_message("❌ Feature unavailable", ephemeral=True)
    
    @app_commands.command(name="play", description="Play music from YouTube, Spotify, or SoundCloud / Zene lejátszása")
    @app_commands.describe(query="Song name or URL / Dal neve vagy URL")
    async def slash_play(self, interaction: discord.Interaction, query: str):
        music_cog = self.bot.get_cog('Music')
        if music_cog:
            await interaction.response.defer()
            
            class FakeContext:
                def __init__(self, interaction):
                    self.author = interaction.user
                    self.guild = interaction.guild
                    self.channel = interaction.channel
                    self.bot = interaction.client
                    self.voice_client = interaction.guild.voice_client
                    self._interaction = interaction
                
                async def send(self, *args, **kwargs):
                    try:
                        await self._interaction.followup.send(*args, **kwargs)
                    except:
                        await self._interaction.channel.send(*args, **kwargs)
            
            ctx = FakeContext(interaction)
            await music_cog.play(ctx, query=query)
        else:
            await interaction.response.send_message("❌ Music feature unavailable", ephemeral=True)
    
    @app_commands.command(name="pause", description="Pause the current playback / Lejátszás szüneteltetése")
    async def slash_pause(self, interaction: discord.Interaction):
        import wavelink
        vc: wavelink.Player = interaction.guild.voice_client
        
        if not vc or not vc.playing:
            await interaction.response.send_message("❌ Nothing is playing", ephemeral=True)
            return
        
        await vc.pause(True)
        await interaction.response.send_message("⏸️ Paused playback", ephemeral=True)
    
    @app_commands.command(name="resume", description="Resume paused playback / Lejátszás folytatása")
    async def slash_resume(self, interaction: discord.Interaction):
        import wavelink
        vc: wavelink.Player = interaction.guild.voice_client
        
        if not vc or not vc.paused:
            await interaction.response.send_message("❌ Nothing is paused", ephemeral=True)
            return
        
        await vc.pause(False)
        await interaction.response.send_message("▶️ Resumed playback", ephemeral=True)
    
    @app_commands.command(name="skip", description="Skip to the next song / Következő dal")
    async def slash_skip(self, interaction: discord.Interaction):
        import wavelink
        vc: wavelink.Player = interaction.guild.voice_client
        
        if not vc or not vc.playing:
            await interaction.response.send_message("❌ Nothing is playing", ephemeral=True)
            return
        
        await vc.skip(force=True)
        await interaction.response.send_message("⏭️ Skipped to next song", ephemeral=True)
    
    @app_commands.command(name="stop", description="Stop playback and disconnect / Lejátszás leállítása")
    async def slash_stop(self, interaction: discord.Interaction):
        import wavelink
        vc: wavelink.Player = interaction.guild.voice_client
        
        if not vc:
            await interaction.response.send_message("❌ Not connected to voice", ephemeral=True)
            return
        
        await vc.disconnect()
        await interaction.response.send_message("⏹️ Stopped playback and disconnected", ephemeral=True)
    
    @app_commands.command(name="queue", description="Display the music queue / Zene sor megjelenítése")
    async def slash_queue(self, interaction: discord.Interaction):
        import wavelink
        vc: wavelink.Player = interaction.guild.voice_client
        
        if not vc:
            await interaction.response.send_message("❌ Not connected to voice", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🎵 Music Queue",
            color=0x8B00FF
        )
        
        if vc.current:
            embed.add_field(
                name="Now Playing",
                value=f"🎶 **{vc.current.title}**\n`{vc.current.author}`",
                inline=False
            )
        
        if vc.queue:
            queue_list = []
            for i, track in enumerate(vc.queue[:10], 1):
                queue_list.append(f"{i}. **{track.title}** - `{track.author}`")
            
            embed.add_field(
                name=f"Up Next ({vc.queue.count} songs)",
                value="\n".join(queue_list),
                inline=False
            )
        else:
            if not vc.current:
                embed.description = "Queue is empty"
        
        if vc.queue.mode == wavelink.QueueMode.loop:
            embed.set_footer(text="🔁 Loop: ON")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="nowplaying", description="Show currently playing track / Jelenlegi dal megjelenítése")
    async def slash_nowplaying(self, interaction: discord.Interaction):
        import wavelink
        vc: wavelink.Player = interaction.guild.voice_client
        
        if not vc or not vc.current:
            await interaction.response.send_message("❌ Nothing is playing", ephemeral=True)
            return
        
        track = vc.current
        
        position = vc.position
        duration = track.length
        
        progress_bar_length = 20
        progress = int((position / duration) * progress_bar_length) if duration > 0 else 0
        bar = "█" * progress + "░" * (progress_bar_length - progress)
        
        position_str = f"{int(position // 60)}:{int(position % 60):02d}"
        duration_str = f"{int(duration // 60)}:{int(duration % 60):02d}"
        
        embed = discord.Embed(
            title="🎵 Now Playing",
            description=f"**{track.title}**\n`{track.author}`",
            color=0x00F3FF
        )
        
        embed.add_field(
            name="Progress",
            value=f"`{position_str}` {bar} `{duration_str}`",
            inline=False
        )
        
        if hasattr(track, 'artwork') and track.artwork:
            embed.set_thumbnail(url=track.artwork)
        
        if vc.queue.mode == wavelink.QueueMode.loop:
            embed.set_footer(text="🔁 Loop: ON")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="loop", description="Toggle loop mode / Ismétlés be/ki")
    async def slash_loop(self, interaction: discord.Interaction):
        import wavelink
        vc: wavelink.Player = interaction.guild.voice_client
        
        if not vc:
            await interaction.response.send_message("❌ Not connected to voice", ephemeral=True)
            return
        
        if vc.queue.mode == wavelink.QueueMode.loop:
            vc.queue.mode = wavelink.QueueMode.normal
            status = "disabled"
            emoji = "➡️"
        else:
            vc.queue.mode = wavelink.QueueMode.loop
            status = "enabled"
            emoji = "🔁"
        
        await interaction.response.send_message(f"{emoji} Loop mode {status}", ephemeral=True)
    
    @app_commands.command(name="volume", description="Adjust playback volume / Hangerő beállítása")
    @app_commands.describe(volume="Volume level (0-100) / Hangerő szint (0-100)")
    async def slash_volume(self, interaction: discord.Interaction, volume: int):
        import wavelink
        
        if volume < 0 or volume > 100:
            await interaction.response.send_message("❌ Volume must be between 0 and 100", ephemeral=True)
            return
        
        vc: wavelink.Player = interaction.guild.voice_client
        
        if not vc:
            await interaction.response.send_message("❌ Not connected to voice", ephemeral=True)
            return
        
        await vc.set_volume(volume)
        await interaction.response.send_message(f"🔊 Volume set to {volume}%", ephemeral=True)
    
    @app_commands.command(name="servers", description="List all servers the bot is in (Owner Only) / Bot által használt szerverek listája")
    async def slash_servers(self, interaction: discord.Interaction):
        if not await self.bot.is_owner(interaction.user):
            await interaction.response.send_message(translations.get_text(interaction.guild.id, 'owner_only'), ephemeral=True)
            return
        
        guild_id = interaction.guild.id if interaction.guild else None
        
        embed = discord.Embed(
            title=translations.get_text(guild_id, 'servers_title'),
            description=translations.get_text(guild_id, 'servers_description', len(self.bot.guilds)),
            color=0x00ffff
        )
        
        server_list = []
        for guild in self.bot.guilds:
            server_list.append(f"**{guild.name}**\n`ID: {guild.id}`")
        
        if server_list:
            chunks = [server_list[i:i+10] for i in range(0, len(server_list), 10)]
            for i, chunk in enumerate(chunks):
                embed.add_field(
                    name=f"Servers {i*10 + 1}-{min((i+1)*10, len(server_list))}",
                    value="\n\n".join(chunk),
                    inline=False
                )
        
        embed.set_footer(text=translations.get_text(guild_id, 'servers_footer', len(self.bot.guilds)))
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="createinvite", description="Create an invite for a server (Owner Only) / Meghívó létrehozása szerverhez")
    @app_commands.describe(server_id="Server ID to create invite for / Szerver ID meghívó létrehozásához")
    async def slash_createinvite(self, interaction: discord.Interaction, server_id: str):
        if not await self.bot.is_owner(interaction.user):
            await interaction.response.send_message(translations.get_text(interaction.guild.id, 'owner_only'), ephemeral=True)
            return
        
        guild_id = interaction.guild.id if interaction.guild else None
        
        try:
            target_server_id = int(server_id)
        except ValueError:
            await interaction.response.send_message(translations.get_text(guild_id, 'server_not_found'), ephemeral=True)
            return
        
        guild = self.bot.get_guild(target_server_id)
        
        if guild is None:
            await interaction.response.send_message(translations.get_text(guild_id, 'server_not_found'), ephemeral=True)
            return
        
        text_channels = [ch for ch in guild.text_channels if ch.permissions_for(guild.me).create_instant_invite]
        
        if not text_channels:
            await interaction.response.send_message(translations.get_text(guild_id, 'no_permission_invite', guild.name), ephemeral=True)
            return
        
        channel = text_channels[0]
        
        try:
            invite = await channel.create_invite(max_age=0, max_uses=0, reason=f"Created by bot owner {interaction.user}")
            
            embed = discord.Embed(
                title=translations.get_text(guild_id, 'invite_created'),
                description=translations.get_text(guild_id, 'invite_created_desc', guild.name),
                color=0x00ffff
            )
            embed.add_field(name=translations.get_text(guild_id, 'invite_link'), value=invite.url, inline=False)
            embed.add_field(name=translations.get_text(guild_id, 'invite_expires'), value=translations.get_text(guild_id, 'invite_never'), inline=True)
            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        except discord.Forbidden:
            await interaction.response.send_message(translations.get_text(guild_id, 'no_permission_invite', guild.name), ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error creating invite: {e}", ephemeral=True)

    @app_commands.command(name="addcc", description="Add a custom command (Owner Only) / Egyéni parancs hozzáadása")
    @app_commands.describe(
        name="Command name (without prefix) / Parancs neve (prefix nélkül)",
        response="Command response text / Parancs válasz szövege"
    )
    async def slash_addcc(self, interaction: discord.Interaction, name: str, response: str):
        if not await self.bot.is_owner(interaction.user):
            await interaction.response.send_message(translations.get_text(interaction.guild.id, 'owner_only'), ephemeral=True)
            return
        
        guild_id = interaction.guild.id
        name = name.lower().strip()
        
        # Validate command name
        if len(name) == 0:
            await interaction.response.send_message("❌ Command name cannot be empty!", ephemeral=True)
            return
        
        if ' ' in name:
            await interaction.response.send_message("❌ Command name cannot contain spaces!", ephemeral=True)
            return
        
        # Get custom commands cog
        cc_cog = self.bot.get_cog('CustomCommands')
        if not cc_cog:
            await interaction.response.send_message("❌ Custom commands system not loaded!", ephemeral=True)
            return
        
        # Check if command already exists
        if name in cc_cog.custom_commands:
            await interaction.response.send_message(f"❌ Custom command `{name}` already exists! Use `/mcc` to modify it.", ephemeral=True)
            return
        
        # Add custom command
        cc_cog.custom_commands[name] = response
        cc_cog.save_custom_commands()
        
        embed = discord.Embed(
            title="✅ Custom Command Added",
            description=f"**Command:** `{name}`\n**Response:** {response}",
            color=0x00FF00
        )
        embed.add_field(
            name="Usage",
            value=f"Users can now use: `!{name}` (or your custom prefix)",
            inline=False
        )
        embed.set_footer(text=f"Total custom commands: {len(cc_cog.custom_commands)}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="rcc", description="Remove a custom command (Owner Only) / Egyéni parancs eltávolítása")
    @app_commands.describe(name="Command name to remove / Eltávolítandó parancs neve")
    async def slash_rcc(self, interaction: discord.Interaction, name: str):
        if not await self.bot.is_owner(interaction.user):
            await interaction.response.send_message(translations.get_text(interaction.guild.id, 'owner_only'), ephemeral=True)
            return
        
        guild_id = interaction.guild.id
        name = name.lower().strip()
        
        # Get custom commands cog
        cc_cog = self.bot.get_cog('CustomCommands')
        if not cc_cog:
            await interaction.response.send_message("❌ Custom commands system not loaded!", ephemeral=True)
            return
        
        # Check if command exists
        if name not in cc_cog.custom_commands:
            await interaction.response.send_message(f"❌ Custom command `{name}` does not exist!", ephemeral=True)
            return
        
        # Remove custom command
        old_response = cc_cog.custom_commands[name]
        del cc_cog.custom_commands[name]
        cc_cog.save_custom_commands()
        
        embed = discord.Embed(
            title="🗑️ Custom Command Removed",
            description=f"**Command:** `{name}`\n**Old Response:** {old_response}",
            color=0xFF0000
        )
        embed.set_footer(text=f"Total custom commands: {len(cc_cog.custom_commands)}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="mcc", description="Modify a custom command (Owner Only) / Egyéni parancs módosítása")
    @app_commands.describe(
        name="Command name to modify / Módosítandó parancs neve",
        response="New response text / Új válasz szövege"
    )
    async def slash_mcc(self, interaction: discord.Interaction, name: str, response: str):
        if not await self.bot.is_owner(interaction.user):
            await interaction.response.send_message(translations.get_text(interaction.guild.id, 'owner_only'), ephemeral=True)
            return
        
        guild_id = interaction.guild.id
        name = name.lower().strip()
        
        # Get custom commands cog
        cc_cog = self.bot.get_cog('CustomCommands')
        if not cc_cog:
            await interaction.response.send_message("❌ Custom commands system not loaded!", ephemeral=True)
            return
        
        # Check if command exists
        if name not in cc_cog.custom_commands:
            await interaction.response.send_message(f"❌ Custom command `{name}` does not exist! Use `/addcc` to create it.", ephemeral=True)
            return
        
        # Modify custom command
        old_response = cc_cog.custom_commands[name]
        cc_cog.custom_commands[name] = response
        cc_cog.save_custom_commands()
        
        embed = discord.Embed(
            title="✏️ Custom Command Modified",
            description=f"**Command:** `{name}`",
            color=0xFFFF00
        )
        embed.add_field(name="Old Response", value=old_response[:1024], inline=False)
        embed.add_field(name="New Response", value=response[:1024], inline=False)
        embed.set_footer(text=f"Total custom commands: {len(cc_cog.custom_commands)}")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="setbotprefix", description="Change the bot command prefix / Bot parancs prefix megváltoztatása")
    @app_commands.describe(prefix="New prefix for bot commands / Új prefix a bot parancsokhoz")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_setbotprefix(self, interaction: discord.Interaction, prefix: str):
        guild_id = interaction.guild.id
        
        # Validate prefix
        if len(prefix) > 5:
            await interaction.response.send_message("❌ Prefix must be 5 characters or less! / A prefix maximum 5 karakter lehet!", ephemeral=True)
            return
        
        if prefix == "/":
            await interaction.response.send_message("❌ Cannot use `/` as prefix (reserved for slash commands) / Nem használható a `/` prefix (fenntartva slash parancsokhoz)", ephemeral=True)
            return
        
        # Set new prefix
        config.set_guild_prefix(guild_id, prefix)
        
        embed = discord.Embed(
            title="✅ Bot Prefix Updated / Prefix Frissítve",
            description=f"**New prefix:** `{prefix}`\n**Example:** `{prefix}help`\n\n**Új prefix:** `{prefix}`\n**Példa:** `{prefix}help`",
            color=0x00FF00
        )
        embed.add_field(
            name="Note / Megjegyzés",
            value="Slash commands (/) still work! / A slash parancsok (/) továbbra is működnek!",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)

    # ==================== AUTO-MODERATION COMMANDS ====================
    
    @app_commands.command(name="automod", description="Configure auto-moderation system")
    @app_commands.describe(
        action="Action to perform",
        setting="Setting to modify (optional)",
        value="Value to set (optional)"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_automod(self, interaction: discord.Interaction, action: str, setting: str = None, value: str = None):
        automod_cog = self.bot.get_cog('AutoMod')
        if not automod_cog:
            await interaction.response.send_message("❌ AutoMod system not loaded!", ephemeral=True)
            return
        
        settings = automod_cog.get_automod_config(interaction.guild.id)
        
        if action == "enable":
            settings['enabled'] = True
            automod_cog.save_automod_config(interaction.guild.id, settings)
            await interaction.response.send_message("✅ Auto-moderation enabled!")
        
        elif action == "disable":
            settings['enabled'] = False
            automod_cog.save_automod_config(interaction.guild.id, settings)
            await interaction.response.send_message("✅ Auto-moderation disabled!")
        
        elif action == "settings":
            embed = discord.Embed(title="🛡️ Auto-Moderation Settings", color=0x00F3FF)
            embed.add_field(name="Enabled", value="✅ Yes" if settings['enabled'] else "❌ No", inline=True)
            embed.add_field(name="Spam Detection", value="✅ Yes" if settings['spam_detection'] else "❌ No", inline=True)
            embed.add_field(name="Link Filter", value="✅ Yes" if settings['link_filter'] else "❌ No", inline=True)
            embed.add_field(name="Caps Filter", value="✅ Yes" if settings['caps_filter'] else "❌ No", inline=True)
            embed.add_field(name="Emoji Spam", value="✅ Yes" if settings['emoji_spam'] else "❌ No", inline=True)
            embed.add_field(name="Punishment", value=settings['punishment'].upper(), inline=True)
            embed.add_field(name="Bad Words", value=f"{len(settings['bad_words'])} words", inline=True)
            await interaction.response.send_message(embed=embed)
        
        else:
            await interaction.response.send_message("❌ Invalid action! Use: enable, disable, or settings", ephemeral=True)

    # ==================== WELCOME/GOODBYE COMMANDS ====================
    
    @app_commands.command(name="setwelcome", description="Setup welcome message system")
    @app_commands.describe(
        channel="Channel for welcome messages",
        message="Welcome message ({user}, {server}, {count})"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_setwelcome(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str = None):
        welcome_cog = self.bot.get_cog('Welcome')
        if not welcome_cog:
            await interaction.response.send_message("❌ Welcome system not loaded!", ephemeral=True)
            return
        
        settings = welcome_cog.get_welcome_config(interaction.guild.id)
        settings['enabled'] = True
        settings['channel_id'] = channel.id
        if message:
            settings['message'] = message
        
        welcome_cog.save_welcome_config(interaction.guild.id, settings)
        
        embed = discord.Embed(
            title="✅ Welcome System Configured",
            description=f"Welcome messages will be sent to {channel.mention}",
            color=0x00FF00
        )
        embed.add_field(name="Message", value=settings['message'], inline=False)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="setgoodbye", description="Setup goodbye message system")
    @app_commands.describe(
        enabled="Enable goodbye messages",
        message="Goodbye message ({user}, {server})"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_setgoodbye(self, interaction: discord.Interaction, enabled: bool, message: str = None):
        welcome_cog = self.bot.get_cog('Welcome')
        if not welcome_cog:
            await interaction.response.send_message("❌ Welcome system not loaded!", ephemeral=True)
            return
        
        settings = welcome_cog.get_welcome_config(interaction.guild.id)
        settings['goodbye_enabled'] = enabled
        if message:
            settings['goodbye_message'] = message
        
        welcome_cog.save_welcome_config(interaction.guild.id, settings)
        
        status = "enabled" if enabled else "disabled"
        await interaction.response.send_message(f"✅ Goodbye messages {status}!")

    # ==================== REACTION ROLES COMMANDS ====================
    
    @app_commands.command(name="reactionrole", description="Setup reaction roles")
    @app_commands.describe(
        message_id="Message ID to add reaction role to",
        emoji="Emoji for the role",
        role="Role to assign"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_reactionrole(self, interaction: discord.Interaction, message_id: str, emoji: str, role: discord.Role):
        rr_cog = self.bot.get_cog('ReactionRoles')
        if not rr_cog:
            await interaction.response.send_message("❌ Reaction Roles system not loaded!", ephemeral=True)
            return
        
        try:
            msg_id = int(message_id)
            message = await interaction.channel.fetch_message(msg_id)
        except:
            await interaction.response.send_message("❌ Invalid message ID or message not found!", ephemeral=True)
            return
        
        reaction_roles = rr_cog.get_reaction_roles()
        message_key = str(msg_id)
        
        if message_key not in reaction_roles:
            reaction_roles[message_key] = {}
        
        reaction_roles[message_key][emoji] = role.id
        rr_cog.save_reaction_roles(reaction_roles)
        
        try:
            await message.add_reaction(emoji)
        except:
            pass
        
        await interaction.response.send_message(f"✅ Reaction role added! React with {emoji} to get {role.mention}")

    # ==================== LEVELING COMMANDS ====================
    
    @app_commands.command(name="rank", description="Check your rank and level")
    @app_commands.describe(user="User to check (optional)")
    async def slash_rank(self, interaction: discord.Interaction, user: discord.Member = None):
        leveling_cog = self.bot.get_cog('Leveling')
        if not leveling_cog:
            await interaction.response.send_message("❌ Leveling system not loaded!", ephemeral=True)
            return
        
        target = user or interaction.user
        user_data = leveling_cog.get_user_xp(interaction.guild.id, target.id)
        
        xp_needed = leveling_cog.xp_for_level(user_data['level'] + 1) - user_data['xp']
        
        embed = discord.Embed(
            title=f"📊 {target.name}'s Rank",
            color=0x00F3FF
        )
        embed.add_field(name="Level", value=f"⭐ {user_data['level']}", inline=True)
        embed.add_field(name="XP", value=f"{user_data['xp']} / {leveling_cog.xp_for_level(user_data['level'] + 1)}", inline=True)
        embed.add_field(name="Total XP", value=f"{user_data['total_xp']}", inline=True)
        embed.add_field(name="XP Until Next Level", value=f"{xp_needed} XP", inline=False)
        embed.set_thumbnail(url=target.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="leaderboard", description="Show server XP leaderboard")
    async def slash_leaderboard(self, interaction: discord.Interaction):
        leveling_cog = self.bot.get_cog('Leveling')
        if not leveling_cog:
            await interaction.response.send_message("❌ Leveling system not loaded!", ephemeral=True)
            return
        
        cfg = config.load_config()
        guild_data = cfg.get('user_xp', {}).get(str(interaction.guild.id), {})
        
        # Sort by total XP
        sorted_users = sorted(
            guild_data.items(),
            key=lambda x: x[1].get('total_xp', 0),
            reverse=True
        )[:10]
        
        embed = discord.Embed(
            title=f"🏆 {interaction.guild.name} Leaderboard",
            color=0xFFD700
        )
        
        for i, (user_id, data) in enumerate(sorted_users, 1):
            user = interaction.guild.get_member(int(user_id))
            if user:
                embed.add_field(
                    name=f"{i}. {user.name}",
                    value=f"Level {data['level']} • {data['total_xp']} total XP",
                    inline=False
                )
        
        if not sorted_users:
            embed.description = "No data yet! Start chatting to earn XP!"
        
        await interaction.response.send_message(embed=embed)

    # ==================== REMINDER COMMANDS ====================
    
    @app_commands.command(name="remind", description="Set a reminder")
    @app_commands.describe(
        time="Time (e.g., 1h, 30m, 2d)",
        message="Reminder message"
    )
    async def slash_remind(self, interaction: discord.Interaction, time: str, message: str):
        reminders_cog = self.bot.get_cog('Reminders')
        if not reminders_cog:
            await interaction.response.send_message("❌ Reminders system not loaded!", ephemeral=True)
            return
        
        # Parse time
        time_units = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
        
        try:
            time_amount = int(time[:-1])
            time_unit = time[-1]
        except:
            await interaction.response.send_message("❌ Invalid time format! Use: 10s, 5m, 2h, 1d", ephemeral=True)
            return
        
        if time_unit not in time_units:
            await interaction.response.send_message("❌ Invalid time format! Use: 10s, 5m, 2h, 1d", ephemeral=True)
            return
        
        seconds = time_amount * time_units[time_unit]
        remind_at = datetime.now(timezone.utc) + timedelta(seconds=seconds)
        
        reminder_id = reminders_cog.add_reminder(
            interaction.user.id,
            interaction.channel.id,
            interaction.guild.id,
            message,
            remind_at
        )
        
        embed = discord.Embed(
            title="⏰ Reminder Set!",
            description=f"I'll remind you in {time}",
            color=0x00F3FF
        )
        embed.add_field(name="Message", value=message, inline=False)
        embed.add_field(name="Time", value=remind_at.strftime('%Y-%m-%d %H:%M UTC'), inline=False)
        
        await interaction.response.send_message(embed=embed)

    # ==================== AFK COMMAND ====================
    
    @app_commands.command(name="afk", description="Set your AFK status")
    @app_commands.describe(reason="Reason for being AFK")
    async def slash_afk(self, interaction: discord.Interaction, reason: str = "AFK"):
        afk_cog = self.bot.get_cog('AFK')
        if not afk_cog:
            await interaction.response.send_message("❌ AFK system not loaded!", ephemeral=True)
            return
        
        afk_cog.set_afk(interaction.user.id, reason)
        
        await interaction.response.send_message(f"💤 You are now AFK: {reason}")

    # ==================== SERVER STATS COMMANDS ====================
    
    @app_commands.command(name="serverstats", description="Show server statistics")
    async def slash_serverstats(self, interaction: discord.Interaction):
        stats_cog = self.bot.get_cog('ServerStats')
        if not stats_cog:
            await interaction.response.send_message("❌ Server Stats system not loaded!", ephemeral=True)
            return
        
        stats = stats_cog.get_server_stats(interaction.guild.id)
        
        # Get top 5 most active users
        top_users = sorted(
            stats.get('most_active_users', {}).items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        embed = discord.Embed(
            title=f"📊 {interaction.guild.name} Statistics",
            color=0x00F3FF
        )
        embed.add_field(name="Total Messages", value=f"{stats.get('total_messages', 0):,}", inline=True)
        embed.add_field(name="Members", value=f"{interaction.guild.member_count}", inline=True)
        embed.add_field(name="Channels", value=f"{len(interaction.guild.channels)}", inline=True)
        
        if top_users:
            users_text = "\n".join([
                f"{i+1}. <@{user_id}>: {count} msgs"
                for i, (user_id, count) in enumerate(top_users)
            ])
            embed.add_field(name="🔥 Most Active Users", value=users_text, inline=False)
        
        await interaction.response.send_message(embed=embed)

    # ==================== SUGGESTION COMMANDS ====================
    
    @app_commands.command(name="suggest", description="Submit a suggestion")
    @app_commands.describe(suggestion="Your suggestion")
    async def slash_suggest(self, interaction: discord.Interaction, suggestion: str):
        suggestions_cog = self.bot.get_cog('Suggestions')
        if not suggestions_cog:
            await interaction.response.send_message("❌ Suggestions system not loaded!", ephemeral=True)
            return
        
        suggestion_id = await suggestions_cog.create_suggestion(
            interaction.guild,
            interaction.user,
            suggestion
        )
        
        if suggestion_id:
            await interaction.response.send_message(f"✅ Your suggestion has been submitted! (ID: #{suggestion_id})", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Suggestions are not set up on this server!", ephemeral=True)
    
    @app_commands.command(name="setupsuggestions", description="Setup suggestion system")
    @app_commands.describe(channel="Channel for suggestions")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_setupsuggestions(self, interaction: discord.Interaction, channel: discord.TextChannel):
        suggestions_cog = self.bot.get_cog('Suggestions')
        if not suggestions_cog:
            await interaction.response.send_message("❌ Suggestions system not loaded!", ephemeral=True)
            return
        
        settings = suggestions_cog.get_suggestion_config(interaction.guild.id)
        settings['enabled'] = True
        settings['channel_id'] = channel.id
        suggestions_cog.save_suggestion_config(interaction.guild.id, settings)
        
        await interaction.response.send_message(f"✅ Suggestions channel set to {channel.mention}!")

    # ==================== ECONOMY COMMANDS ====================
    
    @app_commands.command(name="balance", description="Check your balance")
    @app_commands.describe(user="User to check (optional)")
    async def slash_balance(self, interaction: discord.Interaction, user: discord.Member = None):
        economy_cog = self.bot.get_cog('Economy')
        if not economy_cog:
            await interaction.response.send_message("❌ Economy system not loaded!", ephemeral=True)
            return
        
        target = user or interaction.user
        data = economy_cog.get_user_balance(interaction.guild.id, target.id)
        
        embed = discord.Embed(
            title=f"💰 {target.name}'s Balance",
            color=0xFFD700
        )
        embed.add_field(name="Wallet", value=f"${data['balance']:,}", inline=True)
        embed.add_field(name="Bank", value=f"${data['bank']:,}", inline=True)
        embed.add_field(name="Total", value=f"${data['balance'] + data['bank']:,}", inline=True)
        embed.set_thumbnail(url=target.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="daily", description="Claim your daily reward")
    async def slash_daily(self, interaction: discord.Interaction):
        economy_cog = self.bot.get_cog('Economy')
        if not economy_cog:
            await interaction.response.send_message("❌ Economy system not loaded!", ephemeral=True)
            return
        
        from datetime import datetime, timedelta, timezone
        
        data = economy_cog.get_user_balance(interaction.guild.id, interaction.user.id)
        
        if data['last_daily']:
            last_daily = datetime.fromisoformat(data['last_daily'])
            next_daily = last_daily + timedelta(hours=24)
            
            if datetime.now(timezone.utc) < next_daily:
                time_left = next_daily - datetime.now(timezone.utc)
                hours = int(time_left.total_seconds() // 3600)
                minutes = int((time_left.total_seconds() % 3600) // 60)
                await interaction.response.send_message(f"⏰ Daily reward available in {hours}h {minutes}m", ephemeral=True)
                return
        
        reward = 500
        data['balance'] += reward
        data['last_daily'] = datetime.now(timezone.utc).isoformat()
        economy_cog.save_user_balance(interaction.guild.id, interaction.user.id, data)
        
        embed = discord.Embed(
            title="🎁 Daily Reward Claimed!",
            description=f"You received **${reward:,}**!",
            color=0x00FF00
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="work", description="Work for money")
    async def slash_work(self, interaction: discord.Interaction):
        economy_cog = self.bot.get_cog('Economy')
        if not economy_cog:
            await interaction.response.send_message("❌ Economy system not loaded!", ephemeral=True)
            return
        
        import random
        from datetime import datetime, timedelta, timezone
        
        data = economy_cog.get_user_balance(interaction.guild.id, interaction.user.id)
        
        if data['last_work']:
            last_work = datetime.fromisoformat(data['last_work'])
            next_work = last_work + timedelta(hours=1)
            
            if datetime.now(timezone.utc) < next_work:
                time_left = next_work - datetime.now(timezone.utc)
                minutes = int(time_left.total_seconds() // 60)
                await interaction.response.send_message(f"⏰ You can work again in {minutes} minutes", ephemeral=True)
                return
        
        earnings = random.randint(50, 200)
        data['balance'] += earnings
        data['last_work'] = datetime.now(timezone.utc).isoformat()
        economy_cog.save_user_balance(interaction.guild.id, interaction.user.id, data)
        
        jobs = ["programmer", "designer", "streamer", "moderator", "artist"]
        job = random.choice(jobs)
        
        embed = discord.Embed(
            title="💼 Work Complete!",
            description=f"You worked as a **{job}** and earned **${earnings:,}**!",
            color=0x00F3FF
        )
        await interaction.response.send_message(embed=embed)

    # ==================== STARBOARD COMMANDS ====================
    
    @app_commands.command(name="starboard", description="Setup starboard system")
    @app_commands.describe(
        action="Action to perform",
        channel="Starboard channel",
        threshold="Stars needed (default: 5)"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_starboard(self, interaction: discord.Interaction, action: str, channel: discord.TextChannel = None, threshold: int = 5):
        starboard_cog = self.bot.get_cog('Starboard')
        if not starboard_cog:
            await interaction.response.send_message("❌ Starboard system not loaded!", ephemeral=True)
            return
        
        settings = starboard_cog.get_starboard_config(interaction.guild.id)
        
        if action == "enable" and channel:
            settings['enabled'] = True
            settings['channel_id'] = channel.id
            settings['threshold'] = threshold
            starboard_cog.save_starboard_config(interaction.guild.id, settings)
            await interaction.response.send_message(f"✅ Starboard enabled in {channel.mention} with threshold of {threshold} ⭐")
        elif action == "disable":
            settings['enabled'] = False
            starboard_cog.save_starboard_config(interaction.guild.id, settings)
            await interaction.response.send_message("✅ Starboard disabled!")
        else:
            await interaction.response.send_message("❌ Invalid action! Use 'enable' or 'disable'", ephemeral=True)

    # ==================== COUNTING COMMANDS ====================
    
    @app_commands.command(name="counting", description="Setup counting game")
    @app_commands.describe(channel="Counting channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_counting(self, interaction: discord.Interaction, channel: discord.TextChannel):
        counting_cog = self.bot.get_cog('Counting')
        if not counting_cog:
            await interaction.response.send_message("❌ Counting system not loaded!", ephemeral=True)
            return
        
        settings = counting_cog.get_counting_config(interaction.guild.id)
        settings['enabled'] = True
        settings['channel_id'] = channel.id
        counting_cog.save_counting_config(interaction.guild.id, settings)
        
        await interaction.response.send_message(f"✅ Counting game enabled in {channel.mention}! Start counting from 1!")

    # ==================== BIRTHDAY COMMANDS ====================
    
    @app_commands.command(name="birthday", description="Set your birthday")
    @app_commands.describe(date="Your birthday (MM-DD format, e.g., 12-25)")
    async def slash_birthday(self, interaction: discord.Interaction, date: str):
        birthday_cog = self.bot.get_cog('Birthdays')
        if not birthday_cog:
            await interaction.response.send_message("❌ Birthday system not loaded!", ephemeral=True)
            return
        
        from datetime import datetime
        
        try:
            datetime.strptime(date, '%m-%d')
        except:
            await interaction.response.send_message("❌ Invalid date format! Use MM-DD (e.g., 12-25)", ephemeral=True)
            return
        
        settings = birthday_cog.get_birthday_config(interaction.guild.id)
        settings['birthdays'][str(interaction.user.id)] = date
        birthday_cog.save_birthday_config(interaction.guild.id, settings)
        
        await interaction.response.send_message(f"🎂 Your birthday has been set to **{date}**!", ephemeral=True)

    # ==================== CONFESSION COMMANDS ====================
    
    @app_commands.command(name="confess", description="Submit an anonymous confession")
    @app_commands.describe(confession="Your confession")
    async def slash_confess(self, interaction: discord.Interaction, confession: str):
        confession_cog = self.bot.get_cog('Confessions')
        if not confession_cog:
            await interaction.response.send_message("❌ Confession system not loaded!", ephemeral=True)
            return
        
        confession_id, message = await confession_cog.submit_confession(
            interaction.guild,
            interaction.user,
            confession
        )
        
        await interaction.response.send_message(message, ephemeral=True)

    # ==================== MODMAIL COMMANDS ====================
    
    @app_commands.command(name="setupmodmail", description="Setup ModMail system")
    @app_commands.describe(category="Category for ModMail tickets")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_setupmodmail(self, interaction: discord.Interaction, category: discord.CategoryChannel):
        modmail_cog = self.bot.get_cog('ModMail')
        if not modmail_cog:
            await interaction.response.send_message("❌ ModMail system not loaded!", ephemeral=True)
            return
        
        settings = modmail_cog.get_modmail_config(interaction.guild.id)
        settings['enabled'] = True
        settings['category_id'] = category.id
        modmail_cog.save_modmail_config(interaction.guild.id, settings)
        
        await interaction.response.send_message(f"✅ ModMail enabled! Tickets will be created in {category.name}")

    # ==================== ANTI-RAID COMMANDS ====================
    
    @app_commands.command(name="antiraid", description="Configure anti-raid protection")
    @app_commands.describe(
        action="Action to perform",
        threshold="Users joining in time window",
        time_window="Time window in seconds"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_antiraid(self, interaction: discord.Interaction, action: str, threshold: int = 10, time_window: int = 10):
        antiraid_cog = self.bot.get_cog('AntiRaid')
        if not antiraid_cog:
            await interaction.response.send_message("❌ Anti-Raid system not loaded!", ephemeral=True)
            return
        
        settings = antiraid_cog.get_antiraid_config(interaction.guild.id)
        
        if action == "enable":
            settings['enabled'] = True
            settings['join_threshold'] = threshold
            settings['time_window'] = time_window
            antiraid_cog.save_antiraid_config(interaction.guild.id, settings)
            await interaction.response.send_message(f"✅ Anti-raid enabled! ({threshold} joins in {time_window}s triggers protection)")
        elif action == "disable":
            settings['enabled'] = False
            antiraid_cog.save_antiraid_config(interaction.guild.id, settings)
            await interaction.response.send_message("✅ Anti-raid disabled!")
        else:
            await interaction.response.send_message("❌ Invalid action! Use 'enable' or 'disable'", ephemeral=True)

    # ==================== MISC UTILITY COMMANDS ====================
    
    @app_commands.command(name="rolepersist", description="Toggle role persistence")
    @app_commands.describe(enabled="Enable or disable")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_rolepersist(self, interaction: discord.Interaction, enabled: bool):
        rolepersist_cog = self.bot.get_cog('RolePersist')
        if not rolepersist_cog:
            await interaction.response.send_message("❌ Role Persistence not loaded!", ephemeral=True)
            return
        
        settings = rolepersist_cog.get_persist_config(interaction.guild.id)
        settings['enabled'] = enabled
        rolepersist_cog.save_persist_config(interaction.guild.id, settings)
        
        status = "enabled" if enabled else "disabled"
        await interaction.response.send_message(f"✅ Role persistence {status}!")
    
    @app_commands.command(name="tempban", description="Temporarily ban a user")
    @app_commands.describe(
        user="User to ban",
        duration="Duration (e.g., 1h, 2d, 30m)",
        reason="Ban reason"
    )
    @app_commands.checks.has_permissions(ban_members=True)
    async def slash_tempban(self, interaction: discord.Interaction, user: discord.Member, duration: str, reason: str = "No reason provided"):
        tempban_cog = self.bot.get_cog('TempBans')
        if not tempban_cog:
            await interaction.response.send_message("❌ TempBan system not loaded!", ephemeral=True)
            return
        
        from datetime import datetime, timedelta, timezone
        
        # Parse duration
        time_units = {'h': 3600, 'd': 86400, 'm': 60}
        try:
            amount = int(duration[:-1])
            unit = duration[-1]
            seconds = amount * time_units[unit]
        except:
            await interaction.response.send_message("❌ Invalid duration! Use format: 1h, 2d, 30m", ephemeral=True)
            return
        
        unban_at = datetime.now(timezone.utc) + timedelta(seconds=seconds)
        
        try:
            await user.ban(reason=reason)
            tempban_cog.add_tempban(interaction.guild.id, user.id, unban_at)
            await interaction.response.send_message(f"✅ {user.mention} banned for {duration}. Unban at: {unban_at.strftime('%Y-%m-%d %H:%M UTC')}")
        except:
            await interaction.response.send_message("❌ Failed to ban user!", ephemeral=True)
    
    @app_commands.command(name="cmdstats", description="View command usage statistics")
    async def slash_cmdstats(self, interaction: discord.Interaction):
        stats_cog = self.bot.get_cog('CommandStats')
        if not stats_cog:
            await interaction.response.send_message("❌ Command Stats not loaded!", ephemeral=True)
            return
        
        stats = stats_cog.get_command_stats(interaction.guild.id)
        
        if not stats:
            await interaction.response.send_message("No command statistics yet!", ephemeral=True)
            return
        
        # Get top 10 commands
        top_commands = sorted(stats.get('commands', {}).items(), key=lambda x: x[1], reverse=True)[:10]
        
        embed = discord.Embed(
            title="📊 Command Statistics",
            description=f"Total Commands Used: **{stats.get('total_commands', 0):,}**",
            color=0x00F3FF
        )
        
        if top_commands:
            commands_text = "\n".join([f"{i+1}. `{cmd}` - {count} uses" for i, (cmd, count) in enumerate(top_commands)])
            embed.add_field(name="Top Commands", value=commands_text, inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    # ==================== MINI-GAMES COMMANDS ====================
    
    @app_commands.command(name="trivia", description="Play a trivia game")
    @app_commands.describe(category="Trivia category (general, gaming, tech)")
    async def slash_trivia(self, interaction: discord.Interaction, category: str = "general"):
        minigames_cog = self.bot.get_cog('MiniGames')
        if not minigames_cog:
            await interaction.response.send_message("❌ Mini-games not loaded!", ephemeral=True)
            return
        
        await minigames_cog.play_trivia(interaction, category)
    
    @app_commands.command(name="blackjack", description="Play blackjack")
    @app_commands.describe(bet="Amount to bet")
    async def slash_blackjack(self, interaction: discord.Interaction, bet: int = 100):
        minigames_cog = self.bot.get_cog('MiniGames')
        if not minigames_cog:
            await interaction.response.send_message("❌ Mini-games not loaded!", ephemeral=True)
            return
        
        await minigames_cog.play_blackjack(interaction, bet)
    
    @app_commands.command(name="slots", description="Play the slot machine")
    @app_commands.describe(bet="Amount to bet")
    async def slash_slots(self, interaction: discord.Interaction, bet: int = 50):
        minigames_cog = self.bot.get_cog('MiniGames')
        if not minigames_cog:
            await interaction.response.send_message("❌ Mini-games not loaded!", ephemeral=True)
            return
        
        await minigames_cog.play_slots(interaction, bet)
    
    @app_commands.command(name="coinflip", description="Flip a coin")
    @app_commands.describe(bet="Amount to bet", choice="Heads or tails")
    async def slash_coinflip(self, interaction: discord.Interaction, bet: int, choice: str):
        minigames_cog = self.bot.get_cog('MiniGames')
        if not minigames_cog:
            await interaction.response.send_message("❌ Mini-games not loaded!", ephemeral=True)
            return
        
        await minigames_cog.play_coinflip(interaction, bet, choice)
    
    @app_commands.command(name="scramble", description="Play word scramble")
    async def slash_scramble(self, interaction: discord.Interaction):
        minigames_cog = self.bot.get_cog('MiniGames')
        if not minigames_cog:
            await interaction.response.send_message("❌ Mini-games not loaded!", ephemeral=True)
            return
        
        await minigames_cog.play_scramble(interaction)
    
    @app_commands.command(name="connectfour", description="Play Connect Four")
    @app_commands.describe(opponent="User to play against")
    async def slash_connectfour(self, interaction: discord.Interaction, opponent: discord.Member):
        connectfour_cog = self.bot.get_cog('ConnectFour')
        if not connectfour_cog:
            await interaction.response.send_message("❌ Connect Four not loaded!", ephemeral=True)
            return
        
        await connectfour_cog.start_game(interaction, opponent)
    
    # ==================== REPUTATION COMMANDS ====================
    
    @app_commands.command(name="rep", description="Give reputation to a user")
    @app_commands.describe(user="User to give reputation to", positive="Positive or negative")
    async def slash_rep(self, interaction: discord.Interaction, user: discord.Member, positive: bool = True):
        rep_cog = self.bot.get_cog('Reputation')
        if not rep_cog:
            await interaction.response.send_message("❌ Reputation system not loaded!", ephemeral=True)
            return
        
        await rep_cog.give_rep(interaction, user, positive)
    
    # ==================== ADVANCED ECONOMY COMMANDS ====================
    
    @app_commands.command(name="rob", description="Attempt to rob another user")
    @app_commands.describe(user="User to rob")
    async def slash_rob(self, interaction: discord.Interaction, user: discord.Member):
        adveconomy_cog = self.bot.get_cog('AdvancedEconomy')
        if not adveconomy_cog:
            await interaction.response.send_message("❌ Advanced Economy not loaded!", ephemeral=True)
            return
        
        await adveconomy_cog.rob_user(interaction, user)
    
    @app_commands.command(name="shop", description="View the item shop")
    async def slash_shop(self, interaction: discord.Interaction):
        adveconomy_cog = self.bot.get_cog('AdvancedEconomy')
        if not adveconomy_cog:
            await interaction.response.send_message("❌ Advanced Economy not loaded!", ephemeral=True)
            return
        
        await adveconomy_cog.show_shop(interaction)
    
    @app_commands.command(name="buy", description="Buy an item from the shop")
    @app_commands.describe(item_id="Item ID to purchase")
    async def slash_buy(self, interaction: discord.Interaction, item_id: str):
        adveconomy_cog = self.bot.get_cog('AdvancedEconomy')
        if not adveconomy_cog:
            await interaction.response.send_message("❌ Advanced Economy not loaded!", ephemeral=True)
            return
        
        await adveconomy_cog.buy_item(interaction, item_id)
    
    # ==================== SETUP & HELP COMMANDS ====================
    
    @app_commands.command(name="setup", description="Interactive setup wizard / Telepítési varázsló")
    async def slash_setup(self, interaction: discord.Interaction):
        from translations import get_text
        setup_cog = self.bot.get_cog('SetupWizard')
        if not setup_cog:
            await interaction.response.send_message("❌ Setup wizard not loaded!", ephemeral=True)
            return
        
        await setup_cog.start_setup(interaction)
    
    @app_commands.command(name="help", description="View bot help menu / Súgó menü megtekintése")
    async def slash_help(self, interaction: discord.Interaction):
        from translations import get_text
        help_cog = self.bot.get_cog('InteractiveHelp')
        if not help_cog:
            await interaction.response.send_message("❌ Help system not loaded!", ephemeral=True)
            return
        
        await help_cog.show_help(interaction)

async def setup(bot):
    print("📝 Setting up SlashCommands cog...")
    try:
        await bot.add_cog(SlashCommands(bot))
        print("✅ SlashCommands cog added successfully!")
    except Exception as e:
        print(f"❌ Failed to setup SlashCommands: {e}")
        import traceback
        traceback.print_exc()

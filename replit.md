# ⚡ SHADOW-MOD ✨ | Futuristic Discord Bot

## Overview
**Next-Gen Discord Moderation System v4.0 ULTIMATE MEGA EDITION**

SHADOW-MOD is the MOST comprehensive, cyberpunk-themed Discord bot built with Python, designed to be the ultimate all-in-one solution for Discord servers. With **58 feature modules** and **100+ slash commands**, it combines advanced moderation, economy, analytics, utility, mini-games, AI moderation, and entertainment systems into a single powerful bot. The bot features multilanguage support (English & Hungarian), an AI Chat Assistant powered by OpenAI, a robust music system with Spotify/YouTube/SoundCloud support, and a sophisticated verification process with anti-alt protection.

**Core Features (27 Original Modules):** Advanced moderation suite (ban, kick, mute, tempban, warnings), ticket system, comprehensive logging, interactive games (RPS, Tic-Tac-Toe), fun commands, polls, role management, giveaways, name automation, verification, music playback, custom commands, auto-moderation, welcome/goodbye systems, reaction roles, leveling/XP system, reminders, AFK status, server statistics, and community suggestions.

**NEW Advanced Features (19 Modules):** 
- **💰 Economy System:** Virtual currency, daily rewards, work commands, shop system, inventory management
- **⭐ Starboard:** Auto-pin highly-starred messages to showcase community highlights
- **🔢 Counting Game:** Addictive sequential counting with high scores and milestones
- **🎂 Birthday Tracker:** Automatic birthday celebrations with messages and roles
- **🎭 Confessions:** Anonymous confession system with approval queue
- **📬 ModMail:** Professional DM-based support ticket system
- **🚨 Anti-Raid Protection:** Advanced detection and auto-ban for coordinated raids
- **📝 Advanced Logging:** Message edits/deletions, voice activity, role changes, username tracking
- **🔄 Role Persistence:** Save and restore member roles on rejoin
- **⏱️ Temporary Bans:** Auto-unban after set time periods
- **📢 Custom Embed Builder:** Create beautiful embed messages via commands
- **🔊 Temporary Voice Channels:** Auto-create/delete voice channels
- **🎬 Stream Alerts:** Notify when members go live on Discord
- **💾 Server Backup:** Full backup and restore of server settings, roles, and channels
- **🎵 Playlist Manager:** Personal music playlists for users
- **📈 Growth Tracking:** Member count analytics with historical data
- **🏆 Achievement System:** Unlock badges for milestones and activities
- **📱 Social Media Integration:** Framework for posting to Twitter/Instagram
- **📊 Command Usage Stats:** Detailed analytics on command usage

With 75+ slash commands, extensive customization, and a futuristic cyberpunk aesthetic, SHADOW-MOD represents the pinnacle of Discord bot development.

## User Preferences
None specified yet.

## System Architecture
The bot is built with a modular, cog-based architecture in Python, ensuring maintainability and scalability. It features dual prefix support (`!` and `/`) and extensive slash command implementations (90+ commands across 46 cogs). A Flask web server (`web_server.py`) provides a live statistics dashboard, sharing data via `bot_stats.json`. Configuration is managed through `config.py` and `bot_config.json`, with multilingual translations handled by `translations.py`.

**Cog Structure (58 Total Modules):**
- Original (27): tickets, antialt, logging, moderation, games, fun, polls, roles, giveaways, nameauto, webhook_logging, language, aichat, verify, info, music, admin, customcommands, automod, welcome, reactionroles, leveling, reminders, afk, serverstats, suggestions, slash_commands
- v3.0 Expansion (19): economy, starboard, counting, birthdays, confessions, modmail, antiraid, advancedlogging, rolepersist, tempbans, embedbuilder, tempvoice, streamalerts, serverbackup, playlists, growthtracking, achievements, socialmedia, commandstats
- v4.0 MEGA Expansion (12): minigames, connectfour, reputation, events, setupwizard, interactivehelp, advancedeconomy, aimoderation, voiceanalytics, appealssystem, memeeconomy, botstatus, webhooks

**UI/UX Decisions:**
- **Cyberpunk Neon Theme:** The bot and its accompanying web dashboard feature a futuristic, cyberpunk neon aesthetic with cyan, pink, purple, and blue color schemes.
- **Interactive Components:** All features heavily utilize Discord embeds, buttons, and other interactive components for a modern and engaging user experience.
- **Responsive Design:** The web dashboard is fully mobile-responsive, ensuring usability across various devices.
- **Readability:** UI elements are designed for eye comfort, with reduced excessive glow effects, dimmed backgrounds, and improved text readability with outlines/shadows.

**Technical Implementations:**
- **AI Chat Assistant:** Powered by OpenAI, responding to mentions in designated channels.
- **Music System:** Utilizes Lavalink for robust music playback from YouTube, Spotify (with metadata), and SoundCloud, managed via the `wavelink` library.
- **Verification System:** Button-based verification with integrated anti-alt account detection.
- **Custom Commands:** An owner-only system to create, remove, and modify custom text commands, stored dynamically.
- **Auto-Moderation:** Automated detection and punishment for spam, bad words, suspicious links, excessive caps, and emoji spam.
- **Logging:** Advanced logging to Discord channels for events, and a separate webhook logging system for bot errors and critical events.
- **Persistent Data:** Uses `bot_config.json` for runtime configuration and `bot_stats.json` for shared statistics.
- **Database:** Not explicitly stated, but implies local file-based storage for configurations and stats.

**Feature Specifications:**
- **Multi-language Support:** English and Hungarian, with a language switching command.
- **Server Management:** Comprehensive moderation suite (ban, kick, mute, tempmute, tempban, lock, unlock, warnings), role management, custom prefixes.
- **User Engagement:** Interactive games (RPS, Tic-Tac-Toe), fun commands (memes, sounds, 8ball), polls with live voting, giveaways, leveling/XP system with role rewards, reminders, AFK status.
- **Server Customization:** Customizable welcome/goodbye messages with auto-roles, reaction roles, name automation with role-based prefixes, suggestion system.
- **Information & Analytics:** Server info, bot info, user info (with badges), server statistics tracking.

## External Dependencies
- **Discord API:** Core integration for bot functionality
- **OpenAI API:** For the AI Chat Assistant feature (`OPENAI_API_KEY`)
- **Lavalink:** Used by the `wavelink` library for the music system; connects to public Lavalink nodes
- **Spotify API:** For Spotify track metadata integration within the music system (`SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`)
- **Flask:** Python web framework for the web statistics dashboard
- **Meme API:** For the multilingual meme generator
- **Twitter/Instagram APIs:** (Optional) For social media integration feature

## Recent Changes
**November 11, 2025 - v4.0 ULTIMATE MEGA EDITION Release:**
- Added 12 MEGA features: Mini-Games Suite (Trivia, Blackjack, Slots, Coinflip, Word Scramble, Connect Four), Reputation System, Events with RSVP, Setup Wizard, Interactive Help Menu, Advanced Economy (Shop, Trading, Robbery), AI-Powered Auto-Moderation, Voice Analytics, Ban Appeals System, Meme Economy Competition, Dynamic Bot Status, and Webhook Integrations
- Implemented 40+ new slash commands (100+ total commands now!)
- Expanded bot from 46 to 58 total cogs
- Added PostgreSQL database support for production-ready scalability
- Integrated OpenAI for intelligent content moderation
- Built comprehensive mini-games system with economy integration
- Added event management with automated reminders
- Created interactive setup wizard for easy configuration
- Deployed voice channel analytics and tracking
- Built meme competition system with monthly rewards

**v3.0 Ultimate Edition (Earlier Today):**
- Added 19 advanced feature systems
- Expanded from 27 to 46 cogs
- Implemented economy, starboard, counting, modmail, anti-raid, and more
import discord
from discord.ext import commands
import config
import translations
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from hungarian_automod import has_bad_words, detect_language, merge_bad_words, get_bad_words_for_language
from database import get_guild_settings

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_cache = defaultdict(list)
        self.spam_cooldown = {}
        
    def get_automod_config(self, guild_id):
        """Get automod settings for a guild"""
        cfg = config.load_config()
        automod = cfg.get('automod', {})
        return automod.get(str(guild_id), {
            'enabled': False,
            'spam_detection': True,
            'link_filter': False,
            'bad_words': [],
            'caps_filter': False,
            'emoji_spam': False,
            'max_messages': 5,
            'time_window': 5,
            'punishment': 'warn'
        })
    
    def save_automod_config(self, guild_id, settings):
        """Save automod settings"""
        cfg = config.load_config()
        if 'automod' not in cfg:
            cfg['automod'] = {}
        cfg['automod'][str(guild_id)] = settings
        config.save_config(cfg)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        
        # Skip if user has manage messages permission
        if message.author.guild_permissions.manage_messages:
            return
        
        settings = self.get_automod_config(message.guild.id)
        
        if not settings['enabled']:
            return
        
        # Spam detection
        if settings['spam_detection']:
            if await self.check_spam(message, settings):
                return
        
        # Bad words filter
        if settings['bad_words']:
            if await self.check_bad_words(message, settings):
                return
        
        # Link filter
        if settings['link_filter']:
            if await self.check_links(message):
                return
        
        # Caps filter
        if settings['caps_filter']:
            if await self.check_caps(message):
                return
        
        # Emoji spam
        if settings['emoji_spam']:
            if await self.check_emoji_spam(message):
                return
    
    async def check_spam(self, message, settings):
        """Detect message spam"""
        guild_id = message.guild.id
        author_id = message.author.id
        now = datetime.now(timezone.utc)
        
        # Clean old messages
        self.message_cache[author_id] = [
            msg_time for msg_time in self.message_cache[author_id]
            if (now - msg_time).total_seconds() < settings['time_window']
        ]
        
        # Add current message
        self.message_cache[author_id].append(now)
        
        # Check if spam threshold exceeded
        if len(self.message_cache[author_id]) > settings['max_messages']:
            await self.punish_user(message, "Message spam detected", settings['punishment'])
            self.message_cache[author_id].clear()
            return True
        
        return False
    
    async def check_bad_words(self, message, settings):
        """Check for bad words with language support"""
        # Get guild language setting
        db_settings = get_guild_settings(str(message.guild.id))
        guild_language = db_settings.get('language', 'en')
        
        # Merge language-specific bad words with custom ones
        custom_bad_words = db_settings.get('bad_words', [])
        bad_words_list = merge_bad_words(guild_language, custom_bad_words or [])
        
        # Auto-detect message language
        detected_lang = detect_language(message.content)
        
        # Check for bad words
        found_bad, bad_word = has_bad_words(message.content, guild_language, custom_bad_words)
        
        if found_bad:
            try:
                await message.delete()
                
                # Localized message
                if guild_language == 'hu':
                    msg = f"⚠️ {message.author.mention}, megfelelő viselkedés szükséges!"
                else:
                    msg = f"⚠️ {message.author.mention}, please watch your language!"
                
                await message.channel.send(msg, delete_after=5)
                await self.punish_user(message, f"Used inappropriate word: {bad_word}", settings['punishment'])
            except:
                pass
            return True
        
        return False
    
    async def check_links(self, message):
        """Check for links/invites"""
        url_pattern = r'https?://|discord\.gg/|discord\.com/invite/'
        
        if re.search(url_pattern, message.content, re.IGNORECASE):
            try:
                await message.delete()
                await message.channel.send(
                    f"⚠️ {message.author.mention}, links are not allowed!",
                    delete_after=5
                )
            except:
                pass
            return True
        
        return False
    
    async def check_caps(self, message):
        """Check for excessive caps"""
        if len(message.content) < 5:
            return False
        
        caps_ratio = sum(1 for c in message.content if c.isupper()) / len(message.content)
        
        if caps_ratio > 0.7:
            try:
                await message.delete()
                await message.channel.send(
                    f"⚠️ {message.author.mention}, please don't use excessive caps!",
                    delete_after=5
                )
            except:
                pass
            return True
        
        return False
    
    async def check_emoji_spam(self, message):
        """Check for emoji spam"""
        emoji_count = len(re.findall(r'<a?:\w+:\d+>|[\U0001F600-\U0001F64F]', message.content))
        
        if emoji_count > 10:
            try:
                await message.delete()
                await message.channel.send(
                    f"⚠️ {message.author.mention}, too many emojis!",
                    delete_after=5
                )
            except:
                pass
            return True
        
        return False
    
    async def punish_user(self, message, reason, punishment):
        """Punish user based on settings"""
        if punishment == 'warn':
            # Add warning
            cfg = config.load_config()
            if 'warnings' not in cfg:
                cfg['warnings'] = {}
            
            user_id = str(message.author.id)
            if user_id not in cfg['warnings']:
                cfg['warnings'][user_id] = []
            
            cfg['warnings'][user_id].append({
                'reason': reason,
                'moderator': 'AutoMod',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            config.save_config(cfg)
            
        elif punishment == 'mute':
            try:
                timeout_duration = timedelta(minutes=5)
                await message.author.timeout(timeout_duration, reason=reason)
            except:
                pass
        
        elif punishment == 'kick':
            try:
                await message.author.kick(reason=reason)
            except:
                pass

async def setup(bot):
    await bot.add_cog(AutoMod(bot))

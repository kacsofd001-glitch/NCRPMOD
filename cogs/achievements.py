import discord
from discord.ext import commands
import config

class Achievements(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.achievement_definitions = {
            'first_message': {
                'name': '💬 First Steps',
                'description': 'Send your first message',
                'icon': '💬'
            },
            'hundred_messages': {
                'name': '📝 Chatterbox',
                'description': 'Send 100 messages',
                'icon': '📝'
            },
            'thousand_messages': {
                'name': '🗣️ Conversation Master',
                'description': 'Send 1,000 messages',
                'icon': '🗣️'
            },
            'first_level': {
                'name': '⭐ Rising Star',
                'description': 'Reach level 1',
                'icon': '⭐'
            },
            'level_10': {
                'name': '🌟 Veteran',
                'description': 'Reach level 10',
                'icon': '🌟'
            },
            'level_50': {
                'name': '👑 Legend',
                'description': 'Reach level 50',
                'icon': '👑'
            },
            'early_bird': {
                'name': '🌅 Early Bird',
                'description': 'Send a message at 6 AM',
                'icon': '🌅'
            },
            'night_owl': {
                'name': '🦉 Night Owl',
                'description': 'Send a message at 3 AM',
                'icon': '🦉'
            },
            'helper': {
                'name': '🤝 Helpful',
                'description': 'Answer 10 questions in support',
                'icon': '🤝'
            },
            'one_year': {
                'name': '🎂 Anniversary',
                'description': 'Be in the server for 1 year',
                'icon': '🎂'
            }
        }
    
    def get_user_achievements(self, guild_id, user_id):
        """Get user's unlocked achievements"""
        cfg = config.load_config()
        achievements = cfg.get('user_achievements', {})
        guild_achievements = achievements.get(str(guild_id), {})
        return guild_achievements.get(str(user_id), [])
    
    def unlock_achievement(self, guild_id, user_id, achievement_id):
        """Unlock achievement for user"""
        cfg = config.load_config()
        if 'user_achievements' not in cfg:
            cfg['user_achievements'] = {}
        if str(guild_id) not in cfg['user_achievements']:
            cfg['user_achievements'][str(guild_id)] = {}
        if str(user_id) not in cfg['user_achievements'][str(guild_id)]:
            cfg['user_achievements'][str(guild_id)][str(user_id)] = []
        
        if achievement_id not in cfg['user_achievements'][str(guild_id)][str(user_id)]:
            cfg['user_achievements'][str(guild_id)][str(user_id)].append(achievement_id)
            config.save_config(cfg)
            return True
        return False
    
    async def notify_achievement(self, channel, user, achievement_id):
        """Send achievement unlock notification"""
        achievement = self.achievement_definitions.get(achievement_id)
        if not achievement:
            return
        
        embed = discord.Embed(
            title="🏆 Achievement Unlocked!",
            description=f"{achievement['icon']} **{achievement['name']}**\n{achievement['description']}",
            color=0xFFD700
        )
        embed.set_author(name=user.name, icon_url=user.display_avatar.url)
        
        await channel.send(f"{user.mention}", embed=embed, delete_after=30)

async def setup(bot):
    await bot.add_cog(Achievements(bot))

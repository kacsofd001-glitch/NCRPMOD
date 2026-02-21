import discord
from discord.ext import commands, tasks
import config
from datetime import datetime, timedelta, timezone
import asyncio

class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_reminders.start()
    
    def cog_unload(self):
        self.check_reminders.cancel()
    
    def get_reminders(self):
        """Get all reminders"""
        cfg = config.load_config()
        return cfg.get('reminders', [])
    
    def save_reminders(self, reminders):
        """Save reminders"""
        cfg = config.load_config()
        cfg['reminders'] = reminders
        config.save_config(cfg)
    
    def add_reminder(self, user_id, channel_id, guild_id, message, remind_at, recurring=None):
        """Add a new reminder"""
        reminders = self.get_reminders()
        
        reminder = {
            'id': len(reminders) + 1,
            'user_id': user_id,
            'channel_id': channel_id,
            'guild_id': guild_id,
            'message': message,
            'remind_at': remind_at.isoformat(),
            'recurring': recurring,
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        reminders.append(reminder)
        self.save_reminders(reminders)
        return reminder['id']
    
    @tasks.loop(seconds=30)
    async def check_reminders(self):
        """Check for due reminders"""
        reminders = self.get_reminders()
        now = datetime.now(timezone.utc)
        
        reminders_to_remove = []
        
        for reminder in reminders:
            remind_at = datetime.fromisoformat(reminder['remind_at'])
            
            if now >= remind_at:
                # Send reminder
                try:
                    channel = self.bot.get_channel(reminder['channel_id'])
                    user = self.bot.get_user(reminder['user_id'])
                    
                    if channel and user:
                        embed = discord.Embed(
                            title="⏰ Reminder!",
                            description=reminder['message'],
                            color=0x00F3FF
                        )
                        embed.set_footer(text=f"Set on {datetime.fromisoformat(reminder['created_at']).strftime('%Y-%m-%d %H:%M UTC')}")
                        await channel.send(f"{user.mention}", embed=embed)
                except:
                    pass
                
                # Handle recurring
                if reminder['recurring']:
                    # Update next remind time
                    next_remind = remind_at + timedelta(seconds=reminder['recurring'])
                    reminder['remind_at'] = next_remind.isoformat()
                else:
                    reminders_to_remove.append(reminder)
        
        # Remove completed reminders
        for reminder in reminders_to_remove:
            reminders.remove(reminder)
        
        if reminders_to_remove:
            self.save_reminders(reminders)
    
    @check_reminders.before_loop
    async def before_check_reminders(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Reminders(bot))

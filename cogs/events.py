import discord
from discord.ext import commands, tasks
import config
from datetime import datetime, timezone

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_events.start()
    
    def cog_unload(self):
        self.check_events.cancel()
    
    def get_events(self, guild_id):
        """Get all events for a guild"""
        cfg = config.load_config()
        events = cfg.get('events', {})
        return events.get(str(guild_id), {})
    
    def save_event(self, guild_id, event_id, event_data):
        """Save an event"""
        cfg = config.load_config()
        if 'events' not in cfg:
            cfg['events'] = {}
        if str(guild_id) not in cfg['events']:
            cfg['events'][str(guild_id)] = {}
        cfg['events'][str(guild_id)][str(event_id)] = event_data
        config.save_config(cfg)
    
    def create_event(self, guild_id, name, description, date_time, creator_id):
        """Create a new event"""
        events = self.get_events(guild_id)
        event_id = len(events) + 1
        
        event_data = {
            'name': name,
            'description': description,
            'date_time': date_time,
            'creator_id': creator_id,
            'attendees': [],
            'maybe': [],
            'not_attending': [],
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        self.save_event(guild_id, event_id, event_data)
        return event_id
    
    @tasks.loop(minutes=30)
    async def check_events(self):
        """Check for upcoming events and send reminders"""
        try:
            now = datetime.now(timezone.utc)
            
            cfg = config.load_config()
            all_events = cfg.get('events', {})
            
            for guild_id, events in all_events.items():
                try:
                    guild = self.bot.get_guild(int(guild_id))
                    if not guild:
                        continue
                    
                    for event_id, event_data in events.items():
                        try:
                            event_time = datetime.fromisoformat(event_data['date_time'])
                            time_until = event_time - now
                            
                            if timedelta(hours=1) <= time_until <= timedelta(hours=1, minutes=30):
                                await self.send_reminder(guild, event_data, "1 hour")
                            elif timedelta(hours=24) <= time_until <= timedelta(hours=24, minutes=30):
                                await self.send_reminder(guild, event_data, "24 hours")
                        except Exception as e:
                            print(f"Error processing event {event_id}: {e}")
                            continue
                except Exception as e:
                    print(f"Error processing guild {guild_id} events: {e}")
                    continue
        except Exception as e:
            print(f"Error in check_events loop: {e}")
    
    async def send_reminder(self, guild, event_data, time_str):
        """Send event reminder"""
        channel = guild.system_channel
        if not channel:
            return
        
        attendees = event_data.get('attendees', [])
        if not attendees:
            return
        
        mentions = " ".join([f"<@{user_id}>" for user_id in attendees])
        
        embed = discord.Embed(
            title=f"⏰ Event Reminder: {event_data['name']}",
            description=f"This event starts in {time_str}!\n\n{event_data['description']}",
            color=0xFFA500
        )
        
        await channel.send(mentions, embed=embed)
    
    @check_events.before_loop
    async def before_check_events(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Events(bot))

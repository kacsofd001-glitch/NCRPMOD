import discord
from discord.ext import commands
import config

class ModMail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def get_modmail_config(self, guild_id):
        """Get modmail settings"""
        cfg = config.load_config()
        modmail = cfg.get('modmail', {})
        return modmail.get(str(guild_id), {
            'enabled': False,
            'category_id': None,
            'active_tickets': {}
        })
    
    def save_modmail_config(self, guild_id, settings):
        """Save modmail settings"""
        cfg = config.load_config()
        if 'modmail' not in cfg:
            cfg['modmail'] = {}
        cfg['modmail'][str(guild_id)] = settings
        config.save_config(cfg)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore bots and guild messages
        if message.author.bot or message.guild:
            return
        
        # User sent DM to bot - check all guilds for modmail
        for guild in self.bot.guilds:
            member = guild.get_member(message.author.id)
            if not member:
                continue
            
            settings = self.get_modmail_config(guild.id)
            if not settings['enabled']:
                continue
            
            user_key = str(message.author.id)
            
            # Check if user has active ticket
            if user_key in settings['active_tickets']:
                channel_id = settings['active_tickets'][user_key]
                channel = guild.get_channel(channel_id)
                
                if channel:
                    embed = discord.Embed(
                        description=message.content,
                        color=0x00F3FF,
                        timestamp=discord.utils.utcnow()
                    )
                    embed.set_author(name=message.author.name, icon_url=message.author.display_avatar.url)
                    
                    if message.attachments:
                        embed.set_image(url=message.attachments[0].url)
                    
                    await channel.send(embed=embed)
                    await message.add_reaction('✅')
                    return
            
            # Create new ticket
            category = guild.get_channel(settings['category_id'])
            if not category:
                continue
            
            channel = await guild.create_text_channel(
                name=f"modmail-{message.author.name}",
                category=category,
                topic=f"ModMail ticket for {message.author.name} ({message.author.id})"
            )
            
            settings['active_tickets'][user_key] = channel.id
            self.save_modmail_config(guild.id, settings)
            
            # Send opening message
            embed = discord.Embed(
                title="📬 New ModMail Ticket",
                description=f"**User:** {message.author.mention} ({message.author.name})\n**ID:** {message.author.id}",
                color=0x00F3FF
            )
            await channel.send(embed=embed)
            
            # Send first message
            msg_embed = discord.Embed(
                description=message.content,
                color=0x00F3FF,
                timestamp=discord.utils.utcnow()
            )
            msg_embed.set_author(name=message.author.name, icon_url=message.author.display_avatar.url)
            await channel.send(embed=msg_embed)
            
            # Confirm to user
            await message.add_reaction('✅')
            await message.author.send("✅ Your message has been sent to the server staff! They will respond soon.")
            return

async def setup(bot):
    await bot.add_cog(ModMail(bot))

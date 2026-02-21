import discord
from discord.ext import commands
import config

class Confessions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def get_confession_config(self, guild_id):
        """Get confession settings"""
        cfg = config.load_config()
        confessions = cfg.get('confessions', {})
        return confessions.get(str(guild_id), {
            'enabled': False,
            'channel_id': None,
            'approval_channel_id': None,
            'require_approval': True,
            'counter': 0,
            'pending': {}
        })
    
    def save_confession_config(self, guild_id, settings):
        """Save confession settings"""
        cfg = config.load_config()
        if 'confessions' not in cfg:
            cfg['confessions'] = {}
        cfg['confessions'][str(guild_id)] = settings
        config.save_config(cfg)
    
    async def submit_confession(self, guild, user, confession_text):
        """Submit a new confession"""
        settings = self.get_confession_config(guild.id)
        
        if not settings['enabled']:
            return None, "Confessions are not enabled on this server!"
        
        settings['counter'] += 1
        confession_id = settings['counter']
        
        if settings['require_approval'] and settings['approval_channel_id']:
            # Send to approval queue
            approval_channel = guild.get_channel(settings['approval_channel_id'])
            if not approval_channel:
                return None, "Approval channel not found!"
            
            embed = discord.Embed(
                title=f"📝 Confession #{confession_id} (Pending Approval)",
                description=confession_text,
                color=0xFFA500
            )
            embed.set_footer(text=f"Submitted by {user.name} ({user.id})")
            
            view = discord.ui.View(timeout=None)
            approve_button = discord.ui.Button(label="✅ Approve", style=discord.ButtonStyle.success, custom_id=f"confession_approve_{confession_id}")
            deny_button = discord.ui.Button(label="❌ Deny", style=discord.ButtonStyle.danger, custom_id=f"confession_deny_{confession_id}")
            view.add_item(approve_button)
            view.add_item(deny_button)
            
            msg = await approval_channel.send(embed=embed, view=view)
            
            settings['pending'][str(confession_id)] = {
                'text': confession_text,
                'user_id': user.id,
                'approval_msg_id': msg.id
            }
            self.save_confession_config(guild.id, settings)
            
            return confession_id, "Confession submitted for approval!"
        else:
            # Post directly
            channel = guild.get_channel(settings['channel_id'])
            if not channel:
                return None, "Confession channel not found!"
            
            embed = discord.Embed(
                title=f"📝 Anonymous Confession #{confession_id}",
                description=confession_text,
                color=0x00F3FF
            )
            await channel.send(embed=embed)
            
            self.save_confession_config(guild.id, settings)
            return confession_id, "Confession posted!"

async def setup(bot):
    await bot.add_cog(Confessions(bot))

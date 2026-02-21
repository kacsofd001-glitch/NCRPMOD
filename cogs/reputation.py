import discord
from discord.ext import commands
import config
from datetime import datetime, timedelta, timezone

class Reputation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def get_user_rep(self, guild_id, user_id):
        """Get user reputation data"""
        cfg = config.load_config()
        rep = cfg.get('reputation', {})
        guild_rep = rep.get(str(guild_id), {})
        return guild_rep.get(str(user_id), {
            'rep': 0,
            'given_reps': {},
            'last_gave': None,
            'received_from': []
        })
    
    def save_user_rep(self, guild_id, user_id, data):
        """Save user reputation"""
        cfg = config.load_config()
        if 'reputation' not in cfg:
            cfg['reputation'] = {}
        if str(guild_id) not in cfg['reputation']:
            cfg['reputation'][str(guild_id)] = {}
        cfg['reputation'][str(guild_id)][str(user_id)] = data
        config.save_config(cfg)
    
    async def give_rep(self, interaction, target_user, positive=True):
        """Give reputation to a user"""
        if interaction.user.id == target_user.id:
            await interaction.response.send_message("❌ You can't give reputation to yourself!", ephemeral=True)
            return
        
        giver_data = self.get_user_rep(interaction.guild.id, interaction.user.id)
        
        if giver_data['last_gave']:
            last_gave = datetime.fromisoformat(giver_data['last_gave'])
            cooldown = last_gave + timedelta(hours=24)
            
            if datetime.now(timezone.utc) < cooldown:
                time_left = cooldown - datetime.now(timezone.utc)
                hours = int(time_left.total_seconds() // 3600)
                await interaction.response.send_message(
                    f"⏰ You can give reputation again in {hours} hours!", 
                    ephemeral=True
                )
                return
        
        target_data = self.get_user_rep(interaction.guild.id, target_user.id)
        
        change = 1 if positive else -1
        target_data['rep'] += change
        target_data['received_from'].append(str(interaction.user.id))
        
        giver_data['last_gave'] = datetime.now(timezone.utc).isoformat()
        giver_data['given_reps'][str(target_user.id)] = change
        
        self.save_user_rep(interaction.guild.id, target_user.id, target_data)
        self.save_user_rep(interaction.guild.id, interaction.user.id, giver_data)
        
        emoji = "👍" if positive else "👎"
        action = "positive" if positive else "negative"
        
        embed = discord.Embed(
            title=f"{emoji} Reputation {action.capitalize()}",
            description=f"{interaction.user.mention} gave {action} reputation to {target_user.mention}!",
            color=0x00FF00 if positive else 0xFF0000
        )
        embed.add_field(name=f"{target_user.name}'s Reputation", value=f"**{target_data['rep']}** points", inline=False)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Reputation(bot))

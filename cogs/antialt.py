import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone
import config

class AntiAlt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        cfg = config.load_config()
        min_age_days = cfg.get('min_account_age_days', 7)
        
        account_age = datetime.now(timezone.utc) - member.created_at
        age_in_days = account_age.days
        
        if age_in_days < min_age_days:
            try:
                welcome_embed = discord.Embed(
                    title="⚠️ Account Age Warning",
                    description=f"Your account is only {age_in_days} days old. Please be aware that you may have limited permissions until your account ages.",
                    color=0xFF006E
                )
                await member.send(embed=welcome_embed)
            except:
                pass
    
    @commands.command(name='setaltage')
    @commands.has_permissions(administrator=True)
    async def set_alt_age(self, ctx, days: int):
        if days < 0:
            await ctx.send("❌ Days must be a positive number!")
            return
        
        config.update_config('min_account_age_days', days)
        
        embed = discord.Embed(
            title="✅ Anti-Alt Configuration Updated",
            description=f"Minimum account age set to **{days} days**",
            color=0x00F3FF
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AntiAlt(bot))

import discord
from discord.ext import commands
import traceback
import sys
from datetime import datetime, timezone
import aiohttp
import config

class WebhookLogging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        cfg = config.load_config()
        self.webhook_url = cfg.get('webhook_url')
        
    async def send_to_webhook(self, embed):
        if not self.webhook_url:
            return
            
        try:
            async with aiohttp.ClientSession() as session:
                webhook = discord.Webhook.from_url(self.webhook_url, session=session)
                await webhook.send(embed=embed)
        except Exception as e:
            print(f"Failed to send webhook: {e}")
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        embed = discord.Embed(
            title="⚠️ Command Error",
            color=discord.Color.red(),
            timestamp=datetime.now(timezone.utc)
        )
        
        embed.add_field(name="Command", value=f"`{ctx.command}`", inline=True)
        embed.add_field(name="User", value=f"{ctx.author} ({ctx.author.id})", inline=True)
        embed.add_field(name="Channel", value=f"{ctx.channel.mention}", inline=True)
        
        if isinstance(error, commands.MissingRequiredArgument):
            embed.add_field(
                name="Error Type",
                value="Missing Required Argument",
                inline=False
            )
            embed.add_field(
                name="Details",
                value=f"Missing: `{error.param.name}`",
                inline=False
            )
        elif isinstance(error, commands.MissingPermissions):
            embed.add_field(
                name="Error Type",
                value="Missing Permissions",
                inline=False
            )
            embed.add_field(
                name="Details",
                value=f"Required: {', '.join(error.missing_permissions)}",
                inline=False
            )
        elif isinstance(error, commands.CommandNotFound):
            return
        else:
            embed.add_field(
                name="Error Type",
                value=type(error).__name__,
                inline=False
            )
            embed.add_field(
                name="Details",
                value=f"```py\n{str(error)[:1000]}```",
                inline=False
            )
        
        await self.send_to_webhook(embed)
    
    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        embed = discord.Embed(
            title="❌ Bot Error",
            color=discord.Color.dark_red(),
            timestamp=datetime.now(timezone.utc)
        )
        
        embed.add_field(name="Event", value=f"`{event}`", inline=False)
        
        exc_type, exc_value, exc_traceback = sys.exc_info()
        if exc_type:
            embed.add_field(
                name="Error Type",
                value=exc_type.__name__,
                inline=False
            )
            
            tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            tb_text = ''.join(tb_lines)[-1500:]
            
            embed.add_field(
                name="Traceback",
                value=f"```py\n{tb_text}```",
                inline=False
            )
        
        await self.send_to_webhook(embed)
    
    @commands.Cog.listener()
    async def on_ready(self):
        embed = discord.Embed(
            title="✅ Bot Started",
            description=f"Bot is online and ready!",
            color=discord.Color.green(),
            timestamp=datetime.now(timezone.utc)
        )
        
        embed.add_field(name="Bot Name", value=str(self.bot.user), inline=True)
        embed.add_field(name="Bot ID", value=str(self.bot.user.id), inline=True)
        embed.add_field(name="Guilds", value=str(len(self.bot.guilds)), inline=True)
        
        await self.send_to_webhook(embed)
    
    @commands.command(name='setwebhook')
    @commands.has_permissions(administrator=True)
    async def set_webhook(self, ctx, webhook_url: str):
        self.webhook_url = webhook_url
        config.update_config('webhook_url', webhook_url)
        
        embed = discord.Embed(
            title="✅ Webhook Set",
            description="Bot logging webhook has been configured!",
            color=discord.Color.green()
        )
        embed.add_field(
            name="Test Message",
            value="If this appears in your webhook channel, logging is working!",
            inline=False
        )
        
        await self.send_to_webhook(embed)
        await ctx.send("✅ Webhook logging configured! Check your webhook channel.")
    
    @commands.command(name='testwebhook')
    @commands.has_permissions(administrator=True)
    async def test_webhook(self, ctx):
        embed = discord.Embed(
            title="🧪 Test Webhook",
            description="This is a test message from the bot!",
            color=discord.Color.blue(),
            timestamp=datetime.now(timezone.utc)
        )
        
        embed.add_field(name="Tested by", value=str(ctx.author), inline=True)
        embed.add_field(name="Channel", value=ctx.channel.mention, inline=True)
        
        await self.send_to_webhook(embed)
        await ctx.send("✅ Test webhook sent! Check your webhook channel.")
    
    @commands.command(name='loginfo')
    @commands.has_permissions(administrator=True)
    async def log_info(self, ctx, *, message: str):
        embed = discord.Embed(
            title="ℹ️ Info Log",
            description=message,
            color=discord.Color.blue(),
            timestamp=datetime.now(timezone.utc)
        )
        
        embed.add_field(name="Logged by", value=str(ctx.author), inline=True)
        
        await self.send_to_webhook(embed)
        await ctx.send("✅ Info logged to webhook.")

async def setup(bot):
    await bot.add_cog(WebhookLogging(bot))

import discord
from discord.ext import commands
from datetime import datetime, timezone
from translations import get_text

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        app_info = await self.bot.application_info()
        owner = app_info.owner
        
        embed = discord.Embed(
            title="🎉 Bot Invited to New Server!",
            description=f"I've been added to **{guild.name}**",
            color=0x00ffff,
            timestamp=datetime.now(timezone.utc)
        )
        
        embed.add_field(
            name="📊 Server Info",
            value=f"**Name:** {guild.name}\n**ID:** `{guild.id}`\n**Members:** {guild.member_count}",
            inline=False
        )
        
        if guild.owner:
            embed.add_field(
                name="👑 Server Owner",
                value=f"{guild.owner.mention} ({guild.owner})\n**ID:** `{guild.owner.id}`",
                inline=False
            )
        
        embed.add_field(
            name="📅 Server Created",
            value=f"{guild.created_at.strftime('%Y-%m-%d')}",
            inline=True
        )
        
        embed.add_field(
            name="🌍 Total Servers",
            value=f"{len(self.bot.guilds)} servers",
            inline=True
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.set_footer(text=f"Server ID: {guild.id}")
        
        try:
            await owner.send(embed=embed)
        except:
            pass
    
    def is_bot_owner():
        async def predicate(ctx):
            return await ctx.bot.is_owner(ctx.author)
        return commands.check(predicate)
    
    @commands.command(name='servers')
    @is_bot_owner()
    async def servers(self, ctx):
        guild_id = ctx.guild.id if ctx.guild else None
        
        embed = discord.Embed(
            title=get_text(guild_id, 'servers_title'),
            description=get_text(guild_id, 'servers_description', len(self.bot.guilds)),
            color=0x00ffff
        )
        
        server_list = []
        for guild in self.bot.guilds:
            server_list.append(f"**{guild.name}**\n`ID: {guild.id}`")
        
        if server_list:
            chunks = [server_list[i:i+10] for i in range(0, len(server_list), 10)]
            for i, chunk in enumerate(chunks):
                embed.add_field(
                    name=f"Servers {i*10 + 1}-{min((i+1)*10, len(server_list))}",
                    value="\n\n".join(chunk),
                    inline=False
                )
        
        embed.set_footer(text=get_text(guild_id, 'servers_footer', len(self.bot.guilds)))
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        
        await ctx.send(embed=embed)
    
    @servers.error
    async def servers_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            guild_id = ctx.guild.id if ctx.guild else None
            await ctx.send(get_text(guild_id, 'owner_only'))
    
    @commands.command(name='createinvite')
    @is_bot_owner()
    async def create_invite(self, ctx, server_id: int):
        guild_id = ctx.guild.id if ctx.guild else None
        
        guild = self.bot.get_guild(server_id)
        
        if guild is None:
            await ctx.send(get_text(guild_id, 'server_not_found'))
            return
        
        text_channels = [ch for ch in guild.text_channels if ch.permissions_for(guild.me).create_instant_invite]
        
        if not text_channels:
            await ctx.send(get_text(guild_id, 'no_permission_invite', guild.name))
            return
        
        channel = text_channels[0]
        
        try:
            invite = await channel.create_invite(max_age=0, max_uses=0, reason=f"Created by bot owner {ctx.author}")
            
            embed = discord.Embed(
                title=get_text(guild_id, 'invite_created'),
                description=get_text(guild_id, 'invite_created_desc', guild.name),
                color=0x00ffff
            )
            embed.add_field(name=get_text(guild_id, 'invite_link'), value=invite.url, inline=False)
            embed.add_field(name=get_text(guild_id, 'invite_expires'), value=get_text(guild_id, 'invite_never'), inline=True)
            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)
            
            await ctx.send(embed=embed)
        
        except discord.Forbidden:
            await ctx.send(get_text(guild_id, 'no_permission_invite', guild.name))
        except Exception as e:
            await ctx.send(f"❌ Error creating invite: {e}")
    
    @create_invite.error
    async def create_invite_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            guild_id = ctx.guild.id if ctx.guild else None
            await ctx.send(get_text(guild_id, 'owner_only'))

async def setup(bot):
    await bot.add_cog(Admin(bot))

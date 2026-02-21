import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
from datetime import datetime, timezone, timedelta
import random
import config

class GiveawayView(View):
    def __init__(self, giveaway_id, bot):
        super().__init__(timeout=None)
        self.giveaway_id = giveaway_id
        self.bot = bot
        
        cfg = config.load_config()
        giveaway_data = cfg.get('giveaways', {}).get(giveaway_id, {})
        self.participants = set(giveaway_data.get('participants', []))
        
        self.children[0].custom_id = f'giveaway_enter_{giveaway_id}'
    
    @discord.ui.button(label='🎉 Enter Giveaway', style=discord.ButtonStyle.green)
    async def enter_giveaway(self, interaction: discord.Interaction, button: Button):
        user_id = interaction.user.id
        
        cfg = config.load_config()
        
        if user_id in self.participants:
            self.participants.remove(user_id)
            await interaction.response.send_message(
                "❌ You have left the giveaway!",
                ephemeral=True
            )
        else:
            self.participants.add(user_id)
            await interaction.response.send_message(
                "✅ You have entered the giveaway! Good luck!",
                ephemeral=True
            )
        
        if 'giveaways' in cfg and self.giveaway_id in cfg['giveaways']:
            cfg['giveaways'][self.giveaway_id]['participants'] = list(self.participants)
            config.save_config(cfg)
        
        button.label = f"🎉 Enter Giveaway ({len(self.participants)})"
        await interaction.message.edit(view=self)

class Giveaways(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_giveaways = {}
        self.restore_giveaways()
        self.check_giveaways.start()
    
    def restore_giveaways(self):
        cfg = config.load_config()
        giveaways = cfg.get('giveaways', {})
        
        for giveaway_id in giveaways.keys():
            view = GiveawayView(giveaway_id, self.bot)
            self.active_giveaways[giveaway_id] = view
            self.bot.add_view(view)
    
    def cog_unload(self):
        self.check_giveaways.cancel()
    
    @tasks.loop(seconds=30)
    async def check_giveaways(self):
        cfg = config.load_config()
        current_time = datetime.now(timezone.utc).timestamp()
        
        giveaways = cfg.get('giveaways', {})
        
        for giveaway_id, data in list(giveaways.items()):
            if current_time >= data['end_time']:
                try:
                    channel = self.bot.get_channel(int(data['channel_id']))
                    message = await channel.fetch_message(int(data['message_id']))
                    
                    view = self.active_giveaways.get(giveaway_id)
                    
                    if view and len(view.participants) > 0:
                        winners_count = min(data['winners'], len(view.participants))
                        winners = random.sample(list(view.participants), winners_count)
                        
                        winner_mentions = " ".join([f"<@{w}>" for w in winners])
                        
                        embed = discord.Embed(
                            title="🎉 Giveaway Ended!",
                            description=f"**Prize:** {data['prize']}\n\n**Winner(s):** {winner_mentions}",
                            color=discord.Color.gold(),
                            timestamp=datetime.now(timezone.utc)
                        )
                        embed.set_footer(text=f"Hosted by {data['host']}")
                        
                        await message.edit(embed=embed, view=None)
                        await channel.send(f"🎊 Congratulations {winner_mentions}! You won **{data['prize']}**!")
                    else:
                        embed = discord.Embed(
                            title="🎉 Giveaway Ended!",
                            description=f"**Prize:** {data['prize']}\n\n**Winner:** No valid entries!",
                            color=0xFF006E,
                            timestamp=datetime.now(timezone.utc)
                        )
                        embed.set_footer(text=f"Hosted by {data['host']}")
                        await message.edit(embed=embed, view=None)
                    
                    if 'completed_giveaways' not in cfg:
                        cfg['completed_giveaways'] = {}
                    cfg['completed_giveaways'][giveaway_id] = giveaways[giveaway_id]
                    
                    del giveaways[giveaway_id]
                    if giveaway_id in self.active_giveaways:
                        del self.active_giveaways[giveaway_id]
                except:
                    pass
        
        cfg['giveaways'] = giveaways
        config.save_config(cfg)
    
    @check_giveaways.before_loop
    async def before_check_giveaways(self):
        await self.bot.wait_until_ready()
    
    @commands.command(name='giveaway')
    @commands.has_permissions(manage_guild=True)
    async def start_giveaway(self, ctx, duration: str, winners: int, *, prize: str):
        time_units = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
        
        try:
            time_amount = int(duration[:-1])
            time_unit = duration[-1]
        except:
            await ctx.send("❌ Invalid time format! Use: 10s, 5m, 2h, 1d")
            return
        
        if time_unit not in time_units:
            await ctx.send("❌ Invalid time format! Use: 10s, 5m, 2h, 1d")
            return
        
        if winners < 1:
            await ctx.send("❌ There must be at least 1 winner!")
            return
        
        seconds = time_amount * time_units[time_unit]
        end_time = datetime.now(timezone.utc) + timedelta(seconds=seconds)
        
        embed = discord.Embed(
            title="🎉 GIVEAWAY! 🎉",
            description=f"**Prize:** {prize}\n**Winners:** {winners}\n**Ends:** <t:{int(end_time.timestamp())}:R>",
            color=0x8B00FF,
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_footer(text=f"Hosted by {ctx.author}")
        
        giveaway_id = str(int(datetime.now(timezone.utc).timestamp()))
        
        cfg = config.load_config()
        if 'giveaways' not in cfg:
            cfg['giveaways'] = {}
        
        cfg['giveaways'][giveaway_id] = {
            'prize': prize,
            'winners': winners,
            'end_time': end_time.timestamp(),
            'channel_id': str(ctx.channel.id),
            'message_id': '',
            'host': str(ctx.author),
            'participants': []
        }
        config.save_config(cfg)
        
        view = GiveawayView(giveaway_id, self.bot)
        message = await ctx.send(embed=embed, view=view)
        
        self.active_giveaways[giveaway_id] = view
        
        cfg['giveaways'][giveaway_id]['message_id'] = str(message.id)
        config.save_config(cfg)
        
        await ctx.message.delete()
    
    @commands.command(name='reroll')
    @commands.has_permissions(manage_guild=True)
    async def reroll_giveaway(self, ctx, message_id: int):
        try:
            message = await ctx.channel.fetch_message(message_id)
            
            if not message.embeds or "giveaway" not in message.embeds[0].title.lower():
                await ctx.send("❌ That's not a giveaway message!")
                return
            
            cfg = config.load_config()
            giveaway_data = None
            giveaway_id = None
            
            for gid, data in cfg.get('giveaways', {}).items():
                if data.get('message_id') == str(message_id):
                    giveaway_data = data
                    giveaway_id = gid
                    break
            
            if not giveaway_data:
                for gid, data in cfg.get('completed_giveaways', {}).items():
                    if data.get('message_id') == str(message_id):
                        giveaway_data = data
                        giveaway_id = gid
                        break
            
            if not giveaway_data:
                await ctx.send("❌ Giveaway data not found!")
                return
            
            participants = giveaway_data.get('participants', [])
            
            if len(participants) == 0:
                await ctx.send("❌ No participants to reroll!")
                return
            
            new_winner_id = random.choice(participants)
            new_winner = await self.bot.fetch_user(int(new_winner_id))
            
            embed = discord.Embed(
                title="🎉 Giveaway Rerolled!",
                description=f"**Prize:** {giveaway_data['prize']}\n\n**New Winner:** {new_winner.mention}",
                color=discord.Color.gold(),
                timestamp=datetime.now(timezone.utc)
            )
            
            await ctx.send(embed=embed)
            await ctx.send(f"🎊 Congratulations {new_winner.mention}! You won **{giveaway_data['prize']}**!")
        except Exception as e:
            await ctx.send(f"❌ Error rerolling giveaway: {str(e)}")

async def setup(bot):
    await bot.add_cog(Giveaways(bot))

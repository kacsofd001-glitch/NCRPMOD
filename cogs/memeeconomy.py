import discord
from discord.ext import commands, tasks
import config
from datetime import datetime, timezone

class MemeEconomy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.monthly_reset.start()
    
    def cog_unload(self):
        self.monthly_reset.cancel()
    
    def get_meme_config(self, guild_id):
        """Get meme economy settings"""
        cfg = config.load_config()
        memes = cfg.get('meme_economy', {})
        return memes.get(str(guild_id), {
            'enabled': False,
            'submission_channel_id': None,
            'voting_channel_id': None,
            'memes': {},
            'next_id': 1,
            'current_month': datetime.now(timezone.utc).strftime('%Y-%m')
        })
    
    def save_meme_config(self, guild_id, settings):
        """Save meme economy settings"""
        cfg = config.load_config()
        if 'meme_economy' not in cfg:
            cfg['meme_economy'] = {}
        cfg['meme_economy'][str(guild_id)] = settings
        config.save_config(cfg)
    
    async def submit_meme(self, interaction, image_url, caption):
        """Submit a meme for voting"""
        settings = self.get_meme_config(interaction.guild.id)
        
        if not settings['enabled']:
            await interaction.response.send_message("❌ Meme economy is not enabled!", ephemeral=True)
            return
        
        meme_id = settings['next_id']
        settings['next_id'] += 1
        
        meme_data = {
            'author_id': interaction.user.id,
            'image_url': image_url,
            'caption': caption,
            'upvotes': [],
            'downvotes': [],
            'submitted_at': datetime.now(timezone.utc).isoformat(),
            'month': settings['current_month']
        }
        
        settings['memes'][str(meme_id)] = meme_data
        self.save_meme_config(interaction.guild.id, settings)
        
        if settings['voting_channel_id']:
            channel = interaction.guild.get_channel(settings['voting_channel_id'])
            if channel:
                embed = discord.Embed(
                    title=f"🎭 Meme #{meme_id}",
                    description=caption,
                    color=0xFF00FF
                )
                embed.set_image(url=image_url)
                embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
                embed.set_footer(text="Vote with 👍 or 👎")
                
                msg = await channel.send(embed=embed)
                await msg.add_reaction('👍')
                await msg.add_reaction('👎')
        
        await interaction.response.send_message(f"✅ Your meme has been submitted! (ID: #{meme_id})", ephemeral=True)
    
    @tasks.loop(hours=24)
    async def monthly_reset(self):
        """Check for monthly meme competition winner"""
        try:
            current_month = datetime.now(timezone.utc).strftime('%Y-%m')
            
            cfg = config.load_config()
            all_memes = cfg.get('meme_economy', {})
            
            for guild_id, settings in all_memes.items():
                try:
                    if settings['current_month'] != current_month:
                        winner_id, winner_meme = self.get_monthly_winner(settings)
                        
                        if winner_id and settings.get('voting_channel_id'):
                            guild = self.bot.get_guild(int(guild_id))
                            if guild:
                                channel = guild.get_channel(settings['voting_channel_id'])
                                winner = guild.get_member(winner_meme['author_id'])
                                
                                if channel and winner:
                                    try:
                                        embed = discord.Embed(
                                            title="🏆 Meme of the Month Winner!",
                                            description=f"Congratulations to {winner.mention}!",
                                            color=0xFFD700
                                        )
                                        embed.set_image(url=winner_meme['image_url'])
                                        embed.add_field(name="Caption", value=winner_meme['caption'], inline=False)
                                        embed.add_field(name="Votes", value=f"👍 {len(winner_meme['upvotes'])} | 👎 {len(winner_meme['downvotes'])}", inline=False)
                                        
                                        await channel.send(embed=embed)
                                        
                                        economy_cog = self.bot.get_cog('Economy')
                                        if economy_cog:
                                            economy_cog.add_money(int(guild_id), winner_meme['author_id'], 5000)
                                    except Exception as e:
                                        print(f"Error announcing meme winner for guild {guild_id}: {e}")
                        
                        settings['current_month'] = current_month
                        self.save_meme_config(int(guild_id), settings)
                except Exception as e:
                    print(f"Error processing meme economy for guild {guild_id}: {e}")
                    continue
        except Exception as e:
            print(f"Error in monthly_reset loop: {e}")
    
    def get_monthly_winner(self, settings):
        """Get the meme with most upvotes this month"""
        current_month = settings.get('current_month')
        best_score = -999999
        winner_id = None
        winner_meme = None
        
        for meme_id, meme_data in settings.get('memes', {}).items():
            if meme_data.get('month') == current_month:
                score = len(meme_data['upvotes']) - len(meme_data['downvotes'])
                if score > best_score:
                    best_score = score
                    winner_id = meme_id
                    winner_meme = meme_data
        
        return winner_id, winner_meme
    
    @monthly_reset.before_loop
    async def before_monthly_reset(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(MemeEconomy(bot))

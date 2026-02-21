import discord
from discord.ext import commands
import aiohttp
import random
import config
from translations import get_text, get_guild_language
from urllib.parse import quote

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sounds = [
            "🎵 *Ding dong!*",
            "🔔 *Ring ring!*",
            "📯 *Toot toot!*",
            "🎺 *Doot doot!*",
            "🥁 *Ba dum tss!*",
            "🎸 *Strum strum!*",
            "🎹 *Piano notes!*",
            "🎷 *Smooth jazz!*",
            "📢 *Honk honk!*",
            "🔊 *Beep boop!*"
        ]
        
        self.meme_templates_en = [
            ("drake", "Old boring way", "Cool new way"),
            ("buzz", "Memes", "Memes everywhere"),
            ("doge", "Such wow", "Very meme"),
            ("yoda", "Do or do not", "There is no try"),
            ("both", "Why not both?", "Both is good"),
            ("aliens", "I'm not saying it was", "But it was"),
            ("interesting", "That's very", "Interesting"),
            ("disaster", "I see this as", "An absolute win"),
            ("fine", "This is fine", "Everything is fine"),
            ("think", "Modern problems", "Modern solutions"),
        ]
        
        self.meme_templates_hu = [
            ("drake", "Régi unalmas módszer", "Menő új módszer"),
            ("buzz", "Mémek", "Mémek mindenhol"),
            ("doge", "Ilyen hűha", "Nagyon mém"),
            ("yoda", "Tedd vagy ne tedd", "Nincs próba"),
            ("both", "Miért ne mindkettő?", "Mindkettő jó"),
            ("aliens", "Nem azt mondom hogy az volt", "De az volt"),
            ("interesting", "Ez nagyon", "Érdekes"),
            ("disaster", "Ezt úgy látom", "Abszolút győzelem"),
            ("fine", "Ez rendben van", "Minden rendben"),
            ("think", "Modern problémák", "Modern megoldások"),
        ]
    
    @commands.command(name='meme')
    async def random_meme(self, ctx):
        guild_id = ctx.guild.id
        await ctx.trigger_typing()
        
        # Use a more reliable public meme API for random memes
        meme_apis = [
            "https://meme-api.com/gimme",
            "https://meme-api.com/gimme/wholesomememes",
            "https://meme-api.com/gimme/memes"
        ]
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(random.choice(meme_apis), timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        data = await response.json()
                        meme_url = data.get('url')
                        meme_title = data.get('title', get_text(guild_id, 'meme_title'))
                        
                        embed = discord.Embed(
                            title=meme_title,
                            color=discord.Color.random()
                        )
                        embed.set_image(url=meme_url)
                        embed.set_footer(text=f"r/{data.get('subreddit')} | {get_text(guild_id, 'generated_meme')}")
                        
                        await ctx.send(embed=embed)
                        return
                    else:
                        raise Exception("Meme API error")
        except Exception as e:
            # Fallback to local templates if API fails
            lang = get_guild_language(guild_id)
            templates = self.meme_templates_hu if lang == 'hu' else self.meme_templates_en
            template_name, top_text, bottom_text = random.choice(templates)
            
            top_text_encoded = quote(top_text, safe='')
            bottom_text_encoded = quote(bottom_text, safe='')
            
            meme_url = f"https://api.memegen.link/images/{template_name}/{top_text_encoded}/{bottom_text_encoded}.png"
            
            embed = discord.Embed(
                title=get_text(guild_id, 'meme_title'),
                color=discord.Color.random()
            )
            embed.set_image(url=meme_url)
            embed.set_footer(text=get_text(guild_id, 'generated_meme'))
            
            await ctx.send(embed=embed)
    
    
    @commands.command(name='sound')
    async def random_sound(self, ctx):
        sound = random.choice(self.sounds)
        
        embed = discord.Embed(
            title="🔊 Random Sound",
            description=sound,
            color=discord.Color.random()
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='8ball')
    async def eight_ball(self, ctx, *, question: str = ""):
        from translations import get_text
        if not question:
            await ctx.send("❌ Please ask a question!")
            return
        
        responses = get_text(ctx.guild.id, '8ball_responses')
        answer = random.choice(responses)
        
        embed = discord.Embed(
            title=get_text(ctx.guild.id, 'magic_8ball'),
            color=discord.Color.purple()
        )
        embed.add_field(name=get_text(ctx.guild.id, 'question'), value=question, inline=False)
        embed.add_field(name=get_text(ctx.guild.id, 'answer'), value=answer, inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='coinflip')
    async def coin_flip(self, ctx):
        from translations import get_text
        result = random.choice([get_text(ctx.guild.id, 'heads'), get_text(ctx.guild.id, 'tails')])
        emoji = '🪙'
        
        embed = discord.Embed(
            title=get_text(ctx.guild.id, 'coin_flip'),
            description=get_text(ctx.guild.id, 'coin_result', result),
            color=discord.Color.gold()
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='roll')
    async def dice_roll(self, ctx, dice: str = "1d6"):
        try:
            rolls, sides = map(int, dice.split('d'))
            
            if rolls > 100 or sides > 1000:
                await ctx.send("❌ That's too many dice or sides!")
                return
            
            results = [random.randint(1, sides) for _ in range(rolls)]
            total = sum(results)
            
            embed = discord.Embed(
                title="🎲 Dice Roll",
                description=f"Rolling {rolls}d{sides}",
                color=0x8B00FF
            )
            
            if len(results) <= 20:
                embed.add_field(name="Results", value=", ".join(map(str, results)), inline=False)
            
            embed.add_field(name="Total", value=str(total), inline=False)
            
            await ctx.send(embed=embed)
        except:
            await ctx.send("❌ Invalid format! Use: `!roll 2d6` (rolls, d, sides)")

async def setup(bot):
    await bot.add_cog(Fun(bot))

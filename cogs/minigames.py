import discord
from discord.ext import commands
import random
import asyncio

class MiniGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}
        
        self.trivia_questions = {
            'general': [
                {'question': 'What is the capital of France?', 'answer': 'Paris', 'options': ['London', 'Paris', 'Berlin', 'Madrid']},
                {'question': 'What year did World War 2 end?', 'answer': '1945', 'options': ['1943', '1944', '1945', '1946']},
                {'question': 'Who painted the Mona Lisa?', 'answer': 'Leonardo da Vinci', 'options': ['Michelangelo', 'Leonardo da Vinci', 'Raphael', 'Donatello']},
                {'question': 'What is the largest planet in our solar system?', 'answer': 'Jupiter', 'options': ['Mars', 'Saturn', 'Jupiter', 'Neptune']},
                {'question': 'How many continents are there?', 'answer': '7', 'options': ['5', '6', '7', '8']},
            ],
            'gaming': [
                {'question': 'In what year was Minecraft released?', 'answer': '2011', 'options': ['2009', '2010', '2011', '2012']},
                {'question': 'Who created Discord?', 'answer': 'Jason Citron', 'options': ['Jason Citron', 'Elon Musk', 'Mark Zuckerberg', 'Bill Gates']},
                {'question': 'What is the best-selling video game of all time?', 'answer': 'Minecraft', 'options': ['GTA V', 'Minecraft', 'Tetris', 'Wii Sports']},
            ],
            'tech': [
                {'question': 'What does CPU stand for?', 'answer': 'Central Processing Unit', 'options': ['Computer Personal Unit', 'Central Processing Unit', 'Central Processor Utility', 'Computer Processing Unit']},
                {'question': 'Who founded Apple?', 'answer': 'Steve Jobs', 'options': ['Bill Gates', 'Steve Jobs', 'Elon Musk', 'Jeff Bezos']},
                {'question': 'What programming language is Discord built with?', 'answer': 'Python', 'options': ['Java', 'JavaScript', 'Python', 'C++']},
            ]
        }
    
    async def play_trivia(self, interaction, category='general'):
        """Start a trivia game"""
        questions = self.trivia_questions.get(category, self.trivia_questions['general'])
        question_data = random.choice(questions)
        
        embed = discord.Embed(
            title="🎯 Trivia Time!",
            description=question_data['question'],
            color=0x00F3FF
        )
        
        options = question_data['options'].copy()
        random.shuffle(options)
        
        for i, option in enumerate(options):
            embed.add_field(name=f"Option {i+1}", value=option, inline=True)
        
        embed.set_footer(text="You have 15 seconds to answer!")
        
        view = TriviaView(question_data['answer'], options, interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view)
    
    async def play_blackjack(self, interaction, bet=100):
        """Start a blackjack game"""
        deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 4
        random.shuffle(deck)
        
        player_hand = [deck.pop(), deck.pop()]
        dealer_hand = [deck.pop(), deck.pop()]
        
        embed = discord.Embed(
            title="🃏 Blackjack",
            description=f"Bet: ${bet}",
            color=0xFFD700
        )
        
        player_total = sum(player_hand)
        embed.add_field(name="Your Hand", value=f"{player_hand} (Total: {player_total})", inline=False)
        embed.add_field(name="Dealer Hand", value=f"[{dealer_hand[0]}, ?]", inline=False)
        
        if player_total == 21:
            embed.add_field(name="Result", value="🎉 BLACKJACK! You win!", inline=False)
            await interaction.response.send_message(embed=embed)
            return
        
        view = BlackjackView(player_hand, dealer_hand, deck, bet, interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view)
    
    async def play_slots(self, interaction, bet=50):
        """Play slots machine"""
        symbols = ['🍒', '🍋', '🍊', '🍇', '💎', '7️⃣']
        
        result = [random.choice(symbols) for _ in range(3)]
        
        embed = discord.Embed(
            title="🎰 Slot Machine",
            description=f"Bet: ${bet}\n\n{'  '.join(result)}",
            color=0xFF00FF
        )
        
        if result[0] == result[1] == result[2]:
            if result[0] == '💎':
                winnings = bet * 10
                embed.add_field(name="Result", value=f"💎 JACKPOT! Won ${winnings}!", inline=False)
            elif result[0] == '7️⃣':
                winnings = bet * 7
                embed.add_field(name="Result", value=f"🎰 TRIPLE 7s! Won ${winnings}!", inline=False)
            else:
                winnings = bet * 3
                embed.add_field(name="Result", value=f"✨ Triple match! Won ${winnings}!", inline=False)
        elif result[0] == result[1] or result[1] == result[2]:
            winnings = bet
            embed.add_field(name="Result", value=f"😊 Double match! Won ${winnings}!", inline=False)
        else:
            embed.add_field(name="Result", value=f"😢 No match. Lost ${bet}", inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    async def play_coinflip(self, interaction, bet=100, choice='heads'):
        """Flip a coin"""
        result = random.choice(['heads', 'tails'])
        
        embed = discord.Embed(
            title="🪙 Coinflip",
            description=f"Bet: ${bet}\nYour choice: {choice.capitalize()}",
            color=0xFFD700
        )
        
        coin_emoji = '🟡' if result == 'heads' else '⚪'
        embed.add_field(name="Result", value=f"{coin_emoji} {result.capitalize()}", inline=False)
        
        if result == choice.lower():
            embed.add_field(name="Outcome", value=f"✅ You won ${bet}!", inline=False)
            embed.color = 0x00FF00
        else:
            embed.add_field(name="Outcome", value=f"❌ You lost ${bet}", inline=False)
            embed.color = 0xFF0000
        
        await interaction.response.send_message(embed=embed)
    
    async def play_scramble(self, interaction):
        """Word scramble game"""
        words = [
            'python', 'discord', 'gaming', 'computer', 'keyboard', 'monitor',
            'internet', 'software', 'developer', 'programmer', 'algorithm'
        ]
        
        word = random.choice(words)
        scrambled = ''.join(random.sample(word, len(word)))
        
        while scrambled == word:
            scrambled = ''.join(random.sample(word, len(word)))
        
        embed = discord.Embed(
            title="🔤 Word Scramble",
            description=f"Unscramble this word:\n\n**{scrambled.upper()}**",
            color=0x00F3FF
        )
        embed.set_footer(text="You have 30 seconds! Type your answer below.")
        
        await interaction.response.send_message(embed=embed)
        
        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel
        
        try:
            msg = await self.bot.wait_for('message', timeout=30.0, check=check)
            
            if msg.content.lower() == word:
                await msg.reply("✅ Correct! Great job! 🎉")
            else:
                await msg.reply(f"❌ Wrong! The correct answer was: **{word}**")
        except asyncio.TimeoutError:
            await interaction.followup.send(f"⏰ Time's up! The answer was: **{word}**")

class TriviaView(discord.ui.View):
    def __init__(self, correct_answer, options, user_id):
        super().__init__(timeout=15)
        self.correct_answer = correct_answer
        self.user_id = user_id
        self.answered = False
        
        for i, option in enumerate(options):
            button = discord.ui.Button(label=option, style=discord.ButtonStyle.primary, custom_id=str(i))
            button.callback = self.create_callback(option)
            self.add_item(button)
    
    def create_callback(self, option):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("This isn't your game!", ephemeral=True)
                return
            
            if self.answered:
                return
            
            self.answered = True
            
            if option == self.correct_answer:
                await interaction.response.send_message(f"✅ Correct! The answer was **{self.correct_answer}**! 🎉")
            else:
                await interaction.response.send_message(f"❌ Wrong! The correct answer was **{self.correct_answer}**")
            
            self.stop()
        
        return callback

class BlackjackView(discord.ui.View):
    def __init__(self, player_hand, dealer_hand, deck, bet, user_id):
        super().__init__(timeout=60)
        self.player_hand = player_hand
        self.dealer_hand = dealer_hand
        self.deck = deck
        self.bet = bet
        self.user_id = user_id
    
    @discord.ui.button(label="Hit", style=discord.ButtonStyle.green)
    async def hit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your game!", ephemeral=True)
            return
        
        self.player_hand.append(self.deck.pop())
        player_total = sum(self.player_hand)
        
        if player_total > 21:
            embed = discord.Embed(title="🃏 Blackjack", description=f"Bet: ${self.bet}", color=0xFF0000)
            embed.add_field(name="Your Hand", value=f"{self.player_hand} (Total: {player_total})", inline=False)
            embed.add_field(name="Result", value="💥 BUST! You lose!", inline=False)
            await interaction.response.edit_message(embed=embed, view=None)
            self.stop()
        else:
            embed = discord.Embed(title="🃏 Blackjack", description=f"Bet: ${self.bet}", color=0xFFD700)
            embed.add_field(name="Your Hand", value=f"{self.player_hand} (Total: {player_total})", inline=False)
            embed.add_field(name="Dealer Hand", value=f"[{self.dealer_hand[0]}, ?]", inline=False)
            await interaction.response.edit_message(embed=embed)
    
    @discord.ui.button(label="Stand", style=discord.ButtonStyle.red)
    async def stand_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your game!", ephemeral=True)
            return
        
        player_total = sum(self.player_hand)
        dealer_total = sum(self.dealer_hand)
        
        while dealer_total < 17:
            self.dealer_hand.append(self.deck.pop())
            dealer_total = sum(self.dealer_hand)
        
        embed = discord.Embed(title="🃏 Blackjack", description=f"Bet: ${self.bet}", color=0xFFD700)
        embed.add_field(name="Your Hand", value=f"{self.player_hand} (Total: {player_total})", inline=False)
        embed.add_field(name="Dealer Hand", value=f"{self.dealer_hand} (Total: {dealer_total})", inline=False)
        
        if dealer_total > 21:
            embed.add_field(name="Result", value=f"🎉 Dealer bust! You win ${self.bet * 2}!", inline=False)
            embed.color = 0x00FF00
        elif player_total > dealer_total:
            embed.add_field(name="Result", value=f"🎉 You win ${self.bet * 2}!", inline=False)
            embed.color = 0x00FF00
        elif player_total < dealer_total:
            embed.add_field(name="Result", value=f"😢 You lose ${self.bet}!", inline=False)
            embed.color = 0xFF0000
        else:
            embed.add_field(name="Result", value="🤝 Push! Bet returned.", inline=False)
        
        await interaction.response.edit_message(embed=embed, view=None)
        self.stop()

async def setup(bot):
    await bot.add_cog(MiniGames(bot))

import discord
from discord.ext import commands
from discord.ui import Button, View
import random

class RPSView(View):
    def __init__(self, ctx):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.value = None
    
    @discord.ui.button(label='🪨 Rock', style=discord.ButtonStyle.primary)
    async def rock(self, interaction: discord.Interaction, button: Button):
        await self.process_choice(interaction, 'rock')
    
    @discord.ui.button(label='📄 Paper', style=discord.ButtonStyle.primary)
    async def paper(self, interaction: discord.Interaction, button: Button):
        await self.process_choice(interaction, 'paper')
    
    @discord.ui.button(label='✂️ Scissors', style=discord.ButtonStyle.primary)
    async def scissors(self, interaction: discord.Interaction, button: Button):
        await self.process_choice(interaction, 'scissors')
    
    async def process_choice(self, interaction: discord.Interaction, choice):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("❌ This is not your game!", ephemeral=True)
            return
        
        bot_choice = random.choice(['rock', 'paper', 'scissors'])
        
        emojis = {'rock': '🪨', 'paper': '📄', 'scissors': '✂️'}
        
        if choice == bot_choice:
            result = "It's a tie!"
            color = discord.Color.gold()
        elif (choice == 'rock' and bot_choice == 'scissors') or \
             (choice == 'paper' and bot_choice == 'rock') or \
             (choice == 'scissors' and bot_choice == 'paper'):
            result = "You win! 🎉"
            color = 0x00F3FF
        else:
            result = "You lose! 😢"
            color = 0xFF006E
        
        embed = discord.Embed(
            title="🎮 Rock Paper Scissors",
            description=f"**Your choice:** {emojis[choice]} {choice.title()}\n**My choice:** {emojis[bot_choice]} {bot_choice.title()}\n\n**Result:** {result}",
            color=color
        )
        
        await interaction.response.edit_message(embed=embed, view=None)
        self.stop()

class TicTacToeButton(Button):
    def __init__(self, x: int, y: int):
        super().__init__(style=discord.ButtonStyle.secondary, label='\u200b', row=y)
        self.x = x
        self.y = y
    
    async def callback(self, interaction: discord.Interaction):
        view: TicTacToeView = self.view
        
        if interaction.user.id != view.current_player.id:
            await interaction.response.send_message("❌ It's not your turn!", ephemeral=True)
            return
        
        if view.board[self.y][self.x] != 0:
            await interaction.response.send_message("❌ This position is already taken!", ephemeral=True)
            return
        
        view.board[self.y][self.x] = view.current_marker
        self.style = discord.ButtonStyle.danger if view.current_marker == 1 else discord.ButtonStyle.success
        self.label = 'X' if view.current_marker == 1 else 'O'
        self.disabled = True
        
        winner = view.check_winner()
        
        if winner:
            for child in view.children:
                child.disabled = True
            
            if winner == 3:
                embed = discord.Embed(
                    title="🎮 Tic Tac Toe - Tie!",
                    description="The game ended in a tie!",
                    color=discord.Color.gold()
                )
            else:
                winner_player = view.player1 if winner == 1 else view.player2
                embed = discord.Embed(
                    title="🎮 Tic Tac Toe - Winner!",
                    description=f"{winner_player.mention} wins! 🎉",
                    color=0x00F3FF
                )
            
            await interaction.response.edit_message(embed=embed, view=view)
            view.stop()
        else:
            view.current_marker = 2 if view.current_marker == 1 else 1
            view.current_player = view.player2 if view.current_marker == 2 else view.player1
            
            embed = discord.Embed(
                title="🎮 Tic Tac Toe",
                description=f"**Current turn:** {view.current_player.mention} ({'X' if view.current_marker == 1 else 'O'})",
                color=0x8B00FF
            )
            embed.add_field(name="Players", value=f"❌ {view.player1.mention}\n⭕ {view.player2.mention}")
            
            await interaction.response.edit_message(embed=embed, view=view)

class TicTacToeView(View):
    def __init__(self, player1, player2):
        super().__init__(timeout=300)
        self.player1 = player1
        self.player2 = player2
        self.current_player = player1
        self.current_marker = 1
        self.board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        
        for y in range(3):
            for x in range(3):
                self.add_item(TicTacToeButton(x, y))
    
    def check_winner(self):
        for row in self.board:
            if row[0] == row[1] == row[2] != 0:
                return row[0]
        
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != 0:
                return self.board[0][col]
        
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != 0:
            return self.board[0][0]
        
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != 0:
            return self.board[0][2]
        
        if all(self.board[y][x] != 0 for y in range(3) for x in range(3)):
            return 3
        
        return None

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Expose View classes for access from slash_commands
        self.RPSView = RPSView
        self.TicTacToeView = TicTacToeView
    
    @commands.command(name='rps')
    async def rock_paper_scissors(self, ctx):
        embed = discord.Embed(
            title="🎮 Rock Paper Scissors",
            description="Choose your move!",
            color=0x8B00FF
        )
        
        view = RPSView(ctx)
        await ctx.send(embed=embed, view=view)
    
    @commands.command(name='tictactoe')
    async def tic_tac_toe(self, ctx, opponent: discord.Member):
        if opponent.bot:
            await ctx.send("❌ You cannot play against a bot!")
            return
        
        if opponent.id == ctx.author.id:
            await ctx.send("❌ You cannot play against yourself!")
            return
        
        embed = discord.Embed(
            title="🎮 Tic Tac Toe",
            description=f"**Current turn:** {ctx.author.mention} (X)",
            color=0x8B00FF
        )
        embed.add_field(name="Players", value=f"❌ {ctx.author.mention}\n⭕ {opponent.mention}")
        
        view = TicTacToeView(ctx.author, opponent)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Games(bot))

import discord
from discord.ext import commands

class ConnectFour(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}
    
    async def start_game(self, interaction, opponent):
        """Start a Connect Four game"""
        if interaction.user.id == opponent.id:
            await interaction.response.send_message("❌ You can't play against yourself!", ephemeral=True)
            return
        
        game = ConnectFourGame(interaction.user, opponent)
        game_id = f"{interaction.channel.id}_{interaction.user.id}_{opponent.id}"
        self.active_games[game_id] = game
        
        embed = game.get_board_embed()
        view = ConnectFourView(game, game_id, self)
        
        await interaction.response.send_message(
            f"{interaction.user.mention} vs {opponent.mention}\n{game.current_player.mention}'s turn!",
            embed=embed,
            view=view
        )

class ConnectFourGame:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.current_player = player1
        self.board = [[0 for _ in range(7)] for _ in range(6)]
        self.winner = None
        self.moves = 0
    
    def make_move(self, col):
        """Drop a piece in the specified column"""
        for row in range(5, -1, -1):
            if self.board[row][col] == 0:
                player_num = 1 if self.current_player == self.player1 else 2
                self.board[row][col] = player_num
                self.moves += 1
                
                if self.check_win(row, col, player_num):
                    self.winner = self.current_player
                
                self.current_player = self.player2 if self.current_player == self.player1 else self.player1
                return True
        return False
    
    def check_win(self, row, col, player):
        """Check if the last move resulted in a win"""
        directions = [(0,1), (1,0), (1,1), (1,-1)]
        
        for dr, dc in directions:
            count = 1
            
            for d in [1, -1]:
                r, c = row + dr * d, col + dc * d
                while 0 <= r < 6 and 0 <= c < 7 and self.board[r][c] == player:
                    count += 1
                    r += dr * d
                    c += dc * d
            
            if count >= 4:
                return True
        
        return False
    
    def get_board_embed(self):
        """Create an embed displaying the board"""
        board_str = ""
        for row in self.board:
            row_str = ""
            for cell in row:
                if cell == 0:
                    row_str += "⚪"
                elif cell == 1:
                    row_str += "🔴"
                else:
                    row_str += "🟡"
            board_str += row_str + "\n"
        
        board_str += "1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣"
        
        embed = discord.Embed(
            title="🎮 Connect Four",
            description=board_str,
            color=0x00F3FF
        )
        
        if self.winner:
            embed.add_field(name="Winner", value=f"🎉 {self.winner.mention} wins!", inline=False)
        elif self.moves >= 42:
            embed.add_field(name="Result", value="🤝 It's a draw!", inline=False)
        else:
            embed.add_field(name="Turn", value=f"{self.current_player.mention}", inline=False)
        
        return embed

class ConnectFourView(discord.ui.View):
    def __init__(self, game, game_id, cog):
        super().__init__(timeout=300)
        self.game = game
        self.game_id = game_id
        self.cog = cog
        
        for i in range(7):
            button = discord.ui.Button(label=str(i+1), style=discord.ButtonStyle.primary, custom_id=str(i))
            button.callback = self.create_callback(i)
            self.add_item(button)
    
    def create_callback(self, col):
        async def callback(interaction: discord.Interaction):
            if interaction.user != self.game.current_player:
                await interaction.response.send_message("It's not your turn!", ephemeral=True)
                return
            
            if not self.game.make_move(col):
                await interaction.response.send_message("That column is full!", ephemeral=True)
                return
            
            embed = self.game.get_board_embed()
            
            if self.game.winner or self.game.moves >= 42:
                await interaction.response.edit_message(embed=embed, view=None)
                if self.game_id in self.cog.active_games:
                    del self.cog.active_games[self.game_id]
                self.stop()
            else:
                await interaction.response.edit_message(
                    content=f"{self.game.player1.mention} vs {self.game.player2.mention}\n{self.game.current_player.mention}'s turn!",
                    embed=embed
                )
        
        return callback

async def setup(bot):
    await bot.add_cog(ConnectFour(bot))

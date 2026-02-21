import discord
from discord.ext import commands

class SetupWizard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def start_setup(self, interaction):
        """Start interactive setup wizard"""
        from translations import get_text
        guild_id = interaction.guild.id
        embed = discord.Embed(
            title="🧙 SHADOW-MOD " + get_text(guild_id, 'help_engagement'),
            description=get_text(guild_id, 'help_description'),
            color=0x00F3FF
        )
        
        embed.add_field(
            name=get_text(guild_id, 'help_info'),
            value=get_text(guild_id, 'help_info_desc'),
            inline=False
        )
        
        view = SetupWizardView(self.bot, guild_id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class SetupWizardView(discord.ui.View):
    def __init__(self, bot, guild_id):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild_id = guild_id
    
    @discord.ui.button(label="🔧 Basic Setup", style=discord.ButtonStyle.primary)
    async def basic_setup(self, interaction: discord.Interaction, button: discord.ui.Button):
        from translations import get_text
        embed = discord.Embed(
            title="🔧 " + get_text(self.guild_id, 'help_config'),
            description=get_text(self.guild_id, 'help_config_desc'),
            color=0x00F3FF
        )
        
        await interaction.response.edit_message(embed=embed)
        
        embed.add_field(
            name="Step 1: Create Channels",
            value=(
                "Create these channels:\n"
                "• `#logs` - For moderation logs\n"
                "• `#welcome` - For welcome messages\n"
                "• `#suggestions` - For community suggestions"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Step 2: Run Commands",
            value=(
                "After creating channels, run:\n"
                "`/setlog #logs`\n"
                "`/setwelcome #welcome`\n"
                "`/setupsuggestions #suggestions`"
            ),
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed)
    
    @discord.ui.button(label="💰 Economy Setup", style=discord.ButtonStyle.success)
    async def economy_setup(self, interaction: discord.Interaction, button: discord.ui.Button):
        from translations import get_text
        embed = discord.Embed(
            title="💰 " + get_text(self.guild_id, 'cat_economy'),
            description=get_text(self.guild_id, 'help_economy_desc') if 'help_economy_desc' in TRANSLATIONS['en'] else "Economy setup",
            color=0xFFD700
        )
        
        await interaction.response.edit_message(embed=embed)
        
        embed.add_field(
            name="Available Commands",
            value=(
                "`/balance` - Check balance\n"
                "`/daily` - Claim daily reward\n"
                "`/work` - Work for money\n"
                "`/blackjack <bet>` - Play blackjack\n"
                "`/slots <bet>` - Play slots\n"
                "`/coinflip <bet> <choice>` - Flip a coin"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Tips",
            value="Users can start earning money right away! No setup needed.",
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed)
    
    @discord.ui.button(label="🎮 Games Setup", style=discord.ButtonStyle.primary)
    async def games_setup(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🎮 Mini-Games Setup",
            description="All games are ready to play!",
            color=0xFF00FF
        )
        
        embed.add_field(
            name="Available Games",
            value=(
                "`/trivia` - Trivia questions\n"
                "`/blackjack` - Card game\n"
                "`/slots` - Slot machine\n"
                "`/coinflip` - Coin flip\n"
                "`/scramble` - Word scramble\n"
                "`/connectfour @user` - Connect Four\n"
                "`/rps` - Rock Paper Scissors"
            ),
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed)
    
    @discord.ui.button(label="📊 Advanced Features", style=discord.ButtonStyle.secondary)
    async def advanced_setup(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="📊 Advanced Features Setup",
            description="Configure advanced systems",
            color=0x8B00FF
        )
        
        embed.add_field(
            name="ModMail System",
            value=(
                "1. Create a category: `ModMail`\n"
                "2. Run: `/setupmodmail <category>`\n"
                "Users can now DM the bot to create tickets!"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Starboard",
            value=(
                "1. Create channel: `#starboard`\n"
                "2. Run: `/starboard enable #starboard 5`\n"
                "Messages with 5+ ⭐ will be posted!"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Counting Game",
            value=(
                "1. Create channel: `#counting`\n"
                "2. Run: `/counting #counting`\n"
                "Users count sequentially!"
            ),
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed)

async def setup(bot):
    await bot.add_cog(SetupWizard(bot))

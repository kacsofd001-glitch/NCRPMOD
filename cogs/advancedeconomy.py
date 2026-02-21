import discord
from discord.ext import commands
import config
import random
from datetime import datetime, timedelta, timezone

class AdvancedEconomy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shop_items = {
            'vip_role': {'name': 'VIP Role', 'price': 10000, 'emoji': '👑'},
            'color_role': {'name': 'Custom Color Role', 'price': 5000, 'emoji': '🎨'},
            'xp_boost': {'name': 'XP Boost (24h)', 'price': 2000, 'emoji': '⚡'},
            'lottery_ticket': {'name': 'Lottery Ticket', 'price': 100, 'emoji': '🎫'},
            'shield': {'name': 'Robbery Shield (24h)', 'price': 3000, 'emoji': '🛡️'},
        }
    
    async def rob_user(self, interaction, target):
        """Attempt to rob another user"""
        if interaction.user.id == target.id:
            await interaction.response.send_message("❌ You can't rob yourself!", ephemeral=True)
            return
        
        if target.bot:
            await interaction.response.send_message("❌ You can't rob bots!", ephemeral=True)
            return
        
        economy_cog = self.bot.get_cog('Economy')
        if not economy_cog:
            await interaction.response.send_message("❌ Economy system not loaded!", ephemeral=True)
            return
        
        robber_data = economy_cog.get_user_balance(interaction.guild.id, interaction.user.id)
        target_data = economy_cog.get_user_balance(interaction.guild.id, target.id)
        
        if robber_data.get('last_rob'):
            last_rob = datetime.fromisoformat(robber_data['last_rob'])
            cooldown = last_rob + timedelta(hours=12)
            
            if datetime.now(timezone.utc) < cooldown:
                time_left = cooldown - datetime.now(timezone.utc)
                hours = int(time_left.total_seconds() // 3600)
                await interaction.response.send_message(
                    f"⏰ You can rob again in {hours} hours!", 
                    ephemeral=True
                )
                return
        
        if target_data['balance'] < 500:
            await interaction.response.send_message(
                f"❌ {target.mention} doesn't have enough money to rob!", 
                ephemeral=True
            )
            return
        
        if 'shield' in target_data.get('inventory', []):
            await interaction.response.send_message(
                f"🛡️ {target.mention} has a robbery shield active!", 
                ephemeral=True
            )
            return
        
        success_rate = random.randint(1, 100)
        
        if success_rate <= 50:
            stolen_amount = int(target_data['balance'] * random.uniform(0.1, 0.3))
            
            target_data['balance'] -= stolen_amount
            robber_data['balance'] += stolen_amount
            robber_data['last_rob'] = datetime.now(timezone.utc).isoformat()
            
            economy_cog.save_user_balance(interaction.guild.id, target.id, target_data)
            economy_cog.save_user_balance(interaction.guild.id, interaction.user.id, robber_data)
            
            embed = discord.Embed(
                title="💰 Robbery Successful!",
                description=f"{interaction.user.mention} robbed ${stolen_amount:,} from {target.mention}!",
                color=0x00FF00
            )
            await interaction.response.send_message(embed=embed)
        else:
            fine = int(robber_data['balance'] * 0.2)
            robber_data['balance'] -= fine
            robber_data['last_rob'] = datetime.now(timezone.utc).isoformat()
            
            economy_cog.save_user_balance(interaction.guild.id, interaction.user.id, robber_data)
            
            embed = discord.Embed(
                title="🚨 Robbery Failed!",
                description=f"{interaction.user.mention} was caught! Fine: ${fine:,}",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed)
    
    async def show_shop(self, interaction):
        """Display the item shop"""
        embed = discord.Embed(
            title="🏪 Item Shop",
            description="Purchase items with your currency!",
            color=0xFFD700
        )
        
        for item_id, item in self.shop_items.items():
            embed.add_field(
                name=f"{item['emoji']} {item['name']}",
                value=f"Price: ${item['price']:,}\nID: `{item_id}`",
                inline=True
            )
        
        embed.set_footer(text="Use /buy <item_id> to purchase")
        
        await interaction.response.send_message(embed=embed)
    
    async def buy_item(self, interaction, item_id):
        """Purchase an item from the shop"""
        if item_id not in self.shop_items:
            await interaction.response.send_message("❌ Invalid item!", ephemeral=True)
            return
        
        economy_cog = self.bot.get_cog('Economy')
        if not economy_cog:
            await interaction.response.send_message("❌ Economy system not loaded!", ephemeral=True)
            return
        
        item = self.shop_items[item_id]
        user_data = economy_cog.get_user_balance(interaction.guild.id, interaction.user.id)
        
        if user_data['balance'] < item['price']:
            await interaction.response.send_message(
                f"❌ Not enough money! You need ${item['price']:,}",
                ephemeral=True
            )
            return
        
        user_data['balance'] -= item['price']
        
        if 'inventory' not in user_data:
            user_data['inventory'] = []
        user_data['inventory'].append(item_id)
        
        economy_cog.save_user_balance(interaction.guild.id, interaction.user.id, user_data)
        
        embed = discord.Embed(
            title="✅ Purchase Successful!",
            description=f"You bought **{item['emoji']} {item['name']}** for ${item['price']:,}!",
            color=0x00FF00
        )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(AdvancedEconomy(bot))

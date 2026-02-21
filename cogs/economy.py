import discord
from discord.ext import commands
import config
from datetime import datetime, timedelta, timezone
import random

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def get_user_balance(self, guild_id, user_id):
        """Get user's economy data"""
        cfg = config.load_config()
        economy = cfg.get('economy', {})
        guild_data = economy.get(str(guild_id), {})
        return guild_data.get(str(user_id), {
            'balance': 0,
            'bank': 0,
            'inventory': [],
            'last_daily': None,
            'last_work': None
        })
    
    def save_user_balance(self, guild_id, user_id, data):
        """Save user's economy data"""
        cfg = config.load_config()
        if 'economy' not in cfg:
            cfg['economy'] = {}
        if str(guild_id) not in cfg['economy']:
            cfg['economy'][str(guild_id)] = {}
        cfg['economy'][str(guild_id)][str(user_id)] = data
        config.save_config(cfg)
    
    def get_shop_items(self, guild_id):
        """Get server shop items"""
        cfg = config.load_config()
        shops = cfg.get('shops', {})
        return shops.get(str(guild_id), {
            '1': {'name': 'VIP Role', 'price': 10000, 'type': 'role', 'role_id': None},
            '2': {'name': 'Color Role', 'price': 5000, 'type': 'role', 'role_id': None},
            '3': {'name': 'Boost', 'price': 2000, 'type': 'item', 'description': '2x XP for 1 hour'}
        })
    
    def add_money(self, guild_id, user_id, amount):
        """Add money to user's wallet"""
        data = self.get_user_balance(guild_id, user_id)
        data['balance'] += amount
        self.save_user_balance(guild_id, user_id, data)
        return data['balance']
    
    def remove_money(self, guild_id, user_id, amount):
        """Remove money from user's wallet"""
        data = self.get_user_balance(guild_id, user_id)
        if data['balance'] < amount:
            return None
        data['balance'] -= amount
        self.save_user_balance(guild_id, user_id, data)
        return data['balance']

async def setup(bot):
    await bot.add_cog(Economy(bot))

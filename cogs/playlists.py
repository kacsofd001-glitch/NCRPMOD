import discord
from discord.ext import commands
import config

class Playlists(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def get_user_playlists(self, user_id):
        """Get user's playlists"""
        cfg = config.load_config()
        playlists = cfg.get('playlists', {})
        return playlists.get(str(user_id), {})
    
    def save_playlist(self, user_id, name, songs):
        """Save user playlist"""
        cfg = config.load_config()
        if 'playlists' not in cfg:
            cfg['playlists'] = {}
        if str(user_id) not in cfg['playlists']:
            cfg['playlists'][str(user_id)] = {}
        
        cfg['playlists'][str(user_id)][name] = {
            'songs': songs,
            'created_at': discord.utils.utcnow().isoformat()
        }
        config.save_config(cfg)
    
    def delete_playlist(self, user_id, name):
        """Delete user playlist"""
        cfg = config.load_config()
        playlists = cfg.get('playlists', {})
        
        if str(user_id) in playlists and name in playlists[str(user_id)]:
            del playlists[str(user_id)][name]
            config.save_config(cfg)
            return True
        return False
    
    def add_to_playlist(self, user_id, playlist_name, song):
        """Add song to playlist"""
        cfg = config.load_config()
        if 'playlists' not in cfg:
            cfg['playlists'] = {}
        if str(user_id) not in cfg['playlists']:
            cfg['playlists'][str(user_id)] = {}
        if playlist_name not in cfg['playlists'][str(user_id)]:
            cfg['playlists'][str(user_id)][playlist_name] = {'songs': []}
        
        cfg['playlists'][str(user_id)][playlist_name]['songs'].append(song)
        config.save_config(cfg)

async def setup(bot):
    await bot.add_cog(Playlists(bot))

from flask import Flask, render_template, jsonify, redirect, request, session
from flask_cors import CORS
from datetime import datetime, timezone
import json
import os
import threading
import time
import sys
import requests
import secrets
from functools import wraps
from urllib.parse import quote
import sqlite3

# Kényszerített azonnali naplózás a Render logokhoz
os.environ['PYTHONUNBUFFERED'] = '1'

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(32))
CORS(app)

# --- ADATBÁZIS MODUL IMPORTÁLÁSA ---
try:
    from database import (
        init_db, get_guild_settings, update_guild_settings,
        save_user_session, get_user_session, delete_user_session,
        cache_user_guilds, get_user_admin_guilds, guild_exists_in_cache
    )
    init_db()
except Exception as e:
    print(f"⚠️ Database import error: {e}", flush=True)

# Discord OAuth2 konfiguráció
DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
DISCORD_REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI', 'https://shadowmod.onrender.com/auth/discord/callback')
DISCORD_API_BASE = 'https://discord.com/api'

OAUTH_CONFIGURED = bool(DISCORD_CLIENT_ID and DISCORD_CLIENT_SECRET)

# OAuth konfiguráció ellenőrzése a logban
if not OAUTH_CONFIGURED:
    print("\n⚠️ WARNING: Discord OAuth2 is not configured!", flush=True)
else:
    print("\n✅ Discord OAuth2 is configured!", flush=True)

STATS_FILE = 'bot_stats.json'

# --- SEGÉDFÜGGVÉNYEK ---

def login_required(f):
    """Dekorátor a bejelentkezés ellenőrzéséhez"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return redirect('/auth/discord')
        return f(*args, **kwargs)
    return decorated_function

def get_discord_user_info(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(f'{DISCORD_API_BASE}/v10/users/@me', headers=headers)
    return response.json() if response.status_code == 200 else None

def get_discord_user_guilds(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(f'{DISCORD_API_BASE}/v10/users/@me/guilds', headers=headers)
    return response.json() if response.status_code == 200 else []

def get_bot_stats():
    """Bot statisztikák betöltése fájlból"""
    try:
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r') as f:
                stats = json.load(f)
                stats['start_time'] = datetime.fromisoformat(stats['start_time'])
                return stats
    except:
        pass
    return {
        'start_time': datetime.now(timezone.utc),
        'guilds': 0, 'users': 0, 'channels': 0, 'status': 'initializing'
    }

# --- WEB OLDALAK (ROUTES) ---

@app.route('/')
def index():
    user_id = session.get('user_id')
    response = app.make_response(render_template('index_public.html',
                         user_id=user_id,
                         username=session.get('username'),
                         avatar_url=session.get('avatar_url')))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.route('/auth/discord')
def auth_discord():
    if not OAUTH_CONFIGURED:
        return render_template('oauth_error.html', error_type='not_configured'), 503
    state = secrets.token_urlsafe(32)
    session['oauth_state'] = state
    auth_url = (
        f'https://discord.com/api/oauth2/authorize?'
        f'client_id={DISCORD_CLIENT_ID}&'
        f'redirect_uri={quote(DISCORD_REDIRECT_URI)}&'
        f'response_type=code&'
        f'scope=identify%20guilds&'
        f'state={state}'
    )
    return redirect(auth_url)

@app.route('/auth/discord/callback')
def auth_callback():
    code = request.args.get('code')
    state = request.args.get('state')
    if state != session.get('oauth_state'): return 'Invalid state', 403
    if not code: return 'No authorization code', 400

    data = {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': DISCORD_REDIRECT_URI,
        'scope': 'identify guilds'
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(f'{DISCORD_API_BASE}/v10/oauth2/token', data=data, headers=headers)
    
    if response.status_code != 200: return 'Failed to authenticate', 401
    
    token_data = response.json()
    access_token = token_data.get('access_token')
    user_info = get_discord_user_info(access_token)
    if not user_info: return 'Failed to get user info', 401
    
    user_id = user_info['id']
    username = user_info['username']
    avatar_hash = user_info.get('avatar')
    avatar_url = f'https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png' if avatar_hash else ''
    
    guilds = get_discord_user_guilds(access_token)
    cache_user_guilds(user_id, guilds)
    save_user_session(user_id, access_token, token_data.get('refresh_token'), username, avatar_url, token_data.get('expires_in', 604800))
    
    session['user_id'] = user_id
    session['username'] = username
    session['avatar_url'] = avatar_url
    return redirect('/dashboard')

@app.route('/auth/logout')
def logout():
    user_id = session.get('user_id')
    if user_id: delete_user_session(user_id)
    session.clear()
    return redirect('/')

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session.get('user_id')
    # A template-nek átadjuk a username-t és avatar-t a fejléchez
    response = app.make_response(render_template('dashboard.html', 
                         username=session.get('username'),
                         avatar_url=session.get('avatar_url')))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.route('/dashboard/server/<guild_id>')
@login_required
def server_settings(guild_id):
    user_id = session.get('user_id')
    # Ellenőrizzük az ID alapján a jogosultságot
    if not guild_exists_in_cache(user_id, guild_id): return 'Unauthorized', 403
    settings = get_guild_settings(guild_id)
    response = app.make_response(render_template('server_settings.html',
                         guild_id=guild_id,
                         username=session.get('username'),
                         avatar_url=session.get('avatar_url'),
                         settings=json.dumps(settings)))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.route('/api/settings/<guild_id>', methods=['GET'])
@login_required
def api_get_settings(guild_id):
    user_id = session.get('user_id')
    if not guild_exists_in_cache(user_id, guild_id): return jsonify({'error': 'Unauthorized'}), 403
    return jsonify(get_guild_settings(guild_id))

@app.route('/api/settings/<guild_id>', methods=['POST'])
@login_required
def api_update_settings(guild_id):
    user_id = session.get('user_id')
    if not guild_exists_in_cache(user_id, guild_id): return jsonify({'error': 'Unauthorized'}), 403
    try:
        data = request.get_json()
        update_guild_settings(guild_id, data)
        return jsonify({'success': True, 'message': 'Settings updated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/servers')
@login_required
def api_servers():
    """Visszaadja a szerverek TELJES adatait (ID, név, ikon) a Dashboardnak"""
    user_id = session.get('user_id')
    # Itt az objektumok listáját adjuk át, hogy a JS kiolvashassa a nevet és ID-t
    admin_guilds = get_user_admin_guilds(user_id) 
    return jsonify({'servers': admin_guilds})

@app.route('/help')
def help_page():
    response = app.make_response(render_template('help.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.route('/api/stats')
def api_stats():
    try:
        stats = get_bot_stats()
        uptime = datetime.now(timezone.utc) - stats['start_time']
        return jsonify({
            'guilds': stats.get('guilds', 0),
            'users': stats.get('users', 0),
            'uptime_seconds': int(uptime.total_seconds()),
            'status': stats.get('status', 'online')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- STABIL INDÍTÁSI LOGIKA (Render Fix) ---

def start_bot_process():
    """Bot indítása késleltetve a Web Szerver után"""
    print("\n⏳ Stabilization: Waiting 10s for Flask to bind port...", flush=True)
    time.sleep(10)
    print("\n🤖 Background process: Loading Discord modules...", flush=True)
    try:
        # Késleltetett import a Gunicorn fagyás ellen
        from main import bot
        TOKEN = os.getenv('DISCORD_TOKEN')
        if TOKEN:
            bot.run(TOKEN)
        else:
            print("❌ DISCORD_TOKEN is missing!", flush=True)
    except Exception as e:
        print(f"❌ Bot thread error: {e}", flush=True)

# Háttérszál regisztrálása (Gunicorn is elindítja)
print("\n📋 System: Registering background threads...", flush=True)
threading.Thread(target=start_bot_process, daemon=True, name="DiscordBot").start()

if __name__ == '__main__':
    # Lokális indítás (python web_server.py)
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Manual Startup on port {port}", flush=True)
    app.run(host='0.0.0.0', port=port, debug=False)
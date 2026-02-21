#!/usr/bin/env python3
import os
import sys
import subprocess
import threading
import time

# Ensure output is not buffered
os.environ['PYTHONUNBUFFERED'] = '1'

print("=" * 70, flush=True)
print("🚀 DiscordSage Application Startup", flush=True)
print("=" * 70, flush=True)
print(f"📁 Working directory: {os.getcwd()}", flush=True)
print(f"🐍 Python: {sys.executable}", flush=True)
print(f"🔑 DISCORD_TOKEN: {'✅ SET' if os.getenv('DISCORD_TOKEN') else '❌ NOT SET'}", flush=True)
print("=" * 70, flush=True)

def run_bot():
    """Run the Discord bot in subprocess with output capture"""
    print("\n🤖 [BOT] Starting bot subprocess...", flush=True)
    try:
        # Run bot.py with unbuffered output
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'
        
        process = subprocess.Popen(
            [sys.executable, '-u', 'main.py'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        print("🤖 [BOT] Bot subprocess started, reading output...", flush=True)
        
        # Stream output from bot
        for line in process.stdout:
            print(f"🤖 [BOT] {line.rstrip()}", flush=True)
        
        # Wait for process
        return_code = process.wait()
        print(f"❌ [BOT] Bot process exited with code {return_code}", flush=True)
        
    except Exception as e:
        print(f"❌ [BOT] Failed to start bot: {e}", flush=True)
        import traceback
        traceback.print_exc()

def run_web():
    """Run the Flask web server"""
    print("\n🌐 [WEB] Starting web server...", flush=True)
    try:
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'
        
        process = subprocess.Popen(
            [sys.executable, '-u', 'web_server.py'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        print("🌐 [WEB] Web server subprocess started, reading output...", flush=True)
        
        # Stream output from web server
        for line in process.stdout:
            print(f"🌐 [WEB] {line.rstrip()}", flush=True)
        
        # Wait for process
        return_code = process.wait()
        print(f"❌ [WEB] Web server process exited with code {return_code}", flush=True)
        
    except Exception as e:
        print(f"❌ [WEB] Failed to start web server: {e}", flush=True)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n📋 Starting both services...\n", flush=True)
    
    # Start bot in background thread
    bot_thread = threading.Thread(target=run_bot, daemon=False, name="BotThread")
    bot_thread.start()
    
    # Give bot a moment to start
    time.sleep(2)
    
    # Start web server in main thread (blocking)
    run_web()
    
    # If web server exits, wait for bot thread
    print("\n⏳ Waiting for bot thread...", flush=True)
    bot_thread.join(timeout=5)
    print("🛑 Application shutdown complete", flush=True)

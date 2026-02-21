import subprocess
import sys
import time
import threading

def run_bot():
    """Run the Discord bot"""
    print("🤖 Starting Discord Bot...")
    subprocess.run([sys.executable, "main.py"])

def run_web():
    """Run the Flask web server"""
    time.sleep(3)  # Wait for bot to initialize
    print("🌐 Starting Web Server...")
    subprocess.run([sys.executable, "web_server.py"])

if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot, daemon=False)
    web_thread = threading.Thread(target=run_web, daemon=False)
    
    bot_thread.start()
    web_thread.start()
    
    bot_thread.join()
    web_thread.join()

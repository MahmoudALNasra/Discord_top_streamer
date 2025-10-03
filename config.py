import os

# Get bot token from environment variable
BOT_TOKEN = os.environ.get('BOT_TOKEN', '')
DATABASE_PATH = "voice_tracker.db"

if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN environment variable is not set!")

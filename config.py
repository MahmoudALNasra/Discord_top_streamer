import os

BOT_TOKEN = os.environ.get('BOT_TOKEN', '')

if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN environment variable is not set!")

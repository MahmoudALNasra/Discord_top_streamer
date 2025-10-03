# 🎧 Discord Voice & Stream Tracker

A Discord bot that tracks voice channel time and streaming statistics, displaying top 5 users for each category.

## 🤖 Features

- **🎬 Stream Tracking**: Automatically tracks screen sharing/streaming time
- **🎧 Voice Time Tracking**: Tracks time spent in voice channels
- **🏆 Leaderboards**: Shows top 5 streamers and voice channel users
- **📊 Personal Stats**: View your own streaming and voice time statistics

## 🚀 Commands

- `!vt bot_help` - Show all available commands
- `!vt topstreamers` - Display top 5 streamers by total stream time
- `!vt topvoice` - Display top 5 voice channel users by time spent
- `!vt mystats` - Show your personal streaming and voice statistics

## 🛠️ Setup

### Prerequisites
- Python 3.8+
- Discord Bot Token

### Installation
1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variable: `BOT_TOKEN=your_bot_token_here`
4. Run: `python main.py`

### Hosting
This bot is designed to run on cloud platforms like:
- **Render** (recommended)
- **Railway**
- **Replit**
- **Heroku**

## 📊 How It Works

- **Automatically tracks** when users join/leave voice channels
- **Detects streaming** when users start/stop screen sharing
- **Stores data** in SQLite database
- **Updates leaderboards** in real-time

## 🔧 Configuration

Set the following environment variable:
- `BOT_TOKEN`: Your Discord bot token

## 📁 Project Structure

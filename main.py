import discord
from discord.ext import commands
from datetime import datetime
import config
from tracker import VoiceTimeTracker
from database import VoiceTrackerDatabase

class VoiceTrackerBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.voice_states = True
        intents.messages = True
        intents.guilds = True
        intents.message_content = True  # Explicitly enable message content
        
        super().__init__(command_prefix='!vt ', intents=intents)
        
        # Initialize components
        self.database = VoiceTrackerDatabase(config.DATABASE_PATH)
        self.tracker = VoiceTimeTracker(self.database)

# Bot Commands
@commands.command()
async def bot_help(ctx):
    """Show available commands"""
    print(f"🔧 Help command triggered by {ctx.author}")
    embed = discord.Embed(
        title="🎧 Voice & Stream Tracker Help",
        description="Track voice channel time and streaming statistics",
        color=0x7289DA
    )
    embed.add_field(name="!vt topstreamers", value="Show top 5 streamers", inline=False)
    embed.add_field(name="!vt topvoice", value="Show top 5 voice channel users", inline=False)
    embed.add_field(name="!vt mystats", value="Show your personal statistics", inline=False)
    embed.add_field(name="!vt bot_help", value="Show this help message", inline=False)
    
    await ctx.send(embed=embed)

@commands.command()
async def topstreamers(ctx):
    """Show top 5 streamers by total stream time"""
    print(f"🔧 Topstreamers command triggered by {ctx.author}")
    top_streamers = ctx.bot.database.get_top_streamers(5)
    
    embed = discord.Embed(
        title="🎬 Top 5 Streamers",
        description="Most dedicated streamers by total stream time",
        color=0x9146FF,  # Twitch purple
        timestamp=datetime.now()
    )
    
    if top_streamers:
        for i, streamer in enumerate(top_streamers, 1):
            hours = streamer['total_stream_time'] / 3600
            sessions = streamer['sessions']
            
            # Get current username
            user = ctx.bot.get_user(streamer['user_id'])
            username = user.display_name if user else streamer['username']
            
            embed.add_field(
                name=f"{i}. {username}",
                value=f"⏱️ {hours:.1f} hours • {sessions} streams",
                inline=False
            )
    else:
        embed.description = "No streaming data yet! Start streaming to see stats."
    
    await ctx.send(embed=embed)

@commands.command()
async def topvoice(ctx):
    """Show top 5 voice channel users by time spent"""
    print(f"🔧 Topvoice command triggered by {ctx.author}")
    top_voice_users = ctx.bot.database.get_top_voice_users(5)
    
    embed = discord.Embed(
        title="🎧 Top 5 Voice Champions",
        description="Most active users in voice channels",
        color=0x00ff00,
        timestamp=datetime.now()
    )
    
    if top_voice_users:
        for i, user_data in enumerate(top_voice_users, 1):
            hours = user_data['total_voice_time'] / 3600
            sessions = user_data['sessions']
            
            # Get current username
            user = ctx.bot.get_user(user_data['user_id'])
            username = user.display_name if user else user_data['username']
            
            embed.add_field(
                name=f"{i}. {username}",
                value=f"⏱️ {hours:.1f} hours • {sessions} sessions",
                inline=False
            )
    else:
        embed.description = "No voice channel data yet! Join voice channels to see stats."
    
    await ctx.send(embed=embed)

@commands.command()
async def mystats(ctx):
    """Show user's personal statistics"""
    print(f"🔧 Mystats command triggered by {ctx.author}")
    user_id = ctx.author.id
    
    # Get user's streaming stats
    top_streamers = ctx.bot.database.get_top_streamers(100)  # Get all to find user
    user_stream_rank = None
    user_stream_stats = None
    
    for i, streamer in enumerate(top_streamers, 1):
        if streamer['user_id'] == user_id:
            user_stream_rank = i
            user_stream_stats = streamer
            break
    
    # Get user's voice stats
    top_voice_users = ctx.bot.database.get_top_voice_users(100)  # Get all to find user
    user_voice_rank = None
    user_voice_stats = None
    
    for i, user_data in enumerate(top_voice_users, 1):
        if user_data['user_id'] == user_id:
            user_voice_rank = i
            user_voice_stats = user_data
            break
    
    embed = discord.Embed(
        title=f"📊 {ctx.author.display_name}'s Statistics",
        color=0x7289DA,
        timestamp=datetime.now()
    )
    
    # Streaming stats
    if user_stream_stats:
        stream_hours = user_stream_stats['total_stream_time'] / 3600
        embed.add_field(
            name="🎬 Streaming",
            value=f"**{stream_hours:.1f} hours**\n#{user_stream_rank} • {user_stream_stats['sessions']} streams",
            inline=True
        )
    else:
        embed.add_field(
            name="🎬 Streaming",
            value="No streaming data",
            inline=True
        )
    
    # Voice stats
    if user_voice_stats:
        voice_hours = user_voice_stats['total_voice_time'] / 3600
        embed.add_field(
            name="🎧 Voice Time",
            value=f"**{voice_hours:.1f} hours**\n#{user_voice_rank} • {user_voice_stats['sessions']} sessions",
            inline=True
        )
    else:
        embed.add_field(
            name="🎧 Voice Time",
            value="No voice data",
            inline=True
        )
    
    await ctx.send(embed=embed)

# Initialize and run bot
if __name__ == "__main__":
    bot = VoiceTrackerBot()
    
    # Add debug events
    @bot.event
    async def on_ready():
        print(f'✅ {bot.user} has connected to Discord!')
        print(f'📊 Voice Tracker is monitoring {len(bot.guilds)} server(s)')
        print('🤖 Bot is ready! Testing intents...')
        print(f'Message Content Intent: {bot.intents.message_content}')
        print(f'Guilds Intent: {bot.intents.guilds}')
        print(f'Voice States Intent: {bot.intents.voice_states}')
        print('💬 Use !vt bot_help for commands')
    
    @bot.event
    async def on_message(message):
        # Ignore bot's own messages
        if message.author == bot.user:
            return
        
        # Log all messages that start with the command prefix
        if message.content.startswith('!vt '):
            print(f"📨 Command received: '{message.content}' from {message.author} in #{message.channel}")
        
        # Process commands
        await bot.process_commands(message)
    
    # Add commands
    bot.add_command(bot_help)
    bot.add_command(topstreamers)
    bot.add_command(topvoice)
    bot.add_command(mystats)
    
    print("🚀 Starting Discord Voice & Stream Tracker...")
    print("🔧 Debug mode enabled")
    
    try:
        bot.run(config.BOT_TOKEN)
    except discord.LoginFailure:
        print("❌ Invalid bot token! Please check config.py")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")

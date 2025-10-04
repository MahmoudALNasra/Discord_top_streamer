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
        intents.message_content = True
        
        super().__init__(command_prefix='!vt ', intents=intents)
        
        # Initialize components - REMOVED DATABASE_PATH
        self.database = VoiceTrackerDatabase()  # ← CHANGED THIS LINE
        self.tracker = VoiceTimeTracker(self.database)
    
    async def on_ready(self):
        print(f'✅ {self.user} has connected to Discord!')
        print(f'📊 Voice Tracker is monitoring {len(self.guilds)} server(s)')
        print('🤖 Use !vt bot_help for commands')
    
    async def on_voice_state_update(self, member, before, after):
        await self.tracker.handle_voice_state_update(member, before, after)

# Bot Commands
@commands.command()
async def bot_help(ctx):
    """Show available commands"""
    embed = discord.Embed(
        title="🎧 Voice & Stream Tracker Help",
        description="Track voice channel time and streaming statistics",
        color=0x7289DA
    )
    embed.add_field(name="!vt topstreamers", value="Show top 5 streamers", inline=False)
    embed.add_field(name="!vt topvoice", value="Show top 5 voice channel users", inline=False)
    embed.add_field(name="!vt mystats", value="Show your personal statistics", inline=False)
    embed.add_field(name="!vt debug", value="Debug database information", inline=False)
    embed.add_field(name="!vt bot_help", value="Show this help message", inline=False)
    
    await ctx.send(embed=embed)

@commands.command()
async def topstreamers(ctx):
    """Show top 5 streamers by total stream time"""
    top_streamers = ctx.bot.database.get_top_streamers(5)
    
    embed = discord.Embed(
        title="🎬 Top 5 Streamers",
        description="Most dedicated streamers by total stream time",
        color=0x9146FF,
        timestamp=datetime.now()
    )
    
    if top_streamers:
        for i, streamer in enumerate(top_streamers, 1):
            hours = streamer['total_stream_time'] / 3600
            sessions = streamer['sessions']
            
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
    user_id = ctx.author.id
    
    top_streamers = ctx.bot.database.get_top_streamers(100)
    user_stream_rank = None
    user_stream_stats = None
    
    for i, streamer in enumerate(top_streamers, 1):
        if streamer['user_id'] == user_id:
            user_stream_rank = i
            user_stream_stats = streamer
            break
    
    top_voice_users = ctx.bot.database.get_top_voice_users(100)
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

@commands.command()
async def debug(ctx):
    """Debug command to check database"""
    user_id = ctx.author.id
    
    top_voice = ctx.bot.database.get_top_voice_users(10)
    top_stream = ctx.bot.database.get_top_streamers(10)
    
    user_in_voice = any(user['user_id'] == user_id for user in top_voice)
    user_in_stream = any(user['user_id'] == user_id for user in top_stream)
    
    debug_info = f"**Debug Info for {ctx.author.display_name}**\n"
    debug_info += f"User ID: {user_id}\n"
    debug_info += f"Voice Users in DB: {len(top_voice)}\n"
    debug_info += f"Streamers in DB: {len(top_stream)}\n"
    debug_info += f"You in Voice Data: {user_in_voice}\n"
    debug_info += f"You in Stream Data: {user_in_stream}\n"
    
    await ctx.send(f"```{debug_info}```")

# Initialize and run bot
if __name__ == "__main__":
    bot = VoiceTrackerBot()
    
    @bot.event
    async def on_ready():
        print(f'✅ {bot.user} has connected to Discord!')
        print('🤖 Bot is ready!')
    
    # Add commands
    bot.add_command(bot_help)
    bot.add_command(topstreamers)
    bot.add_command(topvoice)
    bot.add_command(mystats)
    bot.add_command(debug)
    
    print("🚀 Starting Discord Voice & Stream Tracker...")
    
    try:
        bot.run(config.BOT_TOKEN)
    except Exception as e:
        print(f"❌ Error: {e}")

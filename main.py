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
        
        self.database = VoiceTrackerDatabase(config.DATABASE_PATH)
        self.tracker = VoiceTimeTracker(self.database)

@commands.command()
async def bot_help(ctx):
    embed = discord.Embed(title="🎧 Voice & Stream Tracker Help", color=0x7289DA)
    embed.add_field(name="!vt topstreamers", value="Show top 5 streamers", inline=False)
    embed.add_field(name="!vt topvoice", value="Show top 5 voice channel users", inline=False)
    embed.add_field(name="!vt mystats", value="Show your personal statistics", inline=False)
    embed.add_field(name="!vt debug", value="Debug database information", inline=False)
    await ctx.send(embed=embed)

@commands.command()
async def topstreamers(ctx):
    top_streamers = ctx.bot.database.get_top_streamers(5)
    embed = discord.Embed(title="🎬 Top 5 Streamers", color=0x9146FF)
    if top_streamers:
        for i, streamer in enumerate(top_streamers, 1):
            user = ctx.bot.get_user(streamer['user_id'])
            username = user.display_name if user else streamer['username']
            hours = streamer['total_stream_time'] / 3600
            embed.add_field(name=f"{i}. {username}", value=f"⏱️ {hours:.1f} hours", inline=False)
    else:
        embed.description = "No streaming data yet!"
    await ctx.send(embed=embed)

@commands.command()
async def topvoice(ctx):
    top_voice_users = ctx.bot.database.get_top_voice_users(5)
    embed = discord.Embed(title="🎧 Top 5 Voice Champions", color=0x00ff00)
    if top_voice_users:
        for i, user_data in enumerate(top_voice_users, 1):
            user = ctx.bot.get_user(user_data['user_id'])
            username = user.display_name if user else user_data['username']
            hours = user_data['total_voice_time'] / 3600
            embed.add_field(name=f"{i}. {username}", value=f"⏱️ {hours:.1f} hours", inline=False)
    else:
        embed.description = "No voice channel data yet!"
    await ctx.send(embed=embed)

@commands.command()
async def mystats(ctx):
    user_id = ctx.author.id
    embed = discord.Embed(title=f"📊 {ctx.author.display_name}'s Statistics", color=0x7289DA)
    
    # Check voice data
    top_voice = ctx.bot.database.get_top_voice_users(100)
    user_voice = next((user for user in top_voice if user['user_id'] == user_id), None)
    if user_voice:
        voice_hours = user_voice['total_voice_time'] / 3600
        embed.add_field(name="🎧 Voice Time", value=f"{voice_hours:.1f} hours", inline=True)
    else:
        embed.add_field(name="🎧 Voice Time", value="No data", inline=True)
    
    # Check stream data
    top_stream = ctx.bot.database.get_top_streamers(100)
    user_stream = next((user for user in top_stream if user['user_id'] == user_id), None)
    if user_stream:
        stream_hours = user_stream['total_stream_time'] / 3600
        embed.add_field(name="🎬 Streaming", value=f"{stream_hours:.1f} hours", inline=True)
    else:
        embed.add_field(name="🎬 Streaming", value="No data", inline=True)
    
    await ctx.send(embed=embed)

@commands.command()
async def debug(ctx):
    """Debug command to check database"""
    user_id = ctx.author.id
    
    # Check database
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

if __name__ == "__main__":
    bot = VoiceTrackerBot()
    
    @bot.event
    async def on_ready():
        print(f'✅ {bot.user} has connected to Discord!')
        print('🤖 Bot is ready!')
    
    # Add ALL commands here
    bot.add_command(bot_help)
    bot.add_command(topstreamers)
    bot.add_command(topvoice)
    bot.add_command(mystats)
    bot.add_command(debug)  # Make sure this is included
    
    print("🚀 Starting Discord Voice & Stream Tracker...")
    
    try:
        bot.run(config.BOT_TOKEN)
    except Exception as e:
        print(f"❌ Error: {e}")

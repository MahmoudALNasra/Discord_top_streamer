import discord
from datetime import datetime
from database import VoiceTrackerDatabase

class VoiceTimeTracker:
    def __init__(self, database):
        self.db = database
    
    async def handle_voice_state_update(self, member, before, after):
        """Track voice channel joins/leaves and streaming"""
        try:
            # User joined a voice channel
            if not before.channel and after.channel:
                await self.user_joined_voice(member, after.channel)
            
            # User left a voice channel
            if before.channel and not after.channel:
                await self.user_left_voice(member, before.channel)
            
            # User started streaming
            if before and not before.self_stream and after and after.self_stream:
                await self.user_started_streaming(member, after.channel)
            
            # User stopped streaming
            if before and before.self_stream and after and not after.self_stream:
                await self.user_stopped_streaming(member, before.channel)
                
        except Exception as e:
            print(f"❌ Error in voice tracker: {e}")
    
    async def user_joined_voice(self, member, channel):
        """User joined any voice channel"""
        self.db.start_voice_session(member.id, member.display_name, channel.id)
        print(f"🎧 {member.display_name} joined voice channel {channel.name}")
    
    async def user_left_voice(self, member, channel):
        """User left any voice channel"""
        duration = self.db.end_voice_session(member.id)
        if duration > 0:
            print(f"🚪 {member.display_name} left voice channel after {duration:.0f} seconds")
    
    async def user_started_streaming(self, member, channel):
        """User started screen sharing/streaming"""
        self.db.start_stream_session(member.id, member.display_name, channel.id)
        print(f"🎬 {member.display_name} started streaming in {channel.name}")
    
    async def user_stopped_streaming(self, member, channel):
        """User stopped screen sharing/streaming"""
        duration = self.db.end_stream_session(member.id)
        if duration > 0:
            print(f"⏹️ {member.display_name} stopped streaming after {duration:.0f} seconds")

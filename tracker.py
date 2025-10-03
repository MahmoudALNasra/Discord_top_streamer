import discord
from datetime import datetime
from database import VoiceTrackerDatabase

class VoiceTimeTracker:
    def __init__(self, database):
        self.db = database
    
    async def handle_voice_state_update(self, member, before, after):
        """Track voice channel joins/leaves and streaming"""
        print(f"🔊 Voice state update: {member.display_name} | "
              f"Before: {before.channel.name if before and before.channel else 'None'} | "
              f"After: {after.channel.name if after and after.channel else 'None'} | "
              f"Stream: {after.self_stream if after else 'N/A'}")

        try:
            # User joined a voice channel
            if not before.channel and after.channel:
                print(f"🎧 JOIN: {member.display_name} joined {after.channel.name}")
                await self.user_joined_voice(member, after.channel)
            
            # User left a voice channel
            if before.channel and not after.channel:
                print(f"🚪 LEAVE: {member.display_name} left {before.channel.name}")
                await self.user_left_voice(member, before.channel)
            
            # User started streaming
            if before and not before.self_stream and after and after.self_stream:
                print(f"🎬 STREAM START: {member.display_name} started streaming")
                await self.user_started_streaming(member, after.channel)
            
            # User stopped streaming
            if before and before.self_stream and after and not after.self_stream:
                print(f"⏹️ STREAM STOP: {member.display_name} stopped streaming")
                await self.user_stopped_streaming(member, before.channel)
                
        except Exception as e:
            print(f"❌ Error in voice tracker: {e}")
    
    async def user_joined_voice(self, member, channel):
        """User joined any voice channel"""
        print(f"✅ Starting voice session for {member.display_name}")
        self.db.start_voice_session(member.id, member.display_name, channel.id)
    
    async def user_left_voice(self, member, channel):
        """User left any voice channel"""
        print(f"✅ Ending voice session for {member.display_name}")
        duration = self.db.end_voice_session(member.id)
        if duration > 0:
            print(f"⏱️ {member.display_name} voice session: {duration:.1f} minutes")
        else:
            print(f"⚠️ No duration recorded for {member.display_name}")
    
    async def user_started_streaming(self, member, channel):
        """User started screen sharing/streaming"""
        print(f"✅ Starting stream session for {member.display_name}")
        self.db.start_stream_session(member.id, member.display_name, channel.id)
    
    async def user_stopped_streaming(self, member, channel):
        """User stopped screen sharing/streaming"""
        print(f"✅ Ending stream session for {member.display_name}")
        duration = self.db.end_stream_session(member.id)
        if duration > 0:
            print(f"⏱️ {member.display_name} stream session: {duration:.1f} minutes")
        else:
            print(f"⚠️ No stream duration recorded for {member.display_name}")

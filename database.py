import sqlite3
from datetime import datetime

class VoiceTrackerDatabase:
    def __init__(self, db_path: str = "voice_tracker.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Streamers table - tracks streaming time
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS streamers (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                total_stream_time INTEGER DEFAULT 0,  -- in seconds
                stream_sessions INTEGER DEFAULT 0,
                last_streamed TIMESTAMP
            )
        ''')
        
        # Voice time table - tracks general voice channel time
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS voice_time (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                total_voice_time INTEGER DEFAULT 0,  -- in seconds
                voice_sessions INTEGER DEFAULT 0,
                last_joined TIMESTAMP
            )
        ''')
        
        # Active sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS active_sessions (
                user_id INTEGER PRIMARY KEY,
                session_type TEXT,  -- 'stream' or 'voice'
                start_time TIMESTAMP,
                channel_id INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Voice Tracker Database initialized successfully!")
    
    # Streamer methods
    def start_stream_session(self, user_id, username, channel_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO active_sessions 
            (user_id, session_type, start_time, channel_id)
            VALUES (?, 'stream', datetime('now'), ?)
        ''', (user_id, channel_id))
        
        conn.commit()
        conn.close()
    
    def end_stream_session(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get session start time
        cursor.execute('''
            SELECT start_time FROM active_sessions 
            WHERE user_id = ? AND session_type = 'stream'
        ''', (user_id,))
        
        result = cursor.fetchone()
        if result:
            start_time = datetime.fromisoformat(result[0])
            stream_duration = (datetime.now() - start_time).total_seconds()
            
            # Update streamer stats
            cursor.execute('''
                INSERT INTO streamers (user_id, username, total_stream_time, stream_sessions, last_streamed)
                VALUES (?, ?, ?, 1, datetime('now'))
                ON CONFLICT(user_id) 
                DO UPDATE SET 
                    total_stream_time = total_stream_time + ?,
                    stream_sessions = stream_sessions + 1,
                    last_streamed = datetime('now'),
                    username = excluded.username
            ''', (user_id, f"User_{user_id}", stream_duration, stream_duration))
            
            # Remove active session
            cursor.execute('''
                DELETE FROM active_sessions 
                WHERE user_id = ? AND session_type = 'stream'
            ''', (user_id,))
        
        conn.commit()
        conn.close()
        return stream_duration if result else 0
    
    # Voice time methods
    def start_voice_session(self, user_id, username, channel_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO active_sessions 
            (user_id, session_type, start_time, channel_id)
            VALUES (?, 'voice', datetime('now'), ?)
        ''', (user_id, channel_id))
        
        conn.commit()
        conn.close()
    
    def end_voice_session(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get session start time
        cursor.execute('''
            SELECT start_time FROM active_sessions 
            WHERE user_id = ? AND session_type = 'voice'
        ''', (user_id,))
        
        result = cursor.fetchone()
        if result:
            start_time = datetime.fromisoformat(result[0])
            voice_duration = (datetime.now() - start_time).total_seconds()
            
            # Update voice time stats
            cursor.execute('''
                INSERT INTO voice_time (user_id, username, total_voice_time, voice_sessions, last_joined)
                VALUES (?, ?, ?, 1, datetime('now'))
                ON CONFLICT(user_id) 
                DO UPDATE SET 
                    total_voice_time = total_voice_time + ?,
                    voice_sessions = voice_sessions + 1,
                    last_joined = datetime('now'),
                    username = excluded.username
            ''', (user_id, f"User_{user_id}", voice_duration, voice_duration))
            
            # Remove active session
            cursor.execute('''
                DELETE FROM active_sessions 
                WHERE user_id = ? AND session_type = 'voice'
            ''', (user_id,))
        
        conn.commit()
        conn.close()
        return voice_duration if result else 0
    
    # Leaderboard methods
    def get_top_streamers(self, limit=5):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, username, total_stream_time, stream_sessions
            FROM streamers 
            ORDER BY total_stream_time DESC 
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [{
            'user_id': row[0],
            'username': row[1],
            'total_stream_time': row[2],
            'sessions': row[3]
        } for row in results]
    
    def get_top_voice_users(self, limit=5):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, username, total_voice_time, voice_sessions
            FROM voice_time 
            ORDER BY total_voice_time DESC 
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [{
            'user_id': row[0],
            'username': row[1],
            'total_voice_time': row[2],
            'sessions': row[3]
        } for row in results]

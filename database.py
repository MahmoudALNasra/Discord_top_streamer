import sqlite3
import os
from datetime import datetime

class VoiceTrackerDatabase:
    def __init__(self, db_path: str = "/tmp/voice_tracker.db"):
        self.db_path = db_path
        self.memory_db = None
        self.init_database()
    
    def get_connection(self):
        try:
            return sqlite3.connect(self.db_path)
        except:
            if self.memory_db is None:
                self.memory_db = sqlite3.connect(':memory:')
                self._init_memory_tables(self.memory_db)
            return self.memory_db
    
    def _init_memory_tables(self, conn):
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS streamers (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                total_stream_time INTEGER DEFAULT 0,
                stream_sessions INTEGER DEFAULT 0,
                last_streamed TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS voice_time (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                total_voice_time INTEGER DEFAULT 0,
                voice_sessions INTEGER DEFAULT 0,
                last_joined TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS active_sessions (
                user_id INTEGER PRIMARY KEY,
                session_type TEXT,
                start_time TIMESTAMP,
                channel_id INTEGER
            )
        ''')
        conn.commit()
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS streamers (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                total_stream_time INTEGER DEFAULT 0,
                stream_sessions INTEGER DEFAULT 0,
                last_streamed TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS voice_time (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                total_voice_time INTEGER DEFAULT 0,
                voice_sessions INTEGER DEFAULT 0,
                last_joined TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS active_sessions (
                user_id INTEGER PRIMARY KEY,
                session_type TEXT,
                start_time TIMESTAMP,
                channel_id INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database initialized (File + Memory fallback)")
    
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
        print(f"🎧 Voice session started for {username}")
    
    def end_voice_session(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT start_time FROM active_sessions 
            WHERE user_id = ? AND session_type = 'voice'
        ''', (user_id,))
        
        result = cursor.fetchone()
        if result:
            start_time = datetime.fromisoformat(result[0])
            duration = (datetime.now() - start_time).total_seconds()
            
            cursor.execute('SELECT total_voice_time FROM voice_time WHERE user_id = ?', (user_id,))
            current_data = cursor.fetchone()
            current_total = current_data[0] if current_data else 0
            
            cursor.execute('''
                INSERT INTO voice_time (user_id, username, total_voice_time, voice_sessions, last_joined)
                VALUES (?, ?, ?, 1, datetime('now'))
                ON CONFLICT(user_id) 
                DO UPDATE SET 
                    total_voice_time = ?,
                    voice_sessions = voice_sessions + 1,
                    last_joined = datetime('now')
            ''', (user_id, f"User_{user_id}", current_total + duration, current_total + duration))
            
            cursor.execute('DELETE FROM active_sessions WHERE user_id = ?', (user_id,))
            
            conn.commit()
            conn.close()
            print(f"⏱️ Recorded {duration/60:.1f} minutes voice time")
            return duration / 60
        
        conn.close()
        return 0
    
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
        print(f"🎬 Stream session started for {username}")
    
    def end_stream_session(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT start_time FROM active_sessions 
            WHERE user_id = ? AND session_type = 'stream'
        ''', (user_id,))
        
        result = cursor.fetchone()
        if result:
            start_time = datetime.fromisoformat(result[0])
            duration = (datetime.now() - start_time).total_seconds()
            
            cursor.execute('SELECT total_stream_time FROM streamers WHERE user_id = ?', (user_id,))
            current_data = cursor.fetchone()
            current_total = current_data[0] if current_data else 0
            
            cursor.execute('''
                INSERT INTO streamers (user_id, username, total_stream_time, stream_sessions, last_streamed)
                VALUES (?, ?, ?, 1, datetime('now'))
                ON CONFLICT(user_id) 
                DO UPDATE SET 
                    total_stream_time = ?,
                    stream_sessions = stream_sessions + 1,
                    last_streamed = datetime('now')
            ''', (user_id, f"User_{user_id}", current_total + duration, current_total + duration))
            
            cursor.execute('DELETE FROM active_sessions WHERE user_id = ?', (user_id,))
            
            conn.commit()
            conn.close()
            print(f"⏱️ Recorded {duration/60:.1f} minutes stream time")
            return duration / 60
        
        conn.close()
        return 0
    
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
        
        return [{'user_id': row[0], 'username': row[1], 'total_voice_time': row[2], 'sessions': row[3]} for row in results]
    
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
        
        return [{'user_id': row[0], 'username': row[1], 'total_stream_time': row[2], 'sessions': row[3]} for row in results]
    
    def get_user_watch_stats(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT total_voice_time, voice_sessions FROM voice_time WHERE user_id = ?', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {'total_voice_time': result[0], 'sessions': result[1]}
        return None

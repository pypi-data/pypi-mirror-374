import sqlite3
import time
from datetime import datetime

class BlockDB:
    def __init__(self):
        self.conn = sqlite3.connect('ffcapcha_blocks.db', check_same_thread=False)
        self.create_table()
    
    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blocked_users (
                user_id INTEGER PRIMARY KEY,
                reason TEXT,
                timestamp REAL,
                expires_at REAL
            )
        ''')
        self.conn.commit()
    
    def add_block(self, user_id, reason="spam", ban_time=300):
        timestamp = time.time()
        expires_at = timestamp + ban_time
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO blocked_users 
            VALUES (?, ?, ?, ?)
        ''', (user_id, reason, timestamp, expires_at))
        self.conn.commit()
    
    def remove_block(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM blocked_users WHERE user_id = ?', (user_id,))
        self.conn.commit()
    
    def is_blocked(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM blocked_users 
            WHERE user_id = ? AND expires_at > ?
        ''', (user_id, time.time()))
        return cursor.fetchone() is not None
    
    def get_all_blocks(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM blocked_users WHERE expires_at > ?', (time.time(),))
        return cursor.fetchall()
    
    def cleanup(self):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM blocked_users WHERE expires_at <= ?', (time.time(),))
        self.conn.commit()

# Глобальный экземпляр базы данных
block_db = BlockDB()
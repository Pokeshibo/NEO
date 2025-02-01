import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('bot_data.db')
        self.c = self.conn.cursor()
        self.initialize_db()
    
    def initialize_db(self):
        self.c.execute('''CREATE TABLE IF NOT EXISTS warnings (
            user_id TEXT,
            guild_id TEXT,
            count INTEGER,
            PRIMARY KEY (user_id, guild_id))''')
        
        self.c.execute('''CREATE TABLE IF NOT EXISTS bad_words (
            guild_id TEXT,
            word TEXT,
            PRIMARY KEY (guild_id, word))''')
        
        self.c.execute('''CREATE TABLE IF NOT EXISTS guild_settings (
            guild_id TEXT PRIMARY KEY,
            spam_limit INTEGER DEFAULT 5,
            warn_limit INTEGER DEFAULT 3)''')
        
        self.c.execute('''CREATE TABLE IF NOT EXISTS invites (
            invite_code TEXT PRIMARY KEY,
            inviter_id TEXT,
            guild_id TEXT,
            uses INTEGER DEFAULT 0)''')
        
        self.c.execute('''CREATE TABLE IF NOT EXISTS invite_tracking (
            member_id TEXT,
            guild_id TEXT,
            invite_code TEXT,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        self.conn.commit()

db = Database()

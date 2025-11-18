import sqlite3
from config import DB_NAME

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT
        );

        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_uuid TEXT UNIQUE,
            creator_id INTEGER,
            name TEXT,
            budget TEXT,
            location TEXT,
            meeting_date TEXT,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY(creator_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER,
            user_id INTEGER,
            player_name TEXT,
            wishlist TEXT,
            recipient_id INTEGER DEFAULT NULL,
            FOREIGN KEY(game_id) REFERENCES games(id),
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(recipient_id) REFERENCES players(id)
        );

        CREATE TABLE IF NOT EXISTS exclusions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER,
            player_id INTEGER,
            forbidden_id INTEGER,
            FOREIGN KEY(game_id) REFERENCES games(id),
            FOREIGN KEY(player_id) REFERENCES players(id),
            FOREIGN KEY(forbidden_id) REFERENCES players(id)
        );
        """)
        conn.commit()
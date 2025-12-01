from database.core import get_connection

def add_user(user_id, username, full_name):
    with get_connection() as conn:
        conn.execute("INSERT OR IGNORE INTO users (id, username, full_name) VALUES (?, ?, ?)", 
                     (user_id, username, full_name))
        conn.commit()

def create_game(uuid, creator_id, name, budget, location, date):
    with get_connection() as conn:
        cur = conn.execute("""
            INSERT INTO games (game_uuid, creator_id, name, budget, location, meeting_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (uuid, creator_id, name, budget, location, date))
        conn.commit()
        return cur.lastrowid

def get_game_by_uuid(uuid):
    with get_connection() as conn:
        return conn.execute("SELECT * FROM games WHERE game_uuid = ?", (uuid,)).fetchone()

def get_game_by_id(game_id):
    with get_connection() as conn:
        return conn.execute("SELECT * FROM games WHERE id = ?", (game_id,)).fetchone()

def get_user_games(user_id):
    with get_connection() as conn:
        return conn.execute("""
            SELECT g.* FROM games g
            JOIN players p ON g.id = p.game_id
            WHERE p.user_id = ? AND g.is_active = 1
        """, (user_id,)).fetchall()

def delete_game(game_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM exclusions WHERE game_id = ?", (game_id,))
        conn.execute("DELETE FROM players WHERE game_id = ?", (game_id,))
        conn.execute("DELETE FROM games WHERE id = ?", (game_id,))
        conn.commit()

def deactivate_game(game_id):
    with get_connection() as conn:
        conn.execute("UPDATE games SET is_active = 0 WHERE id = ?", (game_id,))
        conn.commit()

def add_player(game_id, user_id, name, wish):
    with get_connection() as conn:
        cur = conn.execute("INSERT INTO players (game_id, user_id, player_name, wishlist) VALUES (?, ?, ?, ?)",
                     (game_id, user_id, name, wish))
        conn.commit()
        return cur.lastrowid

def get_player(user_id, game_id):
    with get_connection() as conn:
        return conn.execute("SELECT * FROM players WHERE user_id = ? AND game_id = ?", (user_id, game_id)).fetchone()

def get_players_in_game(game_id):
    with get_connection() as conn:
        return conn.execute("SELECT * FROM players WHERE game_id = ?", (game_id,)).fetchall()

def get_player_by_id(player_id):
    with get_connection() as conn:
        return conn.execute("SELECT * FROM players WHERE id = ?", (player_id,)).fetchone()

def set_recipient(giver_player_id, recipient_player_id):
    with get_connection() as conn:
        conn.execute("UPDATE players SET recipient_id = ? WHERE id = ?", (recipient_player_id, giver_player_id))
        conn.commit()

def add_exclusion(game_id, player_id, forbidden_id):
    with get_connection() as conn:
        conn.execute("INSERT INTO exclusions (game_id, player_id, forbidden_id) VALUES (?, ?, ?)",
                     (game_id, player_id, forbidden_id))
        conn.commit()

def get_exclusions(game_id):
    with get_connection() as conn:
        rows = conn.execute("SELECT player_id, forbidden_id FROM exclusions WHERE game_id = ?", (game_id,)).fetchall()
        return [(r['player_id'], r['forbidden_id']) for r in rows]
    
def update_wishlist(player_id, new_text):
    with get_connection() as conn:
        conn.execute("UPDATE players SET wishlist = ? WHERE id = ?", (new_text, player_id))
        conn.commit()

def leave_game(game_id, user_id):
    with get_connection() as conn:
        player = conn.execute("SELECT id FROM players WHERE game_id = ? AND user_id = ?", 
                              (game_id, user_id)).fetchone()
        
        if player:
            p_id = player['id']
            conn.execute("DELETE FROM exclusions WHERE player_id = ? OR forbidden_id = ?", (p_id, p_id))
            conn.execute("DELETE FROM players WHERE id = ?", (p_id,))
            conn.commit()
            return True
        return False
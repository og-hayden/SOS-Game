from typing import List, Dict, Optional, Tuple
import sqlite3
from datetime import datetime

class GameDatabase:
    def __init__(self, db_path: str = "sos_game.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create games table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS games (
                game_id INTEGER PRIMARY KEY AUTOINCREMENT,
                board_size INTEGER NOT NULL,
                game_mode TEXT NOT NULL,
                blue_player_type TEXT NOT NULL,
                red_player_type TEXT NOT NULL,
                winner TEXT,
                blue_score INTEGER DEFAULT 0,
                red_score INTEGER DEFAULT 0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create moves table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS moves (
                move_id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id INTEGER NOT NULL,
                player TEXT NOT NULL,
                row INTEGER NOT NULL,
                col INTEGER NOT NULL,
                letter TEXT NOT NULL,
                move_number INTEGER NOT NULL,
                FOREIGN KEY (game_id) REFERENCES games (game_id)
            )
        ''')

        # Create SOS lines table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sos_lines (
                line_id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id INTEGER NOT NULL,
                move_number INTEGER NOT NULL,
                start_row INTEGER NOT NULL,
                start_col INTEGER NOT NULL,
                end_row INTEGER NOT NULL,
                end_col INTEGER NOT NULL,
                player TEXT NOT NULL,
                FOREIGN KEY (game_id) REFERENCES games (game_id)
            )
        ''')

        conn.commit()
        conn.close()

    def start_new_game(self, board_size: int, game_mode: str, 
                      blue_player_type: str, red_player_type: str) -> int:
        """Start a new game and return its ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO games (board_size, game_mode, blue_player_type, red_player_type)
            VALUES (?, ?, ?, ?)
        ''', (board_size, game_mode, blue_player_type, red_player_type))

        game_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return game_id

    def save_move(self, game_id: int, player: str, row: int, col: int, 
                  letter: str, move_number: int):
        """Save a move to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO moves (game_id, player, row, col, letter, move_number)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (game_id, player, row, col, letter, move_number))

        conn.commit()
        conn.close()

    def end_game(self, game_id: int, winner: str, blue_score: int, red_score: int):
        """Update game record with final results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE games 
            SET winner = ?, blue_score = ?, red_score = ?
            WHERE game_id = ?
        ''', (winner, blue_score, red_score, game_id))

        conn.commit()
        conn.close()

    def get_recent_games(self, limit: int = 10) -> List[Dict]:
        """Get the most recent games"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT game_id, board_size, game_mode, blue_player_type, 
                   red_player_type, winner, blue_score, red_score, timestamp
            FROM games
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))

        games = []
        for row in cursor.fetchall():
            games.append({
                'game_id': row[0],
                'board_size': row[1],
                'game_mode': row[2],
                'blue_player_type': row[3],
                'red_player_type': row[4],
                'winner': row[5],
                'blue_score': row[6],
                'red_score': row[7],
                'timestamp': row[8]
            })

        conn.close()
        return games

    def get_game_moves(self, game_id: int) -> List[Dict]:
        """Get all moves for a specific game"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT player, row, col, letter, move_number
            FROM moves
            WHERE game_id = ?
            ORDER BY move_number
        ''', (game_id,))

        moves = []
        for row in cursor.fetchall():
            moves.append({
                'player': row[0],
                'row': row[1],
                'col': row[2],
                'letter': row[3],
                'move_number': row[4]
            })

        conn.close()
        return moves

    def save_sos_line(self, game_id: int, move_number: int, start_pos: List[int], 
                      end_pos: List[int], player: str):
        """Save an SOS line to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO sos_lines (
                game_id, move_number, start_row, start_col, end_row, end_col, player
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (game_id, move_number, start_pos[0], start_pos[1], 
              end_pos[0], end_pos[1], player))

        conn.commit()
        conn.close()

    def get_game_sos_lines(self, game_id: int) -> List[Dict]:
        """Get all SOS lines for a specific game"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT move_number, start_row, start_col, end_row, end_col, player
            FROM sos_lines
            WHERE game_id = ?
            ORDER BY move_number
        ''', (game_id,))

        sos_lines = []
        for row in cursor.fetchall():
            sos_lines.append({
                'move_number': row[0],
                'start_pos': [row[1], row[2]],
                'end_pos': [row[3], row[4]],
                'player': row[5]
            })

        conn.close()
        return sos_lines 
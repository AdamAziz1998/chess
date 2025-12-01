import psycopg2
from psycopg2.extras import RealDictCursor, execute_values

DB_SETTINGS = {
    "dbname": "chessdb",
    "user": "adamAziz",
    "password": "PACIFICPUNCH1998!",
    "host": "localhost",
    "port": "5432"
}

class Database:
    def __init__(self, settings=DB_SETTINGS):
        self.conn = psycopg2.connect(**settings)
        self.conn.autocommit = False  # manual commit for batching
        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)
        self.fen_cache = {}  # in-memory cache {fen: id}

    def close(self):
        self.cur.close()
        self.conn.close()

    # ------------------------
    # Schema setup
    # ------------------------
    def create_tables(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS Position (
                id SERIAL PRIMARY KEY,
                fen_position TEXT UNIQUE NOT NULL
            );
        """)

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS Move (
                id SERIAL PRIMARY KEY,
                fen_id INT REFERENCES Position(id) ON DELETE CASCADE,
                new_fen_id INT REFERENCES Position(id) ON DELETE CASCADE,
                move TEXT NOT NULL,
                white INT DEFAULT 0,
                black INT DEFAULT 0,
                draw INT DEFAULT 0,
                UNIQUE(fen_id, new_fen_id)
            );
        """)
        self.conn.commit()
        print("✅ Tables created successfully.")

    # ------------------------
    # Position handling
    # ------------------------
    def get_position_id(self, fen: str):
        """Return ID for a FEN (insert if missing). Uses cache + upsert."""
        if fen in self.fen_cache:
            return self.fen_cache[fen]

        self.cur.execute("""
            INSERT INTO Position (fen_position)
            VALUES (%s)
            ON CONFLICT (fen_position) DO NOTHING
            RETURNING id;
        """, (fen,))
        row = self.cur.fetchone()

        if row:
            pos_id = row["id"]
        else:
            self.cur.execute("SELECT id FROM Position WHERE fen_position = %s;", (fen,))
            pos_id = self.cur.fetchone()["id"]

        self.fen_cache[fen] = pos_id
        return pos_id

    def get_position_by_id(self, pos_id: int):
        self.cur.execute("SELECT * FROM Position WHERE id = %s;", (pos_id,))
        return self.cur.fetchone()

    def get_position_by_fen(self, fen: str):
        self.cur.execute("SELECT * FROM Position WHERE fen_position = %s;", (fen,))
        return self.cur.fetchone()

    def delete_position(self, pos_id: int):
        self.cur.execute("DELETE FROM Position WHERE id = %s;", (pos_id,))
        self.conn.commit()

    # ------------------------
    # Move handling
    # ------------------------
    def insert_move(self, fen_id: int, new_fen_id: int, move: str, white=0, black=0, draw=0):
        """Insert or update a move with outcome counts (atomic upsert)."""
        self.cur.execute("""
            INSERT INTO Move (fen_id, new_fen_id, move, white, black, draw)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (fen_id, new_fen_id) DO UPDATE
            SET white = Move.white + EXCLUDED.white,
                black = Move.black + EXCLUDED.black,
                draw  = Move.draw + EXCLUDED.draw
            RETURNING id;
        """, (fen_id, new_fen_id, move, white, black, draw))
        return self.cur.fetchone()["id"]

    def insert_moves_batch(self, moves: list[tuple]):
        """
        Bulk insert moves:
        moves = [(fen_id, new_fen_id, move, white, black, draw), ...]
        """
        execute_values(
            self.cur,
            """
            INSERT INTO Move (fen_id, new_fen_id, move, white, black, draw)
            VALUES %s
            ON CONFLICT (fen_id, new_fen_id) DO UPDATE
            SET white = Move.white + EXCLUDED.white,
                black = Move.black + EXCLUDED.black,
                draw  = Move.draw + EXCLUDED.draw
            """,
            moves
        )

    def get_moves_by_position(self, fen_id: int):
        self.cur.execute("SELECT * FROM Move WHERE fen_id = %s;", (fen_id,))
        return self.cur.fetchall()

    def get_move_by_fens(self, fen_id: int, new_fen_id: int):
        self.cur.execute("SELECT * FROM Move WHERE fen_id = %s AND new_fen_id = %s;", (fen_id, new_fen_id))
        return self.cur.fetchone()

    def get_moves_stats_by_fen(self, fen: str):
        self.cur.execute("""
            SELECT 
                m.move,
                (SUM(m.white) + SUM(m.black) + SUM(m.draw)) AS times_played,
                SUM(m.white) AS total_white_wins,
                SUM(m.black) AS total_black_wins,
                SUM(m.draw)  AS total_draws
            FROM Move m
            JOIN Position p ON p.id = m.fen_id
            WHERE p.fen_position = %s
            GROUP BY m.move
            ORDER BY times_played DESC;
        """, (fen,))
        return self.cur.fetchall()
    
    def get_most_popular_move(self, fen: str):
        """
        Returns the full data row for the most popular move
        from a given FEN position using a LIMIT 1 query.
        """
        self.cur.execute("""
            SELECT 
                m.move,
                (SUM(m.white) + SUM(m.black) + SUM(m.draw)) AS times_played,
                SUM(m.white) AS total_white_wins,
                SUM(m.black) AS total_black_wins,
                SUM(m.draw)  AS total_draws
            FROM Move m
            JOIN Position p ON p.id = m.fen_id
            WHERE p.fen_position = %s
            GROUP BY m.move
            ORDER BY times_played DESC
            LIMIT 1;
        """, (fen,))
        
        # fetchone() returns the single row or None if no rows were found
        return self.cur.fetchone()

    def delete_move(self, move_id: int):
        self.cur.execute("DELETE FROM Move WHERE id = %s;", (move_id,))
        self.conn.commit()

    # ------------------------
    # Commit control
    # ------------------------
    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type:
            self.conn.rollback()
        else:
            self.conn.commit()
        self.close()

import sqlite3

DB_FILE = "music.db"


def make_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Tracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            track_name TEXT NOT NULL,
            artist TEXT NOT NULL,
            image_path TEXT NOT NULL,
            year TEXT NOT NULL,
            genre TEXT NOT NULL,
            review_path TEXT NOT NULL
        )
    """)

    # DEV ONLY: reset table so reseeding doesn't duplicate data
    cursor.execute("DELETE FROM Tracks")

    conn.commit()
    conn.close()


def add_tracks(tracks):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.executemany("""
        INSERT INTO Tracks
        (track_name, artist, image_path, year, genre, review_path)
        VALUES (?, ?, ?, ?, ?, ?)
    """, tracks)

    conn.commit()
    conn.close()


def make_comments_table():
    """
    Create the Comments table if it doesn't exist.
    Stores: track_id, username, comment, timestamp
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            track_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            comment TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(track_id) REFERENCES Tracks(id)
        )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    make_db()
    make_comments_table()

    tracks = [
        (
            "Canvas",
            "jdrly",
            "images/jdrly_canvas.jpg",
            "2025",
            "Cloud rap / UK rap",
            "reviews/canvas.md"
        ),
        (
            "ZSL Freestyle",
            "Zino Vinci",
            "images/zino_vinci_ZSL.jpg",
            "2025",
            "UK rap / Sample rap",
            "reviews/zsl-freestyle.md"
        ),
        (
            "Brazil",
            "Death To Ricky",
            "images/thrice_dtr.jpg",
            "2025",
            "Quote: \"I'm on my own wave\"",
            "reviews/brazil.md"
        ),
        (
            "The Boy Who Cried Terrified",
            "Fakemink",
            "images/The_Boy_Who_Cried_Terrified.jpeg",
            "2025",
            "Jerk/Uk/Cloud",
            "reviews/The_Boy_Who_Cried_Terrified.md"
        )
    ]

    add_tracks(tracks)
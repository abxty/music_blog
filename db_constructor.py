import os
import sqlite3
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "music.db") 


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
            review_path TEXT NOT NULL,
            local_playback Text NOT NULL
        )
    """)
 
    conn.commit()
    conn.close()

tracks = [
    (
        "Canvas",
        "jdrly",
        "images/jdrly_canvas.jpg",
        "2025",
        "Cloud rap / UK rap",
        "reviews/canvas.md",
        "audio_files/canvas.mp3"
    ),
    (
        "ZSL Freestyle",
        "Zino Vinci",
        "images/zino_vinci_ZSL.jpg",
        "2025",
        "UK rap / Sample rap",
        "reviews/zsl-freestyle.md",
        "audio_files/YSL_Freestyle.mp3"
    ),
    (
        "Brazil",
        "Death To Ricky",
        "images/thrice_dtr.jpg",
        "2025",
        "Quote: \"I'm on my own wave\"",
        "reviews/brazil.md",
        "audio_files/brazil.mp3"

    ),
    (
        "The Boy Who Cried Terrified",
        "Fakemink",
        "images/The_Boy_Who_Cried_Terrified.jpeg",
        "2026",
        "Jerk/Uk/Cloud",
        "reviews/The_Boy_Who_Cried_Terrified.md",
        "audio_files/TBWCT.mp3"
    ),
    (
        "Stick around",
        "Saam Sultan",
        "images/Stick_Around.jpeg",
        "2025",
        "UK/Cloud",
        "reviews/stick_around.md",
        "audio_files/stick_around.mp3"

    ),
    (
        "Shoebox",
        "Niko B / Killthissonny",
        "images/Shoebox.jpeg",
        "2025",
        "Uk / Alt Rap / Cloud / Jerk",
        "reviews/shoebox.md",
        "audio_files/shoebox.mp3"
    )
]


def seed_tracks():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Only seed if empty
    cursor.execute("SELECT COUNT(*) FROM Tracks")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.executemany("""
            INSERT INTO Tracks
            (track_name, artist, image_path, year, genre, review_path, local_playback)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, tracks)

    conn.commit()
    conn.close()
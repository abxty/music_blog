import sqlite3
import markdown
import os
import uuid
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from db_constructor import make_db, seed_tracks
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, "supabase.env"))
print("DATABASE_URL:", os.environ.get("DATABASE_URL", "NOT FOUND"))

app = Flask(__name__)
app.secret_key = os.urandom(24)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "music.db")


# ── SQLite (local tracks) ──────────────────────────────────────────────────────

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ── Supabase / Postgres (community ratings) ───────────────────────────────────

def get_pg_connection():
    return psycopg2.connect(os.environ["DATABASE_URL"])


# ── Startup ───────────────────────────────────────────────────────────────────

make_db()
seed_tracks()


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def homepage():
    conn = get_db_connection()
    track = conn.execute(
        "SELECT * FROM Tracks ORDER BY id DESC LIMIT 1"
    ).fetchone()
    conn.close()
    return render_template("homepage.html", track=track)


@app.route("/blogs")
def blogs():
    conn = get_db_connection()
    tracks = conn.execute(
        "SELECT * FROM Tracks ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return render_template("blogs.html", tracks=tracks)


@app.route("/review/<int:track_id>")
def review(track_id):
    # Assign a session ID to this visitor if they don't have one
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())

    conn = get_db_connection()
    track = conn.execute(
        "SELECT * FROM Tracks WHERE id = ?", (track_id,)
    ).fetchone()
    conn.close()

    if not track:
        return "Review not found", 404

    # Read and render markdown
    review_path = os.path.join(BASE_DIR, track["review_path"])
    with open(review_path, "r", encoding="utf-8") as f:
        review_md = f.read()
    review_html = markdown.markdown(review_md, extensions=["extra", "nl2br"])

    # Fetch community rating from Supabase
    pg = get_pg_connection()
    cur = pg.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        "SELECT ROUND(AVG(score)::numeric, 1) as avg_score, COUNT(*) as total FROM ratings WHERE track_id = %s",
        (track_id,)
    )
    rating_data = cur.fetchone()

    # Check if this visitor has already rated
    cur.execute(
        "SELECT score FROM ratings WHERE track_id = %s AND session_id = %s",
        (track_id, session["session_id"])
    )
    existing = cur.fetchone()
    cur.close()
    pg.close()

    user_rating = existing["score"] if existing else None
    avg_score = float(rating_data["avg_score"]) if rating_data["avg_score"] else None
    total_votes = rating_data["total"]

    return render_template(
        "review.html",
        track=track,
        review_html=review_html,
        avg_score=avg_score,
        total_votes=total_votes,
        user_rating=user_rating
    )


@app.route("/review/<int:track_id>/rate", methods=["POST"])
def rate_track(track_id):
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())

    data = request.get_json()
    score = data.get("score")

    # Validate
    if not isinstance(score, int) or not (1 <= score <= 10):
        return jsonify({"error": "Invalid score"}), 400

    pg = get_pg_connection()
    cur = pg.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Upsert — insert or update if they've rated before
    cur.execute("""
        INSERT INTO ratings (track_id, session_id, score)
        VALUES (%s, %s, %s)
        ON CONFLICT (track_id, session_id)
        DO UPDATE SET score = EXCLUDED.score, timestamp = NOW()
    """, (track_id, session["session_id"], score))

    pg.commit()

    # Return updated average
    cur.execute(
        "SELECT ROUND(AVG(score)::numeric, 1) as avg_score, COUNT(*) as total FROM ratings WHERE track_id = %s",
        (track_id,)
    )
    result = cur.fetchone()
    cur.close()
    pg.close()

    return jsonify({
        "avg_score": float(result["avg_score"]),
        "total_votes": result["total"]
    })


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)
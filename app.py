import sqlite3
import markdown
import os
from db_constructor import make_db, make_comments_table, add_tracks
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "music.db")


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Ensure database exists
if not os.path.exists("music.db"):
    make_db()
    make_comments_table()


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


@app.route("/review/<int:track_id>", methods=["GET", "POST"])
def review(track_id):
    conn = get_db_connection()
    track = conn.execute(
        "SELECT * FROM Tracks WHERE id = ?", (track_id,)
    ).fetchone()

    if not track:
        conn.close()
        return "Review not found", 404

    # Handle new comment submission
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        comment = request.form.get("comment", "").strip()

        if username and comment:
            conn.execute(
                "INSERT INTO Comments (track_id, username, comment) VALUES (?, ?, ?)",
                (track_id, username, comment)
            )
            conn.commit()
        return redirect(url_for("review", track_id=track_id))

    # Fetch existing comments
    comments = conn.execute(
        "SELECT username, comment, timestamp FROM Comments WHERE track_id = ? ORDER BY timestamp DESC",
        (track_id,)
    ).fetchall()

    conn.close()

    # Read markdown review file
    review_path = os.path.join(BASE_DIR, track["review_path"])
    with open(review_path, "r", encoding="utf-8") as f:
        review_md = f.read()

    review_html = markdown.markdown(review_md, extensions=["extra", "nl2br"])

    return render_template(
        "review.html",
        track=track,
        review_html=review_html,
        comments=comments
    )


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)
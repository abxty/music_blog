import sqlite3
import markdown
import os
from dbconstructor import make_db, add_tracks
from flask import Flask, render_template

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "music.db")

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def homepage():
    conn = get_db_connection()
    tracks = conn.execute(
        "SELECT * FROM Tracks ORDER BY id DESC LIMIT 3"
    ).fetchall()
    conn.close()
    return render_template("homepage.html", tracks=tracks)


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
    conn = get_db_connection()
    track = conn.execute(
        "SELECT * FROM Tracks WHERE id = ?",
        (track_id,)
    ).fetchone()
    conn.close()

    if not track:
        return "Review not found", 404

    review_path = os.path.join(BASE_DIR, track["review_path"])

    with open(review_path, "r", encoding="utf-8") as f:
        review_md = f.read()

    review_html = markdown.markdown(review_md)

    return render_template(
        "review.html",
        track=track,
        review_html=review_html
    )


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)
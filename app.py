from flask import Flask, request, jsonify, render_template
import sqlite3
import random
import uuid

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect("puzzles.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS puzzles (
                id TEXT PRIMARY KEY,
                title TEXT,
                creator TEXT,
                categories TEXT
            )
        """)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        data = request.json
        puzzle_id = str(uuid.uuid4())
        title = data.get("title", "Untitled Puzzle")
        creator = data.get("creator", "Anonymous")
        categories = {cat["title"]: cat["words"] for cat in data["categories"]}
        
        with get_db_connection() as conn:
            conn.execute("INSERT INTO puzzles (id, title, creator, categories) VALUES (?, ?, ?, ?)",
                         (puzzle_id, title, creator, str(categories)))
        
        return jsonify({"puzzle_id": puzzle_id})
    
    return render_template("create.html")

@app.route("/play/<puzzle_id>", methods=["GET", "POST"])
def play(puzzle_id):
    with get_db_connection() as conn:
        puzzle = conn.execute("SELECT * FROM puzzles WHERE id = ?", (puzzle_id,)).fetchone()
        
    if not puzzle:
        return "Puzzle not found", 404
    
    categories = eval(puzzle["categories"])
    words = sum(categories.values(), [])  # Flatten list
    random.shuffle(words)
    
    if request.method == "POST":
        data = request.json
        guess = data.get("guess", [])
        
        if len(guess) != 4:
            return jsonify({"message": "Select exactly 4 words."})
        
        for category, words_set in categories.items():
            if set(guess) == set(words_set):
                return jsonify({"message": f"Correct! Category: {category}", "correct": True})
            
            for word in guess:
                remaining = set(guess) - {word}
                if remaining.issubset(set(words_set)):
                    return jsonify({"message": "You're one word away!", "correct": False})
        
        return jsonify({"message": "Incorrect. Try again.", "correct": False})
    
    return render_template("play.html", puzzle_id=puzzle_id, words=words)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
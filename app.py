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

@app.route('/play/puzzle_id>', methods=['GET', 'POST'])
def play():
    puzzle_id = request.args.get('puzzle_id')
    if not puzzle_id:
        return jsonify({"error": "Puzzle ID is required"}), 400

    conn = get_db_connection()
    puzzle = conn.execute("SELECT * FROM puzzles WHERE id = ?", (puzzle_id,)).fetchone()
    conn.close()

    if not puzzle:
        return jsonify({"error": "Puzzle not found"}), 404

    # Reconstruct categories
    categories = {
        "yellow": {"name": puzzle["category1_title"], "words": {puzzle["category1_word1"], puzzle["category1_word2"], puzzle["category1_word3"], puzzle["category1_word4"]}},
        "green": {"name": puzzle["category2_title"], "words": {puzzle["category2_word1"], puzzle["category2_word2"], puzzle["category2_word3"], puzzle["category2_word4"]}},
        "blue": {"name": puzzle["category3_title"], "words": {puzzle["category3_word1"], puzzle["category3_word2"], puzzle["category3_word3"], puzzle["category3_word4"]}},
        "purple": {"name": puzzle["category4_title"], "words": {puzzle["category4_word1"], puzzle["category4_word2"], puzzle["category4_word3"], puzzle["category4_word4"]}},
    }

    player_guesses = {}

    # Return puzzle data on GET request
    if request.method == 'GET':
        # Store player's guesses if not already present
        if puzzle_id not in player_guesses:
            player_guesses[puzzle_id] = set()

        # Collect all words and shuffle
        all_words = sum([list(cat["words"]) for cat in categories.values()], [])
        random.shuffle(all_words)

        return jsonify({
            "title": puzzle["title"],
            "author": puzzle["creator"],
            "words": all_words,
            "categories": categories
        })

    # Handle guess submission on POST request
    elif request.method == 'POST':
        data = request.get_json()
        selected_words = tuple(sorted(data.get("words")))  # Store sorted tuple to track guesses

        if not selected_words or len(selected_words) != 4:
            return jsonify({"error": "Invalid guess"}), 400

        # Check if the guess has already been made
        if selected_words in player_guesses[puzzle_id]:
            return jsonify({"error": "Repeated guess"}), 400

        player_guesses[puzzle_id].add(selected_words)  # Store guess

        for color, category in categories.items():
            if set(selected_words) == category["words"]:
                return jsonify({"correct": True, "category": {"name": category["name"], "color": color}})

        # Check if the guess is "one away" (3 correct, 1 wrong)
        for color, category in categories.items():
            if len(set(selected_words) & category["words"]) == 3:
                return jsonify({"correct": False, "one_away": True})

        return jsonify({"correct": False, "one_away": False})

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
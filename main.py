import flask
import sqlite3
from flask_limiter import Limiter
from better_profanity import profanity
from flask_limiter.util import get_remote_address

app = flask.Flask(
    __name__,
    static_folder="static",
    static_url_path="/"
)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day"],
    storage_uri="memory://",
)


conn = sqlite3.connect('sqlite.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS gifts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        gift TEXT NOT NULL
    )
''')
conn.commit()
conn.close()


@app.get("/")
@limiter.exempt
def index():
    return flask.send_from_directory("static", "index.html")


@app.post("/gifts")
@limiter.limit("1 per second")
def create_gift():
    data = flask.request.get_json()
    name = data.get('name')
    gift = data.get('gift')

    print(f"Received gift submission: name={name}, gift={gift}")
    print(
        f"Profanity prediction: {profanity.contains_profanity(name)} {profanity.contains_profanity(gift)}")

    if profanity.contains_profanity(name) or profanity.contains_profanity(gift):
        return flask.jsonify({'error': 'this seems offensive, quit it'}), 400

    conn = sqlite3.connect('sqlite.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO gifts (name, gift) VALUES (?, ?)', (name, gift))
    conn.commit()
    conn.close()

    return '', 201


@app.get("/gifts")
@limiter.limit("1 per second")
def get_gifts():
    conn = sqlite3.connect('sqlite.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, gift FROM gifts')
    rows = cursor.fetchall()
    conn.close()

    gifts = [{'id': row[0], 'name': row[1], 'gift': row[2]} for row in rows]
    return flask.jsonify(gifts)


if __name__ == "__main__":
    profanity.load_censor_words()
    app.run()

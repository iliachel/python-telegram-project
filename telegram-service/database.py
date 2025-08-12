import sqlite3

def get_db_connection():
    conn = sqlite3.connect('telegram.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY,
            username TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            username TEXT,
            text TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (chat_id) REFERENCES users (chat_id)
        )
    ''')
    conn.commit()
    conn.close()

def add_user(chat_id, username):
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (chat_id, username) VALUES (?, ?)', (chat_id, username))
        conn.commit()
    except sqlite3.IntegrityError:
        # User already exists
        pass
    finally:
        conn.close()

def add_message(chat_id, username, text):
    conn = get_db_connection()
    conn.execute('INSERT INTO messages (chat_id, username, text) VALUES (?, ?, ?)', (chat_id, username, text))
    conn.commit()
    conn.close()

def get_chat_history():
    conn = get_db_connection()
    messages = conn.execute('SELECT username, text FROM messages ORDER BY timestamp DESC LIMIT 50').fetchall()
    conn.close()
    return [dict(row) for row in messages]

def get_all_users():
    conn = get_db_connection()
    users = conn.execute('SELECT chat_id FROM users').fetchall()
    conn.close()
    return [row['chat_id'] for row in users]

create_tables()

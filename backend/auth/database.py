import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "data.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                age INTEGER,
                current_savings REAL,
                currency TEXT DEFAULT 'RUB',
                risk_level TEXT DEFAULT 'medium',
                investment_horizon TEXT,
                avatar BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)


def create_user(username: str, email: str, password_hash: str):
    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
        return True
    except sqlite3.IntegrityError:
        return False


def get_user_by_username(username: str):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, username, email, password_hash FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        return dict(row) if row else None


def get_user_by_email(email: str):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, username, email, password_hash FROM users WHERE email = ?",
            (email,)
        ).fetchone()
        return dict(row) if row else None


def update_user(user_id: int, username: str = None, email: str = None, password_hash: str = None):
    existing_user = get_user_by_username(username) if username else None
    existing_email = get_user_by_email(email) if email else None

    if existing_user and existing_user["id"] != user_id:
        raise ValueError("Username already exists.")
    if existing_email and existing_email["id"] != user_id:
        raise ValueError("Email already exists.")

    with get_connection() as conn:
        if username:
            conn.execute("UPDATE users SET username = ? WHERE id = ?", (username, user_id))
        if email:
            conn.execute("UPDATE users SET email = ? WHERE id = ?", (email, user_id))
        if password_hash:
            conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (password_hash, user_id))


def get_profile(user_id: int):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT age, current_savings, currency, risk_level, investment_horizon FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
        return dict(row) if row else None


def update_profile(user_id: int, age, current_savings, currency, risk_level, investment_horizon):
    with get_connection() as conn:
        conn.execute(
            """UPDATE users SET age=?, current_savings=?, currency=?, risk_level=?, investment_horizon=?
               WHERE id=?""",
            (age, current_savings, currency, risk_level, investment_horizon, user_id)
        )


def get_avatar(user_id: int):
    with get_connection() as conn:
        row = conn.execute("SELECT avatar FROM users WHERE id = ?", (user_id,)).fetchone()
        return bytes(row[0]) if row and row[0] else None


def update_avatar(user_id: int, avatar_bytes: bytes):
    with get_connection() as conn:
        conn.execute("UPDATE users SET avatar = ? WHERE id = ?", (avatar_bytes, user_id))


def save_message(user_id: int, role: str, content: str):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)",
            (user_id, role, content)
        )


def load_messages(user_id: int):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT role, content, created_at FROM messages WHERE user_id = ? ORDER BY created_at ASC",
            (user_id,)
        ).fetchall()
        return [dict(r) for r in rows]

import psycopg2
from psycopg2.errors import UniqueViolation
from auth.config import DB_CONFIG


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    age INTEGER,
                    current_savings DECIMAL(15, 2),
                    currency VARCHAR(3) DEFAULT 'RUB',
                    risk_level VARCHAR(10) DEFAULT 'medium',
                    investment_horizon VARCHAR(20),
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            # Add columns if they don't exist (for existing databases)
            migrations = [
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS age INTEGER",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS current_savings DECIMAL(15, 2)",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS currency VARCHAR(3) DEFAULT 'RUB'",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS risk_level VARCHAR(10) DEFAULT 'medium'",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS investment_horizon VARCHAR(20)",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar BYTEA",
            ]
            for migration in migrations:
                cur.execute(migration)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    role VARCHAR(10) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)


def create_user(username: str, email: str, password_hash: str):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                    (username, email, password_hash)
                )
        return True
    except UniqueViolation:
        return False


# Checks whether a username already exists in the database
def get_user_by_username(username: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, username, email, password_hash FROM users WHERE username = %s",
                (username,)
            )
            row = cur.fetchone()
            if row:
                return {"id": row[0], "username": row[1], "email": row[2], "password_hash": row[3]}
    return None

# Checks whether an email already exists in the database
def get_user_by_email(email: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, username, email, password_hash FROM users WHERE email = %s",
                (email,)
            )
            row = cur.fetchone()
            if row:
                return {"id": row[0], "username": row[1], "email": row[2], "password_hash": row[3]}
    return None


def update_user(user_id: int, username: str = None, email: str = None, password_hash: str = None):
    result = True
    existing_user = get_user_by_username(username) if username else None
    existing_email = get_user_by_email(email) if email else None

    if existing_user and existing_user["id"] != user_id:
        raise ValueError("Username already exists.")
    if existing_email and existing_email["id"] != user_id:
        raise ValueError("Email already exists.")   
    

    with get_connection() as conn:
        with conn.cursor() as cur:
            if username:
                cur.execute(
                    "UPDATE users SET username = %s WHERE id = %s",
                    (username, user_id)
                )
            if email:
                cur.execute(
                    "UPDATE users SET email = %s WHERE id = %s",
                    (email, user_id)
                )
            if password_hash:
                cur.execute(
                    "UPDATE users SET password_hash = %s WHERE id = %s",
                    (password_hash, user_id)
                )
    return result


def get_profile(user_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT age, current_savings, currency, risk_level, investment_horizon FROM users WHERE id = %s",
                (user_id,)
            )
            row = cur.fetchone()
            if row:
                return {
                    "age": row[0],
                    "current_savings": row[1],
                    "currency": row[2],
                    "risk_level": row[3],
                    "investment_horizon": row[4]
                }
    return None


def update_profile(user_id: int, age: int, current_savings: float, currency: str, risk_level: str, investment_horizon: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """UPDATE users 
                   SET age = %s, current_savings = %s, currency = %s, risk_level = %s, investment_horizon = %s
                   WHERE id = %s""",
                (age, current_savings, currency, risk_level, investment_horizon, user_id)
            )


def get_avatar(user_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT avatar FROM users WHERE id = %s", (user_id,))
            row = cur.fetchone()
            if row and row[0]:
                return bytes(row[0])
    return None


def update_avatar(user_id: int, avatar_bytes: bytes):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET avatar = %s WHERE id = %s",
                (psycopg2.Binary(avatar_bytes), user_id)
            )


def save_message(user_id: int, role: str, content: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO messages (user_id, role, content) VALUES (%s, %s, %s) RETURNING created_at",
                (user_id, role, content)
            )
            return cur.fetchone()[0]


def load_messages(user_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT role, content, created_at FROM messages WHERE user_id = %s ORDER BY created_at ASC",
                (user_id,)
            )
            return [{"role": row[0], "content": row[1], "created_at": row[2]} for row in cur.fetchall()]

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
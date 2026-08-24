import os # Library for interacting with the operating system
import psycopg2 # Library for connecting to PostgreSQL databases
from psycopg2.errors import UniqueViolation # Exception for handling unique constraint violations
from dotenv import load_dotenv # Library for loading environment variables from a .env file

# Load environment variables from a .env file
load_dotenv()

# Database configuration using environment variables with default values
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "fina_db"),
    "user": os.getenv("DB_USER", "fina_user"),
    "password": os.getenv("DB_PASSWORD", "fina_password"),
}


# Function to establish a connection to the PostgreSQL database
def get_connection():
    return psycopg2.connect(**DB_CONFIG)


# Function to initialize the database by creating necessary tables if they don't exist
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
                    avatar BYTEA,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    role VARCHAR(10) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)


# Function to create a new user in the database
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


# Function to retrieve a user from the database by their username
def get_user_by_username(username: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, username, email, password_hash FROM users WHERE username = %s",
                (username,)
            )
            row = cur.fetchone()
            return {"id": row[0], "username": row[1], "email": row[2], "password_hash": row[3]} if row else None


# Function to retrieve a user from the database by their email
def get_user_by_email(email: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, username, email, password_hash FROM users WHERE email = %s",
                (email,)
            )
            row = cur.fetchone()
            return {"id": row[0], "username": row[1], "email": row[2], "password_hash": row[3]} if row else None


# Function to update user information in the database
def update_user(user_id: int, username: str = None, email: str = None, password_hash: str = None):
    existing_user = get_user_by_username(username) if username else None
    existing_email = get_user_by_email(email) if email else None

    if existing_user and existing_user["id"] != user_id:
        raise ValueError("Username already exists.")
    if existing_email and existing_email["id"] != user_id:
        raise ValueError("Email already exists.")

    with get_connection() as conn:
        with conn.cursor() as cur:
            if username:
                cur.execute("UPDATE users SET username = %s WHERE id = %s", (username, user_id))
            if email:
                cur.execute("UPDATE users SET email = %s WHERE id = %s", (email, user_id))
            if password_hash:
                cur.execute("UPDATE users SET password_hash = %s WHERE id = %s", (password_hash, user_id))


# Function to retrieve a user's profile information from the database
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


# Function to update a user's profile information in the database
def update_profile(user_id: int, age, current_savings, currency, risk_level, investment_horizon):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """UPDATE users SET age=%s, current_savings=%s, currency=%s, risk_level=%s, investment_horizon=%s
                   WHERE id=%s""",
                (age, current_savings, currency, risk_level, investment_horizon, user_id)
            )


# Function to retrieve a user's avatar from the database
def get_avatar(user_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT avatar FROM users WHERE id = %s", (user_id,))
            row = cur.fetchone()
            return bytes(row[0]) if row and row[0] else None


# Function to update a user's avatar in the database
def update_avatar(user_id: int, avatar_bytes: bytes):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET avatar = %s WHERE id = %s",
                (psycopg2.Binary(avatar_bytes), user_id)
            )


# Function to save a message in the database
def save_message(user_id: int, role: str, content: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO messages (user_id, role, content) VALUES (%s, %s, %s)",
                (user_id, role, content)
            )


# Function to load messages for a user from the database
def load_messages(user_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT role, content, created_at FROM messages WHERE user_id = %s ORDER BY created_at ASC",
                (user_id,)
            )
            return [{"role": r[0], "content": r[1], "created_at": r[2]} for r in cur.fetchall()]

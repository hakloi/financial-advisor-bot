import os # Library for interacting with the operating system
from datetime import datetime
import psycopg2 # Library for connecting to PostgreSQL databases
from psycopg2.errors import UniqueViolation # Exception for handling unique constraint violations
from dotenv import load_dotenv # Library for loading environment variables from a .env file

# Load environment variables from a .env file
load_dotenv()


def resolve_db_config(host=None, port=None, dbname=None, user=None, password=None):
    """Return a DB config that works both inside Docker and when running on the host machine."""
    resolved_host = host if host is not None else os.getenv("DB_HOST", "localhost")
    resolved_port = port if port is not None else os.getenv("DB_PORT", "5432")
    resolved_dbname = dbname if dbname is not None else os.getenv("DB_NAME", "fina_db")
    resolved_user = user if user is not None else os.getenv("DB_USER", "fina_user")
    resolved_password = password if password is not None else os.getenv("DB_PASSWORD", "fina_password")

    if resolved_host == "db" and not os.path.exists("/proc/1/cgroup"):
        return {
            "host": "localhost",
            "port": "5433" if resolved_port == "5432" else resolved_port,
            "dbname": resolved_dbname,
            "user": resolved_user,
            "password": resolved_password,
        }

    return {
        "host": resolved_host,
        "port": resolved_port,
        "dbname": resolved_dbname,
        "user": resolved_user,
        "password": resolved_password,
    }


# Database configuration using environment variables with default values
DB_CONFIG = resolve_db_config()


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
                    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
                    confirmation_token_hash TEXT,
                    confirmation_token_expires_at TIMESTAMPTZ,
                    age INTEGER,
                    current_savings DECIMAL(15, 2),
                    currency VARCHAR(3) DEFAULT 'RUB',
                    risk_level VARCHAR(10) DEFAULT 'medium',
                    investment_horizon VARCHAR(20),
                    avatar BYTEA,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified BOOLEAN NOT NULL DEFAULT FALSE")
            cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS confirmation_token_hash TEXT")
            cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS confirmation_token_expires_at TIMESTAMPTZ")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    role VARCHAR(10) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    entry_date DATE NOT NULL,
                    kind VARCHAR(10) NOT NULL CHECK (kind IN ('income', 'expense')),
                    amount NUMERIC(15, 2) NOT NULL CHECK (amount > 0),
                    currency VARCHAR(3) NOT NULL DEFAULT 'RUB',
                    category VARCHAR(50),
                    description VARCHAR(200),
                    source_key VARCHAR(64),
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            # These ALTER statements keep installations created before the
            # transaction import feature compatible with the current schema.
            cur.execute("ALTER TABLE transactions ADD COLUMN IF NOT EXISTS currency VARCHAR(3) NOT NULL DEFAULT 'RUB'")
            cur.execute("ALTER TABLE transactions ADD COLUMN IF NOT EXISTS category VARCHAR(50)")
            cur.execute("ALTER TABLE transactions ADD COLUMN IF NOT EXISTS source_key VARCHAR(64)")
            cur.execute(
                """CREATE UNIQUE INDEX IF NOT EXISTS transactions_user_source_key_idx
                   ON transactions (user_id, source_key)
                   WHERE source_key IS NOT NULL"""
            )


# Function to create a new user in the database
def create_user(
    username: str,
    email: str,
    password_hash: str,
    confirmation_token_hash: str,
    confirmation_token_expires_at: datetime,
):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                          """INSERT INTO users
                              (username, email, password_hash, confirmation_token_hash, confirmation_token_expires_at)
                              VALUES (%s, %s, %s, %s, %s)""",
                          (username, email, password_hash, confirmation_token_hash, confirmation_token_expires_at)
                )
        return True
    except UniqueViolation:
        return False


# Function to retrieve a user from the database by their username
def get_user_by_username(username: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, username, email, password_hash, email_verified FROM users WHERE username = %s",
                (username,)
            )
            row = cur.fetchone()
            return {"id": row[0], "username": row[1], "email": row[2], "password_hash": row[3], "email_verified": row[4]} if row else None


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


def get_user_by_id(user_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, username, email, password_hash, email_verified FROM users WHERE id = %s",
                (user_id,)
            )
            row = cur.fetchone()
            return {"id": row[0], "username": row[1], "email": row[2], "password_hash": row[3], "email_verified": row[4]} if row else None


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
                """SELECT username, email, created_at, age, current_savings, currency,
                          risk_level, investment_horizon
                   FROM users WHERE id = %s""",
                (user_id,)
            )
            row = cur.fetchone()
            if row:
                return {
                    "username": row[0],
                    "email": row[1],
                    "created_at": row[2],
                    "age": row[3],
                    "current_savings": row[4],
                    "currency": row[5],
                    "risk_level": row[6],
                    "investment_horizon": row[7]
                }
    return None


def confirm_user_email(token_hash: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """UPDATE users
                   SET email_verified = TRUE,
                       confirmation_token_hash = NULL,
                       confirmation_token_expires_at = NULL
                   WHERE confirmation_token_hash = %s
                     AND confirmation_token_expires_at > NOW()
                   RETURNING id""",
                (token_hash,),
            )
            return cur.fetchone() is not None


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


def delete_avatar(user_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE users SET avatar = NULL WHERE id = %s", (user_id,))


# Function to save a message in the database
def save_message(user_id: int, role: str, content: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO messages (user_id, role, content) VALUES (%s, %s, %s) RETURNING id",
                (user_id, role, content)
            )
            return cur.fetchone()[0]


# Function to load messages for a user from the database
def load_messages(user_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, role, content, created_at FROM messages WHERE user_id = %s ORDER BY created_at ASC, id ASC",
                (user_id,)
            )
            return [{"id": r[0], "role": r[1], "content": r[2], "created_at": r[3]} for r in cur.fetchall()]


def delete_message(user_id: int, message_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM messages WHERE id = %s AND user_id = %s RETURNING id",
                (message_id, user_id),
            )
            return cur.fetchone() is not None


def create_transaction(
    user_id: int,
    entry_date,
    kind: str,
    amount: float,
    description: str | None,
    currency: str = "RUB",
    category: str | None = None,
):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO transactions
                   (user_id, entry_date, kind, amount, currency, category, description)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)
                   RETURNING id, entry_date, kind, amount, currency, category, description""",
                (user_id, entry_date, kind, amount, currency, category, description),
            )
            row = cur.fetchone()
            return {
                "id": row[0],
                "entry_date": row[1],
                "kind": row[2],
                "amount": float(row[3]),
                "currency": row[4],
                "category": row[5],
                "description": row[6],
            }


def update_transaction(
    user_id: int,
    transaction_id: int,
    entry_date,
    kind: str,
    amount: float,
    description: str | None,
    currency: str = "RUB",
    category: str | None = None,
):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """UPDATE transactions
                   SET entry_date = %s,
                       kind = %s,
                       amount = %s,
                       currency = %s,
                       category = %s,
                       description = %s
                   WHERE id = %s AND user_id = %s
                   RETURNING id, entry_date, kind, amount, currency, category, description""",
                (entry_date, kind, amount, currency, category, description, transaction_id, user_id),
            )
            row = cur.fetchone()
            if row is None:
                raise ValueError("Transaction not found")
            return {
                "id": row[0],
                "entry_date": row[1],
                "kind": row[2],
                "amount": float(row[3]),
                "currency": row[4],
                "category": row[5],
                "description": row[6],
            }


def delete_transaction(user_id: int, transaction_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM transactions WHERE id = %s AND user_id = %s RETURNING id",
                (transaction_id, user_id),
            )
            return cur.fetchone() is not None


def load_transactions(user_id: int, year: int, month: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT id, entry_date, kind, amount, currency, category, description
                   FROM transactions
                   WHERE user_id = %s AND EXTRACT(YEAR FROM entry_date) = %s
                     AND EXTRACT(MONTH FROM entry_date) = %s
                   ORDER BY entry_date, id""",
                (user_id, year, month),
            )
            return [
                {
                    "id": row[0],
                    "entry_date": row[1],
                    "kind": row[2],
                    "amount": float(row[3]),
                    "currency": row[4],
                    "category": row[5],
                    "description": row[6],
                }
                for row in cur.fetchall()
            ]

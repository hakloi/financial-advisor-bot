import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "advisor_db"),
    "user": os.getenv("DB_USER", "advisor_user"),
    "password": os.getenv("DB_PASSWORD", "advisor_pass"),
}

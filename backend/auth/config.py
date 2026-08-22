import os # Library for interacting with the operating system
from dotenv import load_dotenv # Library for loading environment variables from a .env file

load_dotenv() # Load environment variables from a .env file into the system's environment variables

# Database configuration dictionary that retrieves database connection parameters from environment variables, 
# with default values provided if the environment variables are not set
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "advisor_db"),
    "user": os.getenv("DB_USER", "advisor_user"),
    "password": os.getenv("DB_PASSWORD", "advisor_pass"),
}

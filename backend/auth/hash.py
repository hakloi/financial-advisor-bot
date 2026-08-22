import bcrypt # Library for password hashing and verification


# Function to hash a password using bcrypt, returning the hashed password as a string
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


# Function to verify a password against a hashed password using bcrypt, returning True if the password matches the hash, and False otherwise
def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

import os

class Config:
    DATABASE_PATH = os.getenv("DATABASE_PATH", "bank.db")
    DB_ENCRYPTION_KEY = os.getenv("DB_ENCRYPTION_KEY")

    if not DB_ENCRYPTION_KEY:
        raise RuntimeError("DB_ENCRYPTION_KEY environment variable is required")
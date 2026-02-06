import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def get_engine():
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASS")
    host = os.getenv("DB_HOST")
    db = os.getenv("DB_NAME")

    if not all([user, password, host, db]):
        raise ValueError("Database environment variables are not set")

    return create_engine(
        f"mysql+pymysql://{user}:{password}@{host}:3306/{db}"
    )

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------
# Persistent SQLite database path
# --------------------------------------------------
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./data/dfs_lite.db"
)

print("DATABASE_URL =", DATABASE_URL)

# --------------------------------------------------
# SQLite Engine
# --------------------------------------------------
if DATABASE_URL.startswith("sqlite"):

    engine = create_engine(
        DATABASE_URL,
        connect_args={
            "check_same_thread": False
        }
    )

else:

    engine = create_engine(DATABASE_URL)

# --------------------------------------------------
# Session Factory
# --------------------------------------------------
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# --------------------------------------------------
# Base Model
# --------------------------------------------------
Base = declarative_base()

# --------------------------------------------------
# Database Dependency
# --------------------------------------------------
def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()

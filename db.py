import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_BACKEND = os.getenv("DB_BACKEND", "sqlite")

if DB_BACKEND == "postgres":
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://user:pass@localhost/predictions"
    )
    connect_args = {}
else:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./invoices.db")
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

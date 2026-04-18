"""
Database configuration module.

This module sets up the SQLAlchemy engine, session factory, and base class
for ORM models. It also provides a database dependency used by FastAPI
endpoints to create and manage database sessions.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL for SQLite database stored in the project directory
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# SQLAlchemy engine responsible for managing connections to the database
# check_same_thread=False allows SQLite to be used with FastAPI's multithreading
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Session factory used to create database sessions for interacting with the DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models (tables will inherit from this class)
Base = declarative_base()

def get_db():
    """
    FastAPI dependency that provides a database session.

    A new SQLAlchemy session is created for each request.
    The session is yielded to the endpoint and automatically
    closed after the request is completed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
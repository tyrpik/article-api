"""
Database ORM models.

This module defines the SQLAlchemy models representing database tables.
Each class corresponds to a table in the database and describes its
columns and relationships with other tables.
"""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base

class User(Base):
    """
    User model representing the 'users' table in the database.

    Stores user authentication data and subscription status.
    A user can have multiple associated articles.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_subscribed = Column(Boolean, default=False)

    # Relationship to the Article model (one user can have many articles)
    articles = relationship("Article", back_populates="author")

class Article(Base):
    """
    Article model representing the 'articles' table in the database.

    Stores article content and metadata.
    Each article belongs to a single author (user).
    """

    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    author_id = Column(Integer, ForeignKey("users.id"))

    # Relationship to the User model (each article has one author)
    author = relationship("User", back_populates="articles")
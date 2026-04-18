"""
Pydantic schemas for request and response validation.

This module defines data structures used for API requests and responses.
Schemas ensure data validation, serialization, and control what is exposed
to the client from the database models.
"""

from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional

# --- User Schemas ---

class UserBase(BaseModel):
    """
    Base schema for user data.

    Contains fields shared across all user-related schemas.
    """

    email: EmailStr
    is_subscribed: bool = False

class UserCreate(UserBase):
    """
    Schema used when creating a new user.

    Extends UserBase by adding password field required for registration.
    """
    password: str

class UserResponse(UserBase):
    """
    Schema returned in API responses for user data.

    Excludes sensitive information like password.
    """
    id: int

    class Config:
        from_attributes = True  # Tells Pydantic to read data from ORM models

# --- Article Schemas ---

class ArticleBase(BaseModel):
    """
    Base schema for article data.

    Contains shared fields for article creation and responses.
    """
    title: str
    content: str

class ArticleCreate(ArticleBase):
    """
    Schema used when creating a new article.
    """
    pass

class ArticleUpdate(BaseModel):
    """
    Schema used for updating an article.

    All fields are optional to allow partial updates.
    """
    title: Optional[str] = None
    content: Optional[str] = None

class ArticleResponse(ArticleBase):
    """
    Schema returned in API responses for articles.

    Includes database-generated fields and relationships.
    """
    id: int
    created_at: datetime
    author_id: int

    model_config = ConfigDict(from_attributes=True)
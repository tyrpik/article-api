"""
This module contains functions responsible for interacting
with the database using SQLAlchemy ORM.

It implements CRUD (Create, Read, Update, Delete) operations
for users and articles.
"""

from sqlalchemy.orm import Session
from . import models, schemas
from .auth import get_password_hash

def get_user_by_email(db: Session, email: str):
    """
    Retrieve a user from the database by email.

    Args:
        db (Session): Active database session.
        email (str): Email address of the user.

    Returns:
        models.User | None: The user object if found, otherwise None.
    """

    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    """
    Create a new user in the database.

    The function hashes the user's password before saving it
    and stores the new user record in the database.

    Args:
        db (Session): Active database session.
        user (schemas.UserCreate): User data received from API request.

    Returns:
        models.User: The created user object.
    """

    hashed_password = get_password_hash(user.password)
    # Create DB model instance
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        is_subscribed=user.is_subscribed
    )
    db.add(db_user)
    db.commit()
    # Refresh the instance to load generated fields (e.g. id)
    db.refresh(db_user)
    return db_user

def get_article(db: Session, article_id: int):
    """
    Retrieve a single article by its ID.

    Args:
        db (Session): Active database session.
        article_id (int): ID of the article.

    Returns:
        models.Article | None: The article if found, otherwise None.
    """
    return db.query(models.Article).filter(models.Article.id == article_id).first()

def get_articles(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieve a list of articles with optional pagination.

    Args:
        db (Session): Active database session.
        skip (int): Number of records to skip.
        limit (int): Maximum number of articles to return.

    Returns:
        list[models.Article]: List of article objects.
    """
    return db.query(models.Article).offset(skip).limit(limit).all()

def create_article(db: Session, article: schemas.ArticleCreate, user_id: int):
    """
    Create a new article in the database.

    Args:
        db (Session): Active database session.
        article (schemas.ArticleCreate): Article data received from API request.
        user_id (int): ID of the user creating the article.

    Returns:
        models.Article: The created article object.
    """

    # Convert Pydantic schema to dictionary and add author ID
    db_article = models.Article(**article.model_dump(), author_id=user_id)
    # Save the article to the database
    db.add(db_article)
    db.commit()
    # Refresh to load generated fields (e.g. id, timestamps)
    db.refresh(db_article)

    return db_article

def update_article(db: Session, db_article: models.Article, article_update: schemas.ArticleUpdate):
    """
    Update an existing article.

    Only fields provided in the request will be updated.

    Args:
        db (Session): Active database session.
        db_article (models.Article): Existing article from the database.
        article_update (schemas.ArticleUpdate): Data to update.

    Returns:
        models.Article: Updated article object.
    """

    # Extract only fields that were actually provided in the request
    update_data = article_update.model_dump(exclude_unset=True)

    # Dynamically update fields on the SQLAlchemy model
    for key, value in update_data.items():
        setattr(db_article, key, value)

    db.commit()
    db.refresh(db_article)

    return db_article

def delete_article(db: Session, db_article: models.Article):
    """
    Delete an article from the database.

    Args:
        db (Session): Active database session.
        db_article (models.Article): Article instance to delete.

    Returns:
        bool: True if deletion was successful.
    """

    db.delete(db_article)
    db.commit()
    
    return True
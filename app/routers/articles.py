"""
API endpoints for article management.

This router provides endpoints for creating, retrieving,
updating, and deleting articles.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from .. import schemas, crud, models, auth, services
from ..database import get_db

router = APIRouter(prefix="/articles", tags=["Articles"])

@router.get("/", response_model=List[schemas.ArticleResponse])
def read_articles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of articles.

    Supports basic pagination using skip and limit parameters.

    Args:
        skip (int): Number of articles to skip.
        limit (int): Maximum number of articles to return.
        db (Session): Active database session.

    Returns:
        List[schemas.ArticleResponse]: List of articles.
    """
    articles = crud.get_articles(db, skip=skip, limit=limit)
    return articles

@router.get("/{article_id}", response_model=schemas.ArticleResponse)
def read_article(article_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single article by its ID.

    Args:
        article_id (int): ID of the article.
        db (Session): Active database session.

    Returns:
        schemas.ArticleResponse: The requested article.

    Raises:
        HTTPException: If the article does not exist.
    """
    
    db_article = crud.get_article(db, article_id=article_id)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return db_article

@router.post("/", response_model=schemas.ArticleResponse, status_code=status.HTTP_201_CREATED)
def create_article(
    article: schemas.ArticleCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Create a new article.

    The endpoint requires authentication. The created article will be associated 
    with the currently logged-in user.

    After successfully creating the article, a background task
    is triggered to notify all subscribed users about the new article.

    Args:
        article (schemas.ArticleCreate): Article data from request body.
        background_tasks (BackgroundTasks): FastAPI background tasks manager.
        db (Session): Active database session.
        current_user (models.User): Authenticated user obtained from JWT token.

    Returns:
        schemas.ArticleResponse: The created article.
    """

    new_article = crud.create_article(db=db, article=article, user_id=current_user.id)
    
    # Notify subscribers in the background after creating the article
    background_tasks.add_task(services.notify_subscribers, db, new_article.title)
    
    return new_article

@router.post("/import", status_code=status.HTTP_202_ACCEPTED)
def bulk_import_articles(
    articles: List[schemas.ArticleCreate],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Import multiple articles in bulk.

    Accepts a JSON list of articles and schedules the import to be processed asynchronously
    using a background task. This allows the API to respond immediately without blocking the
    request while potentially large datasets are inserted.

    Args:
        articles (List[schemas.ArticleCreate]): List of articles to import.
        background_tasks (BackgroundTasks): FastAPI background task manager.
        db (Session): Active database session.
        current_user (models.User): Authenticated user performing the import.

    Returns:
        dict: Confirmation message indicating that the import process has started.

    Status Codes:
        202 Accepted: The request has been accepted and the import is being processed
        asynchronously in the background.
    """
    background_tasks.add_task(services.process_bulk_import, db, articles, current_user.id)
    return {"message": "Import started in the background."}

@router.put("/{article_id}", response_model=schemas.ArticleResponse)
def update_article(
    article_id: int, 
    article_update: schemas.ArticleUpdate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Update an existing article.

    Only the author of the article is allowed to update it.

    Args:
        article_id (int): ID of the article to update.
        article_update (schemas.ArticleUpdate): Fields to update.
        db (Session): Active database session.
        current_user (models.User): Authenticated user.

    Returns:
        schemas.ArticleResponse: Updated article.

    Raises:
        HTTPException: If the article does not exist or user is not authorized.
    """

    db_article = crud.get_article(db, article_id=article_id)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    if db_article.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this article")
    
    return crud.update_article(db=db, db_article=db_article, article_update=article_update)

@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article(
    article_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Delete an article.

    Only the author of the article is allowed to delete it.

    Args:
        article_id (int): ID of the article to delete.
        db (Session): Active database session.
        current_user (models.User): Authenticated user.

    Raises:
        HTTPException: If the article does not exist or user is not authorized.
    """

    db_article = crud.get_article(db, article_id=article_id)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    if db_article.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this article")
    
    crud.delete_article(db=db, db_article=db_article)
    return None
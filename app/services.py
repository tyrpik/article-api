"""
Business logic services (Notifications and Import).
"""
import json
from sqlalchemy.orm import Session
from . import models, schemas, crud

def notify_subscribers(db: Session, article_title: str):
    """
    Simulates sending an email notification to all subscribed users.
    This should be run as a background task.
    """
    # Find all users where is_subscribed is True
    subscribers = db.query(models.User).filter(models.User.is_subscribed == True).all()
    
    for user in subscribers:
        # In a real app, you would use an email library like smtplib or SendGrid here
        print(f"[NOTIFICATION] Sending email to {user.email}: New article published -> '{article_title}'")


def process_bulk_import(db: Session, import_data: list[schemas.ArticleCreate], current_user_id: int):
    """
    Processes a list of articles and saves them to the database.
    """
    imported_count = 0
    for item in import_data:
        db_article = models.Article(
            title=item.title,
            content=item.content,
            author_id=current_user_id
        )
        db.add(db_article)
        imported_count += 1
    
    db.commit()
    print(f"[IMPORT] Successfully imported {imported_count} articles for user ID {current_user_id}")
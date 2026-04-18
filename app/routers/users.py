"""
User-related API endpoints.

This module provides routes for:
- user registration
- user authentication (JWT token generation)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import schemas, crud, models, auth
from ..database import get_db

# Router responsible for user-related operations
router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.

    Creates a new user account in the database if the email
    is not already registered.

    Args:
        user (schemas.UserCreate): User registration data
            including email, password, and subscription flag.
        db (Session): Database session provided by FastAPI dependency.

    Returns:
        schemas.UserResponse: The newly created user.

    Raises:
        HTTPException: If the email address is already registered.
    """

    db_user = crud.get_user_by_email(db, email=user.email)

    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    return crud.create_user(db=db, user=user)

@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate a user and generate a JWT access token.

    Uses OAuth2 password flow where the client sends credentials
    as form data (`username` and `password`). In this application,
    the `username` field represents the user's email address.

    Args:
        form_data (OAuth2PasswordRequestForm): Login form containing
            username (email) and password.
        db (Session): Database session provided by FastAPI dependency.

    Returns:
        dict: JWT access token and token type.

    Raises:
        HTTPException: If authentication fails.
    """

    # OAuth2 uses the field "username", which we interpret as email
    user = crud.get_user_by_email(db, email=form_data.username)

    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate JWT token containing the user ID
    access_token = auth.create_access_token(data={"sub": str(user.id)})
    
    return {"access_token": access_token, "token_type": "bearer"}
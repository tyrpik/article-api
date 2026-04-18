"""
Authentication and security module.

Provides utilities for:
- password hashing and verification using bcrypt
- JWT access token generation
- retrieving the currently authenticated user

This module is used by API endpoints to handle authentication
and protect routes that require a logged-in user.
"""

from datetime import datetime, timedelta, timezone
import bcrypt
from jose import jwt
import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional
from .database import get_db
from . import models

load_dotenv()

# Security configuration used for signing JWT tokens
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify whether a plain text password matches the stored hashed password.

    Args:
        plain_password (str): Password provided by the user during login.
        hashed_password (str): Hashed password stored in the database.

    Returns:
        bool: True if the password is correct, otherwise False.
    """

    password_byte_enc = plain_password.encode('utf-8')
    hashed_password_byte_enc = hashed_password.encode('utf-8')

    return bcrypt.checkpw(password_byte_enc, hashed_password_byte_enc)

def get_password_hash(password: str) -> str:
    """
    Hash a plain text password using bcrypt.

    Args:
        password (str): Plain text password.

    Returns:
        str: Securely hashed password.
    """

    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)

    return hashed_password.decode('utf-8')

def create_access_token(data: dict) -> str:
    """
    Generate a JWT access token.

    The token contains the provided payload data and an expiration timestamp.

    Args:
        data (dict): Data to encode in the token (e.g., user ID or email).

    Returns:
        str: Encoded JWT token.
    """

    # Copy the input data to avoid modifying the original dictionary
    to_encode = data.copy()

    # Ensure the token always contains a subject (user identifier)
    if "sub" not in to_encode:
        raise ValueError("Token payload must contain 'sub' field")
    
    # Set token expiration time
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Add expiration claim to the payload
    to_encode.update({"exp": expire})
    # Generate and sign the JWT token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

# OAuth2 scheme used by FastAPI to extract the Bearer token from requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    """
    Validate the JWT token and retrieve the current authenticated user.

    This dependency can be used in protected endpoints to ensure that
    the request contains a valid access token.

    Args:
        token (str): JWT token extracted from the Authorization header.
        db (Session): Database session.

    Returns:
        models.User: The authenticated user.

    Raises:
        HTTPException: If the token is invalid or the user does not exist.
    """

    # Exception returned when authentication fails
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Extract user ID from the token payload
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception
        
    # Retrieve the user from the database using the user ID from the token
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user
"""
Main entry point for the FastAPI application.

This module initializes the FastAPI app, creates database tables
based on ORM models, and defines basic API routes.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from . import models
from .database import engine
from .routers import users, articles

# Create database tables based on SQLAlchemy models in models.py
# This runs at application startup and ensures all tables exist
models.Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n" + "="*55)
    print("API IS RUNNING!")
    print("Swagger Documentation: http://localhost:8000/docs")
    print("="*55 + "\n")
    yield
    print("\nShutting down... Goodbye!\n")


# Initialize FastAPI application instance
app = FastAPI(
    title="Article API",
    description="A simple API for managing articles and users.",
    version="1.0.0"
)

# Connect router with user-related endpoints to the main application
app.include_router(users.router)
# Connect router with article-related endpoints to the main application
app.include_router(articles.router)

@app.get("/")
def read_root():
    """
    Root endpoint.

    Returns a simple welcome message and hints about API documentation.
    """
    return {"message": "Welcome to the Article API! Go to /docs to see the Swagger UI."}
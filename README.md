# Article API

Simple REST API built with FastAPI for managing users and articles.

## Features

- User registration & Authentication
- Password hashing
- JWT access tokens
- Article CRUD operations (Create, Read, Update, Delete)
- **Background Tasks:** Email notifications simulation for platform subscribers
- **Bulk Import:** Asynchronous bulk processing of articles via JSON import
- SQLAlchemy ORM with SQLite
- Pydantic V2 data validation

## Tech stack

- **FastAPI**
- **SQLAlchemy**
- **Pydantic**
- **JWT** (`python-jose`)
- **Bcrypt** (direct implementation)
- **SQLite**

## Installation

Clone the repository:

git clone https://github.com/yourname/article_api.git
cd article_api

Create a virtual environment and install dependencies:

python -m venv venv
source venv/bin/activate # On Windows use: venv\Scripts\activate
pip install -r requirements.txt

Create `.env` file in the root directory:

SECRET_KEY=your-secret-key

Run the server locally:

uvicorn app.main:app --reload

## Running with Docker

To run the application inside a Docker container, simply use:

docker-compose up --build

Note: If the terminal output says Uvicorn running on http://0.0.0.0:8000, please use localhost or 127.0.0.1 in your browser

## API Documentation

Once the server is running, interactive API documentation (Swagger UI) will be available at:
http://localhost:8000/docs

## Security Note (Secure Channel Requirement)

To fulfill the "Focus on simplicity rather than overengineering" guideline, this application runs over standard HTTP for local development and Docker evaluation.

To satisfy the "secure channel" requirement in a production environment, this API should be placed behind a reverse proxy (like Nginx or Traefik) configured with TLS/SSL certificates (e.g., Let's Encrypt) to ensure all communications occur strictly over HTTPS. Password hashing (bcrypt) and JWT authorization have already been implemented at the application level.

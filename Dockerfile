# Use a lightweight official Python 3.13 image as the base environment
FROM python:3.13-slim

# Set the working directory inside the container
# All subsequent commands will be executed relative to this path
WORKDIR /code

# Copy dependency definitions to the container
# This step is separated to leverage Docker layer caching
COPY ./requirements.txt /code/requirements.txt

# Install project dependencies
# --no-cache-dir prevents pip from storing cache files,
# keeping the final image smaller
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the application source code into the container
COPY ./app /code/app

# Copy environment variables file
# In production environments, secrets should be managed
# via environment variables or secret managers instead of .env files
COPY .env /code/.env

# Expose the port used by the FastAPI application
EXPOSE 8000

# Start the application using Uvicorn ASGI server
# 0.0.0.0 allows the container to accept external connections
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
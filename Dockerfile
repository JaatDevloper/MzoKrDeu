# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
# Since we are using uv/pyproject.toml in Replit, let's create a requirements.txt for Docker
COPY pyproject.toml .
RUN pip install --no-cache-dir python-telegram-bot telethon flask

# Copy the rest of the application code
COPY main.py .

# Command to run the bot
CMD ["python", "main.py"]

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 8000
EXPOSE 8000

# Set environment variables
ENV DATABASE_URL=sqlite:////app/database.db

# Run the seeding script to populate SQLite, then start the FastAPI application
CMD ["sh", "-c", "python app/agents/pipeline.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]

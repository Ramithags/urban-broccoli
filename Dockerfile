# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HOME=/home/appuser

# Create a non-root user and set permissions
RUN useradd -m appuser
WORKDIR $HOME

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Pre-download models to make the container ready-to-run
# This downloads all-MiniLM-L6-v2 and Phi-2 during build
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')" && \
    python -c "from transformers import AutoTokenizer, AutoModelForCausalLM; AutoTokenizer.from_pretrained('microsoft/phi-2'); AutoModelForCausalLM.from_pretrained('microsoft/phi-2')"

# Create directory for ChromaDB and set permissions
RUN mkdir -p .chromadb && chown -R appuser:appuser .chromadb

# Switch to non-root user
USER appuser

# Expose the port the app runs on
EXPOSE 8000

# Healthcheck to ensure the container is healthy
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

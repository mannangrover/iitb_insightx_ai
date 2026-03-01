# Build stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    git-lfs \
    && rm -rf /var/lib/apt/lists/*

# Install Git LFS
RUN git lfs install

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Pull LFS files
RUN git lfs pull || true

# Expose API port (Railway injects PORT at runtime)
EXPOSE 8000

# Start FastAPI only; main.py already respects PORT env var on Railway
CMD ["python", "main.py"]

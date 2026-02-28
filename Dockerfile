# Build stage
FROM python:3.12-slim

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

# Expose ports
EXPOSE 8000 8501

# Create entrypoint script that runs both services
RUN echo '#!/bin/bash\n\
# Start FastAPI in background\n\
uvicorn main:app --host 0.0.0.0 --port 8000 &\n\
\n\
# Start Streamlit in foreground\n\
streamlit run app.py --server.port=8501 --server.address=0.0.0.0' > /app/entrypoint.sh && \
chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]

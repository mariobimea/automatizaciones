FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for vector store (will use Railway volume if available)
RUN mkdir -p /data/chroma_db

# Expose port (Railway will set $PORT dynamically)
EXPOSE 8000

# Run application (use shell form to expand $PORT)
CMD uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8000}

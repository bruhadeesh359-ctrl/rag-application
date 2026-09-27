FROM python:3.12-slim

WORKDIR /app

# Install system dependencies required for compilation and running
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install poetry or use pip directly. We use pip for simplicity.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Copy application code
COPY ./app /app/app

# Set PYTHONPATH and DATA_DIR
ENV PYTHONPATH=/app
ENV DATA_DIR=/app/data
ENV HF_HOME=/app/data/.cache

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Expose the FastAPI port
EXPOSE 8000

# Run the backend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

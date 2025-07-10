# AI Medical Billing System Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    tesseract-ocr \
    tesseract-ocr-eng \
    libsm6 \
    libxext6 \
    libfontconfig1 \
    libxrender1 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgssapi-krb5-2 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash medical && \
    chown -R medical:medical /app
USER medical

# Install Python dependencies
COPY --chown=medical:medical requirements.txt .
RUN pip install --user -r requirements.txt

# Copy application code
COPY --chown=medical:medical . .

# Create necessary directories
RUN mkdir -p logs uploads data chroma_db

# Set PATH to include user packages
ENV PATH="/home/medical/.local/bin:$PATH"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["python", "-m", "app.main"] 
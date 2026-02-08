# ================================================================
# EaseEmail Notifications - Production Dockerfile
# Multi-stage build for minimal runtime footprint
# ================================================================

# ----------------------------------------------------------------
# STAGE 1: Builder
# Install build dependencies and compile Python packages
# ----------------------------------------------------------------
FROM python:3.11-slim AS builder

# Build-time dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Install Python dependencies into a virtual environment
# This allows clean copy to runtime stage
COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ----------------------------------------------------------------
# STAGE 2: Runtime
# Minimal image with only runtime dependencies
# ----------------------------------------------------------------
FROM python:3.11-slim AS runtime

# Runtime-only system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Security: Create non-root user
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Python optimization flags
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Create required directories with correct ownership
RUN mkdir -p /app/logs /app/static && \
    chown -R appuser:appgroup /app

# Copy application code
COPY --chown=appuser:appgroup . /app/

# Copy and prepare entrypoint
COPY --chown=appuser:appgroup docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Switch to non-root user
USER appuser

# Expose API port
EXPOSE 8000

# Health check (overridden per service in compose)
HEALTHCHECK --interval=30s --timeout=10s --start-period=45s --retries=3 \
    CMD curl -f http://localhost:8000/health/live || exit 1

# Entrypoint handles migrations and role detection
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Default command (API server)
# Workers override this in docker-compose.yml
CMD ["gunicorn", "app.main:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "2", \
     "--threads", "1", \
     "--timeout", "120", \
     "--graceful-timeout", "30", \
     "--keep-alive", "5", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "100", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info"]

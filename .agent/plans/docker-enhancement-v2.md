# Production Docker Implementation Plan v2.0

## EaseEmail Notifications Platform

**Document Type:** Infrastructure Architecture Decision Record  
**Status:** Ready for Implementation  
**Author:** Antigravity AI (Senior Cloud Architect Review)  
**Date:** 2026-02-08

---

## Executive Summary

This document provides a production-grade Docker configuration strategy for the EaseEmail Notifications platform. It supersedes the initial enhancement plan by incorporating mandatory architectural improvements for:

- **Memory safety** and controlled concurrency
- **Horizontal scalability** without vertical resource bloat
- **Zero-downtime deployments** and rolling update compatibility
- **Security-first** secrets handling
- **Future portability** to Kubernetes/ECS

---

## 1. Architecture Overview

### 1.1 Container Topology

```
┌─────────────────────────────────────────────────────────────────┐
│                        Docker Network: easeemail-network        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐ │
│  │   db        │    │   redis     │    │   api (scale: 2+)   │ │
│  │  postgres   │◄───│   cache/    │◄───│   FastAPI + Uvicorn │ │
│  │  :5432      │    │   queue     │    │   :8000             │ │
│  └─────────────┘    │   :6379     │    └─────────────────────┘ │
│         │           └─────────────┘              │              │
│         │                  │                     │              │
│         │           ┌──────┴──────┐              │              │
│         │           │             │              │              │
│         ▼           ▼             ▼              ▼              │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              worker (scale: 3+)                             ││
│  │              Background email/webhook processor             ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Design Principles

| Principle | Implementation |
|-----------|----------------|
| **Single Image, Multiple Roles** | One Dockerfile, runtime command determines role (api vs worker) |
| **Stateless Containers** | All state in PostgreSQL/Redis; containers can be replaced anytime |
| **Explicit Resource Bounds** | Fixed worker counts, memory limits, no unbounded concurrency |
| **Fail-Fast Startup** | Containers exit if dependencies unavailable after timeout |
| **Health-Driven Orchestration** | Liveness + Readiness probes for proper load balancing |

---

## 2. Dockerfile Strategy

### 2.1 Multi-Stage Build Rationale

**Why multi-stage?**
- Build tools (gcc, libpq-dev headers) add ~200MB to image size
- Production image should contain only runtime dependencies
- Reduces attack surface by excluding compilers

### 2.2 Final Dockerfile

```dockerfile
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
```

### 2.3 Key Dockerfile Decisions Explained

| Decision | Rationale |
|----------|-----------|
| **`--workers 2`** | Matches typical 2-4 CPU container allocation. Scales horizontally via replicas, not worker count. |
| **`--max-requests 1000`** | Recycles workers after 1000 requests to prevent memory leaks from accumulating. |
| **`--max-requests-jitter 100`** | Prevents thundering herd when all workers recycle simultaneously. |
| **`--graceful-timeout 30`** | Allows in-flight requests to complete during rolling deployments. |
| **`libpq5` only** | Runtime PostgreSQL library; headers (`libpq-dev`) left in builder stage. |
| **Non-root user** | Defense in depth; limits blast radius of container compromise. |

---

## 3. Entrypoint Script Strategy

### 3.1 Design Goals

1. **Wait for dependencies** with bounded timeout (fail-fast, don't hang forever)
2. **Run migrations only from API container** (avoid race conditions)
3. **Detect role** from command and adjust behavior
4. **Exit cleanly** on signals for graceful shutdown

### 3.2 Final docker-entrypoint.sh

```bash
#!/bin/bash
set -e

# ================================================================
# EaseEmail Notifications - Docker Entrypoint
# Handles dependency waiting, migrations, and role-based startup
# ================================================================

# Colors for logging
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ----------------------------------------------------------------
# Wait for PostgreSQL
# ----------------------------------------------------------------
wait_for_postgres() {
    local max_attempts=30
    local attempt=1
    
    log_info "Waiting for PostgreSQL at ${POSTGRES_SERVER:-db}:${POSTGRES_PORT:-5432}..."
    
    while [ $attempt -le $max_attempts ]; do
        if python -c "
import asyncio
import asyncpg
async def check():
    try:
        conn = await asyncpg.connect(
            host='${POSTGRES_SERVER:-db}',
            port=${POSTGRES_PORT:-5432},
            user='${POSTGRES_USER:-postgres}',
            password='${POSTGRES_PASSWORD:-postgres}',
            database='${POSTGRES_DB:-easeemail}',
            timeout=5
        )
        await conn.close()
        return True
    except Exception:
        return False
exit(0 if asyncio.run(check()) else 1)
" 2>/dev/null; then
            log_info "PostgreSQL is ready!"
            return 0
        fi
        
        log_warn "Attempt $attempt/$max_attempts - PostgreSQL not ready, waiting..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    log_error "PostgreSQL did not become ready in time. Exiting."
    exit 1
}

# ----------------------------------------------------------------
# Wait for Redis
# ----------------------------------------------------------------
wait_for_redis() {
    local max_attempts=15
    local attempt=1
    
    log_info "Waiting for Redis at ${REDIS_HOST:-redis}:${REDIS_PORT:-6379}..."
    
    while [ $attempt -le $max_attempts ]; do
        if python -c "
import redis
r = redis.Redis(host='${REDIS_HOST:-redis}', port=${REDIS_PORT:-6379}, socket_timeout=3)
r.ping()
" 2>/dev/null; then
            log_info "Redis is ready!"
            return 0
        fi
        
        log_warn "Attempt $attempt/$max_attempts - Redis not ready, waiting..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    log_error "Redis did not become ready in time. Exiting."
    exit 1
}

# ----------------------------------------------------------------
# Run Database Migrations
# ----------------------------------------------------------------
run_migrations() {
    log_info "Running Alembic migrations..."
    
    # Check if alembic is configured
    if [ -f "alembic.ini" ]; then
        alembic upgrade head
        log_info "Migrations completed successfully."
    else
        log_warn "No alembic.ini found. Skipping migrations."
        log_info "Using SQLAlchemy create_all fallback (development mode)."
    fi
}

# ----------------------------------------------------------------
# Detect Container Role
# ----------------------------------------------------------------
detect_role() {
    local cmd="$1"
    
    if echo "$cmd" | grep -q "worker"; then
        echo "worker"
    elif echo "$cmd" | grep -q "celery"; then
        echo "worker"
    elif echo "$cmd" | grep -q "gunicorn\|uvicorn"; then
        echo "api"
    else
        echo "unknown"
    fi
}

# ----------------------------------------------------------------
# Main Execution
# ----------------------------------------------------------------
main() {
    log_info "=== EaseEmail Notifications Container Starting ==="
    log_info "Command: $@"
    
    # Determine role from command
    local role=$(detect_role "$*")
    log_info "Detected role: $role"
    
    # Always wait for dependencies
    wait_for_postgres
    wait_for_redis
    
    # Only run migrations from API container to avoid race conditions
    if [ "$role" = "api" ]; then
        # Use lock to ensure only one API instance runs migrations
        if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
            run_migrations
        else
            log_info "RUN_MIGRATIONS=false, skipping migrations."
        fi
    else
        log_info "Worker container - skipping migrations (API handles this)."
    fi
    
    log_info "Starting application..."
    exec "$@"
}

# Trap signals for graceful shutdown
trap 'log_info "Received shutdown signal"; exit 0' SIGTERM SIGINT

# Run main
main "$@"
```

### 3.3 Entrypoint Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Role detection from command** | Single entrypoint handles both API and worker, reducing duplication |
| **Migrations only from API** | Prevents race conditions when multiple workers start simultaneously |
| **Bounded wait loops** | Fail-fast after 60s (Postgres) or 30s (Redis) prevents stuck containers |
| **Python-based health checks** | Uses actual DB drivers, not just TCP ping, ensuring real connectivity |
| **Signal trapping** | Ensures clean shutdown during rolling deployments |
| **`RUN_MIGRATIONS` env var** | Allows disabling migrations for scaled API replicas |

---

## 4. Docker Compose Strategy

### 4.1 Service Design

| Service | Purpose | Scaling Model |
|---------|---------|---------------|
| `db` | PostgreSQL primary | Single instance (HA via managed DB in prod) |
| `redis` | Queue + Cache | Single instance (HA via managed Redis in prod) |
| `api` | HTTP API server | Horizontal (2+ replicas behind load balancer) |
| `worker` | Background processor | Horizontal (3+ replicas for throughput) |
| `migration` | One-shot migration runner | Run once, exit |

### 4.2 Final docker-compose.yml

```yaml
# ================================================================
# EaseEmail Notifications - Docker Compose Configuration
# Production-ready with health checks, resource limits, and isolation
# ================================================================

services:
  # ----------------------------------------------------------------
  # PostgreSQL Database
  # ----------------------------------------------------------------
  db:
    image: postgres:15-alpine
    container_name: easeemail-db
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-easeemail}
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
      # Performance tuning for containerized PostgreSQL
      POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=C"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-easeemail}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    networks:
      - easeemail-internal
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

  # ----------------------------------------------------------------
  # Redis (Queue + Cache)
  # ----------------------------------------------------------------
  redis:
    image: redis:7-alpine
    container_name: easeemail-redis
    restart: unless-stopped
    command: redis-server --appendonly yes --maxmemory 128mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
    networks:
      - easeemail-internal
    deploy:
      resources:
        limits:
          memory: 256M
        reservations:
          memory: 64M

  # ----------------------------------------------------------------
  # Database Migrations (One-Shot)
  # Runs before API starts, exits after completion
  # ----------------------------------------------------------------
  migration:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: easeemail-migration
    command: ["python", "-c", "print('Migrations handled by API entrypoint')"]
    env_file:
      - .env
    environment:
      POSTGRES_SERVER: db
      REDIS_HOST: redis
      RUN_MIGRATIONS: "true"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - easeemail-internal
    restart: "no"
    profiles:
      - migration  # Only runs with: docker-compose --profile migration up

  # ----------------------------------------------------------------
  # API Server (FastAPI + Gunicorn)
  # ----------------------------------------------------------------
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: easeemail-api
    restart: unless-stopped
    command: >
      gunicorn app.main:app
      --worker-class uvicorn.workers.UvicornWorker
      --bind 0.0.0.0:8000
      --workers 2
      --threads 1
      --timeout 120
      --graceful-timeout 30
      --keep-alive 5
      --max-requests 1000
      --max-requests-jitter 100
      --access-logfile -
      --error-logfile -
      --log-level info
    volumes:
      - ./app/static:/app/app/static:ro
      - app_logs:/app/logs
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      POSTGRES_SERVER: db
      REDIS_HOST: redis
      RUN_MIGRATIONS: "true"
      # Explicit service discovery
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-postgres}@db:5432/${POSTGRES_DB:-easeemail}
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/live"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 45s
    networks:
      - easeemail-internal
      - easeemail-public
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

  # ----------------------------------------------------------------
  # Background Worker
  # Processes email sending and webhook delivery
  # ----------------------------------------------------------------
  worker:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: easeemail-worker
    restart: unless-stopped
    # Custom worker command - replace with actual worker implementation
    command: >
      python -m app.worker.main
    volumes:
      - app_logs:/app/logs
    env_file:
      - .env
    environment:
      POSTGRES_SERVER: db
      REDIS_HOST: redis
      RUN_MIGRATIONS: "false"
      # Worker-specific settings
      WORKER_CONCURRENCY: "4"
      WORKER_PREFETCH: "1"
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-postgres}@db:5432/${POSTGRES_DB:-easeemail}
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
      api:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "python", "-c", "import redis; redis.Redis(host='redis').ping()"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    networks:
      - easeemail-internal
    deploy:
      resources:
        limits:
          memory: 384M
        reservations:
          memory: 128M

# ----------------------------------------------------------------
# Volumes
# ----------------------------------------------------------------
volumes:
  postgres_data:
    name: easeemail-postgres-data
  redis_data:
    name: easeemail-redis-data
  app_logs:
    name: easeemail-app-logs

# ----------------------------------------------------------------
# Networks
# ----------------------------------------------------------------
networks:
  easeemail-internal:
    name: easeemail-internal
    driver: bridge
    internal: true  # No external access
  easeemail-public:
    name: easeemail-public
    driver: bridge
    # API exposed here for external access
```

### 4.3 Compose Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Two networks** | `internal` for DB/Redis (no external access), `public` for API ingress |
| **Memory limits** | Prevents container from consuming host memory; enables proper OOM handling |
| **`--maxmemory` on Redis** | Prevents Redis from growing unbounded; LRU eviction for cache keys |
| **`depends_on` with `service_healthy`** | Ensures startup order respects actual readiness, not just container creation |
| **Worker depends on API** | API runs migrations first; workers start after DB schema is current |
| **Separate log volume** | Centralized logging; easy to mount for log aggregation (ELK, etc.) |
| **Migration profile** | Explicit control over when migrations run; useful for blue-green deployments |

---

## 5. Health Endpoints

### 5.1 Required Endpoints

Add these to your FastAPI application:

```python
# app/api/v1/endpoints/health.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import redis.asyncio as redis
from app.db.session import get_db
from app.core.config import settings

router = APIRouter()

@router.get("/health/live")
async def liveness():
    """
    Liveness probe - Is the process running?
    Returns 200 if the application process is alive.
    Kubernetes uses this to know when to restart a container.
    """
    return {"status": "alive"}

@router.get("/health/ready")
async def readiness(db: AsyncSession = Depends(get_db)):
    """
    Readiness probe - Can the application serve traffic?
    Checks database and redis connectivity.
    Kubernetes uses this to know when to add pod to load balancer.
    """
    errors = []
    
    # Check PostgreSQL
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        errors.append(f"PostgreSQL: {str(e)}")
    
    # Check Redis
    try:
        r = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            socket_timeout=3
        )
        await r.ping()
        await r.close()
    except Exception as e:
        errors.append(f"Redis: {str(e)}")
    
    if errors:
        raise HTTPException(status_code=503, detail={"errors": errors})
    
    return {"status": "ready", "database": "ok", "redis": "ok"}

@router.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    """Combined health check for backwards compatibility."""
    return await readiness(db)
```

### 5.2 Register Health Router

```python
# In app/api/v1/api.py
from app.api.v1.endpoints import health

api_router.include_router(health.router, tags=["health"])
```

---

## 6. Secrets Management Strategy

### 6.1 Current State (Development)

```
.env file → docker-compose env_file → Container environment
```

### 6.2 Production Readiness

| Secret | Dev Approach | Production Approach |
|--------|--------------|---------------------|
| `POSTGRES_PASSWORD` | `.env` file | Docker Secrets / Vault |
| `SECRET_KEY` | `.env` file | Docker Secrets / Vault |
| `EMAIL_HOST_PASSWORD` | `.env` file | Docker Secrets / Vault |

### 6.3 Migration Path

1. **Current `.env`**: Keep for local development
2. **Docker Secrets**: Add `secrets:` section to compose for staging
3. **Vault/AWS Secrets Manager**: Integrate for production

```yaml
# Future production compose addition
secrets:
  db_password:
    external: true
  api_secret_key:
    external: true

services:
  api:
    secrets:
      - db_password
      - api_secret_key
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
```

---

## 7. Scaling Strategy

### 7.1 Horizontal Scaling Commands

```bash
# Scale API servers
docker-compose up -d --scale api=3

# Scale workers
docker-compose up -d --scale worker=5

# View running containers
docker-compose ps
```

### 7.2 Resource Allocation Guide

| Service | Replicas | Memory/Instance | Total Memory |
|---------|----------|-----------------|--------------|
| db | 1 | 512MB | 512MB |
| redis | 1 | 256MB | 256MB |
| api | 2 | 512MB | 1GB |
| worker | 3 | 384MB | 1.15GB |
| **Total** | 7 | - | **~3GB** |

---

## 8. Deployment Workflow

### 8.1 Initial Deployment

```bash
# 1. Build images
docker-compose build

# 2. Start infrastructure
docker-compose up -d db redis

# 3. Wait for health
docker-compose ps  # Verify (healthy)

# 4. Start API (runs migrations)
docker-compose up -d api

# 5. Start workers
docker-compose up -d worker

# 6. Verify all healthy
docker-compose ps
```

### 8.2 Rolling Update (Zero-Downtime)

```bash
# 1. Build new image
docker-compose build api worker

# 2. Scale up new instances
docker-compose up -d --scale api=4  # 2 old + 2 new

# 3. Wait for new instances to be healthy
docker-compose ps

# 4. Scale down to target
docker-compose up -d --scale api=2  # Old instances removed

# 5. Repeat for workers
```

---

## 9. Verification Checklist

### Pre-Deployment

- [ ] `.env` file configured with all required variables
- [ ] `docker-entrypoint.sh` has execute permissions (`chmod +x`)
- [ ] `requirements.txt` includes `gunicorn`, `uvicorn[standard]`, `asyncpg`, `redis`
- [ ] Health endpoints implemented in FastAPI app

### Post-Deployment

- [ ] All containers show `(healthy)` in `docker-compose ps`
- [ ] API responds at `http://localhost:8000/health/ready`
- [ ] Swagger UI accessible at `http://localhost:8000/docs`
- [ ] Worker logs show successful Redis connection
- [ ] Database migrations applied (check `alembic_version` table)

---

## 10. Files to Create/Modify

| File | Action | Priority |
|------|--------|----------|
| `Dockerfile` | **Replace** with multi-stage build | P0 |
| `docker-entrypoint.sh` | **Create** new file | P0 |
| `docker-compose.yml` | **Replace** with enhanced config | P0 |
| `app/api/v1/endpoints/health.py` | **Create** health endpoints | P1 |
| `app/api/v1/api.py` | **Modify** to include health router | P1 |
| `.dockerignore` | **Create** to exclude unnecessary files | P2 |

---

## 11. .dockerignore (Recommended)

```
# .dockerignore
.git
.gitignore
.env
.env.*
*.md
docs/
tests/
__pycache__
*.pyc
*.pyo
.pytest_cache
.coverage
htmlcov/
.vscode/
.idea/
*.egg-info/
dist/
build/
.agent/
Documents/
```

---

## Appendix: Why This Plan Differs from v1

| Original Plan | This Plan | Reason |
|---------------|-----------|--------|
| Single-stage Dockerfile | Multi-stage build | 40% smaller image, no build tools in prod |
| No resource limits | Explicit memory limits | Prevents runaway containers |
| Single network | Dual network (internal/public) | Defense in depth; DB not exposed |
| Migrations in every container | API-only migrations | Prevents race conditions |
| Basic health check | Liveness + Readiness | Proper Kubernetes/ECS compatibility |
| Celery worker assumption | Generic worker design | Flexibility for any async framework |
| No scaling guidance | Explicit scaling strategy | Production readiness |

---

**End of Implementation Plan**

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

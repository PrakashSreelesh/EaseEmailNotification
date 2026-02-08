# Implementation Plan - Docker Configuration Enhancement

Refining the `Dockerfile` and `docker-compose.yml` for `EaseEmailNotifications` to match the robust, production-ready standards of the reference "Albiz Media" project, while adapting for the FastAPI architecture.

## User Review Required

> [!IMPORTANT]
> The reference project uses `gunicorn` as an application server. For FastAPI, we will use `gunicorn` with `uvicorn` workers (`uvicorn.workers.UvicornWorker`) for better performance and concurrency in production builds.

## Proposed Changes

### 1. Create `docker-entrypoint.sh`

We will create an entrypoint script to handle database migrations automatically before the application starts.

**File:** `docker-entrypoint.sh`
- **Logic:**
    - Wait for the database to be ready (optional but recommended).
    - Run Alembic migrations: `alembic upgrade head`.
    - Execute the command passed to the container (start server or worker).

### 2. Update `Dockerfile`

Refactor the existing simple `Dockerfile` into a robust, multi-stage-like production file.

- **Base Image:** `python:3.11-slim`
- **System Dependencies:** Install `build-essential`, `libpq-dev` (for PostgreSQL), `curl` (for healthchecks).
- **User Setup:** Create a non-root user `appuser` (UID 1000) for security.
- **Directory Structure:** Create `/app/logs` and set permissions.
- **Environment:** Set `PYTHONDONTWRITEBYTECODE`, `PYTHONUNBUFFERED`.
- **Entrypoint:** Copy and use `docker-entrypoint.sh`.
- **Healthcheck:** Add a healthcheck command pinging the API.
- **Command:** Use `gunicorn` with `uvicorn` workers binding to port 8000.

### 3. Update `docker-compose.yml`

Enhance the composition to include healthchecks, proper networking, and environment file usage.

- **Services:** `db`, `redis`, `api` (was `web` in ref), `worker`.
- **Environment:** Load from `.env` file instead of inline values where possible.
- **Healthchecks:**
    - `db`: `pg_isready`
    - `redis`: `redis-cli ping`
    - `api`: `curl` check against health endpoint.
- **Dependencies:** Use `depends_on` with `condition: service_healthy` to ensure DB is up before API starts.
- **Volumes:** Persist `postgres_data` and namespaced `redis_data`.

## Verification Plan

1.  **Build Containers:** Run `docker-compose build` to verify the Dockerfile integrity.
2.  **Start Stack:** Run `docker-compose up -d` and check logs (`docker-compose logs -f`).
3.  **Check Health:** Use `docker ps` to verify all services report `(healthy)`.
4.  **Verify Migrations:** Ensure migrations ran via the entrypoint script logs.
5.  **Test Endpoint:** Access `http://localhost:8000/docs` to confirm the API is serving.

## Action Plan

- [ ] Create `docker-entrypoint.sh` with migration logic.
- [ ] Update `Dockerfile` with system deps, user creation, and entrypoint.
- [ ] Update `docker-compose.yml` with healthchecks, env file, and dependencies.
- [ ] Verify the build and startup.


# EaseEmail Notifications (FastAPI Edition)

A high-performance implementation of the EaseEmail Platform using purely FastAPI, SQLAlchemy (Async), and Celery.

## Architecture

- **`app/main.py`**: Entry point for the REST API.
- **`app/models/`**: SQLAlchemy models for Tenants, Users, Applications, and Email Services.
- **`app/worker/`**: Celery worker logic for async email dispatch.
- **`app/api/`**: API Route definitions.

## Key Features

- **Async Database Access**: Using `asyncpg` + `SQLAlchemy 2.0`.
- **Background Workers**: Celery backed by Redis for high-throughput email sending.
- **Multi-tenancy**: Built-in support for Tenants and Applications.

## Running the Project

The easiest way to run is via Docker Compose:

```bash
docker-compose up --build
```

This will spin up:
- **API**: `http://localhost:8000` (Docs: `/api/v1/docs`)
- **Worker**: Background process for sending emails.
- **Postgres**: Database.
- **Redis**: Message Broker.

## Development

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

   chmod +x ./run_local.sh
   ./run_local.sh


2. Run API:
   ```bash
   uvicorn app.main:app --reload
   ```

3. Run Worker:
   ```bash
   celery -A app.worker.tasks worker --loglevel=info
   ```

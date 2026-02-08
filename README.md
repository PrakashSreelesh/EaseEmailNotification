
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

   # Run the script-Locally
   chmod +x ./run_local.sh
   ./run_local.sh
   ```

2. Run API:
   ```bash
   uvicorn app.main:app --reload
   ```

3. Run Worker:
   ```bash
   celery -A app.worker.tasks worker --loglevel=info
   ```



- Send email using Application API Key authentication

```bash
curl -X 'POST' \
  'http://0.0.0.0:8000/api/v1/send/email/?template=Welcome%20Email' \
  -H 'accept: application/json' \
  -H 'XAPIKey: XAPIKey' \
  -H 'Content-Type: application/json' \
  -d '{
  "to_email": "prakashsreelesh94@gmail.com",
  "variables_data": {
    "date": "09-02-2026",
    "username": "Sreelesh Prakash",
    "password": "password@123",
    "login_url": "sample_login_url",
    "application": "sample_application"
  },
  "service_name": "Service Test"
}'
```



```md
# Build the images
docker-compose build

# Start the stack
docker-compose up -d

# Check health status
docker-compose ps

# View logs
docker-compose logs -f api

```
---
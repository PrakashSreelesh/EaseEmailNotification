#!/bin/bash

# Kill any existing processes (silently)
pkill -f "uvicorn app.main:app" > /dev/null 2>&1
pkill -f "celery -A app.worker.tasks" > /dev/null 2>&1

echo "Starting Redis..."
sudo service redis-server start

echo "Starting Postgres..."
sudo service postgresql start

# Note: We skip DB creation since it already exists with user/pass: postgres

echo "Starting Celery Worker..."
celery -A app.worker.tasks worker --loglevel=info &
worker_pid=$!

echo "Starting FastAPI Server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
api_pid=$!

echo "-----------------------------------------------"
echo "EaseEmail Notifications is running!"
echo "API:    http://localhost:8000"
echo "Docs:   http://localhost:8000/docs"
echo "-----------------------------------------------"

# Wait for processes
wait $worker_pid $api_pid

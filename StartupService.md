# EaseEmail Notifications - Startup Service Guide

**Version:** 3.0 (Async Email + Webhook Callbacks)  
**Last Updated:** 2026-02-09  
**Super Admin:** admin@easeemail.com

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Setup](#database-setup)
4. [Starting Services](#starting-services)
5. [Accessing the Application](#accessing-the-application)
6. [Stopping Services](#stopping-services)
7. [Troubleshooting](#troubleshooting)
8. [Development Workflow](#development-workflow)

---

## 1. Prerequisites

### System Requirements

✅ **Required Software:**
- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Node.js 14+ (for frontend, if applicable)
- Git

✅ **Python Packages:**
All listed in `requirements.txt` (will be installed in Step 2)

### Check Prerequisites

```bash
# Check Python version
python3 --version
# Expected: Python 3.8.x or higher

# Check PostgreSQL
psql --version
# Expected: psql (PostgreSQL) 12.x or higher

# Check Redis
redis-cli --version
# Expected: redis-cli 6.x.x or higher

# Check Git
git --version
# Expected: git version 2.x.x
```

---

## 2. Environment Setup

### Step 2.1: Clone Repository (if not already done)

```bash
cd ~/MyOwnProjects/SMTP-Service/EaseEmail-Fullstack-New
git clone <repository-url> EaseEmailNotifications
cd EaseEmailNotifications
```

### Step 2.2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation (you should see (venv) in prompt)
which python
# Expected: /path/to/EaseEmailNotifications/venv/bin/python
```

### Step 2.3: Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# Verify critical packages
pip list | grep -E "(fastapi|celery|sqlalchemy|redis|prometheus)"
```

**Expected packages:**
```
celery                  5.x.x
fastapi                 0.x.x
SQLAlchemy             2.x.x
redis                  4.x.x
prometheus_client      0.21.1
```

### Step 2.4: Configure Environment Variables

```bash
# Copy example environment file (if exists)
cp .env.example .env

# Edit .env file
nano .env  # or use your preferred editor
```

**Required Environment Variables:**

```bash
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/easeemail

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your-secret-key-here-change-in-production

# CORS Origins (for frontend)
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]

# Logging
LOG_LEVEL=INFO
```

---

## 3. Database Setup

### Step 3.1: Start PostgreSQL

```bash
# Start PostgreSQL service
sudo systemctl start postgresql

# Verify running
sudo systemctl status postgresql
# Expected: active (running)
```

### Step 3.2: Create Database

```bash
# Login to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE easeemail;
CREATE USER easeemail_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE easeemail TO easeemail_user;

# Exit psql
\q
```

### Step 3.3: Run Migrations

**⚠️ IMPORTANT: Run migrations in order**

```bash
# Navigate to project directory
cd /home/sreelesh-p/MyOwnProjects/SMTP-Service/EaseEmail-Fullstack-New/EaseEmailNotifications

# Run initial schema migration
psql -U postgres -d easeemail -f migrations/initial_schema.sql

# Run webhook delivery tracking migration (NEW in v3.0)
psql -U postgres -d easeemail -f migrations/001_add_webhook_delivery_tracking.sql
```

**Verify migrations:**
```bash
psql -U postgres -d easeemail -c "\dt"
```

**Expected tables:**
- tenants
- applications
- email_services
- email_templates
- smtp_configurations
- email_jobs
- email_logs
- webhook_services
- **webhook_deliveries** (NEW - v3.0)

### Step 3.4: Verify Database Connection

```bash
# Test connection from Python
python3 << EOF
from app.db.session import SessionLocal
db = SessionLocal()
print("✅ Database connected successfully!")
db.close()
EOF
```

---

## 4. Starting Services

### Step 4.1: Start Redis

```bash
# Start Redis service
sudo systemctl start redis

# Verify Redis is running
redis-cli ping
# Expected: PONG
```

### Step 4.2: Method A - Use Startup Script (Recommended)

```bash
# Make sure you're in the project directory
cd /home/sreelesh-p/MyOwnProjects/SMTP-Service/EaseEmail-Fullstack-New/EaseEmailNotifications

# Run the startup script
./run_local.sh
```

**Expected Output:**
```
Starting Redis...
Starting Postgres...
Starting Celery Worker...
Starting FastAPI Server...
-----------------------------------------------
EaseEmail Notifications is running!
API:    http://localhost:8000
Docs:   http://localhost:8000/docs
-----------------------------------------------
```

### Step 4.3: Method B - Manual Startup (Detailed Control)

**⚠️ You need 4 separate terminal windows for this method**

#### Terminal 1: Redis (if not using systemd)

```bash
cd /home/sreelesh-p/MyOwnProjects/SMTP-Service/EaseEmail-Fullstack-New/EaseEmailNotifications
redis-server
```

#### Terminal 2: Email Worker

```bash
cd /home/sreelesh-p/MyOwnProjects/SMTP-Service/EaseEmail-Fullstack-New/EaseEmailNotifications
source venv/bin/activate

celery -A app.worker.celery_config worker \
  -Q email_delivery \
  -c 4 \
  --loglevel=info \
  --logfile=logs/email_worker.log
```

**Expected Output:**
```
-------------- celery@hostname v5.x.x
...
[tasks]
  . send_email_task

[queues]
  .> email_delivery

celery@hostname ready.
```

#### Terminal 3: Webhook Worker

```bash
cd /home/sreelesh-p/MyOwnProjects/SMTP-Service/EaseEmail-Fullstack-New/EaseEmailNotifications
source venv/bin/activate

celery -A app.worker.celery_config worker \
  -Q webhook_delivery \
  -c 2 \
  --loglevel=info \
  --logfile=logs/webhook_worker.log
```

**Expected Output:**
```
[tasks]
  . deliver_webhook_task

[queues]
  .> webhook_delivery

celery@hostname ready.
```

#### Terminal 4: FastAPI Server

```bash
cd /home/sreelesh-p/MyOwnProjects/SMTP-Service/EaseEmail-Fullstack-New/EaseEmailNotifications
source venv/bin/activate

uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload \
  --log-level info
```

**Expected Output:**
```
INFO:     Will watch for changes in these directories: ['/path/to/EaseEmailNotifications']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 4.4: Verify All Services Running

```bash
# Check API health
curl http://localhost:8000/api/v1/health/ready

# Expected response:
# {"status":"ready","database":"ok","redis":"ok","service":"easeemail-api"}

# Check workers
ps aux | grep celery | grep -v grep
# Should show 6+ celery processes (1 main + 4 email workers + 2 webhook workers)

# Check API server
ps aux | grep uvicorn | grep -v grep
# Should show uvicorn process
```

---

## 5. Accessing the Application

### 5.1 Web Interface

#### Access Dashboard (Frontend)

1. **Open your browser**
2. **Navigate to:** http://localhost:8000
3. **Automatic redirect to:** http://localhost:8000/dashboard

#### Login Credentials

**Super Admin User:**
- **Email:** `admin@easeemail.com`
- **Password:** `admin@123`
- **Role:** System Super Administrator

```bash
# View all users if needed
psql -U postgres -d easeemail -c "SELECT email, role, is_superadmin, is_active FROM users;"
```

**Other Available Users:**
- `prakashsreelesh94@gmail.com` (Admin)
- `prakashsreelesh@gmail.com` (Regular User)

### 5.2 API Documentation

**Interactive API Docs (Swagger UI):**
- URL: http://localhost:8000/docs
- Try out endpoints directly from browser
- View request/response schemas

**Alternative API Docs (ReDoc):**
- URL: http://localhost:8000/redoc
- Clean, searchable documentation

### 5.3 Monitoring Endpoints

**Health Check:**
```bash
curl http://localhost:8000/api/v1/health/ready
```

**Prometheus Metrics:**
```bash
curl http://localhost:8000/api/v1/metrics
```

**Liveness Probe:**
```bash
curl http://localhost:8000/api/v1/health/live
```

---

## 6. Stopping Services

### Method A: Stop All Services (Quick)

```bash
# Kill all Celery workers
pkill -f celery

# Kill API server
pkill -f uvicorn

# Stop Redis (if started manually)
pkill redis-server

# Or use systemctl
sudo systemctl stop redis
sudo systemctl stop postgresql
```

### Method B: Graceful Shutdown (Recommended)

#### Stop Each Service Gracefully

**1. Stop Celery Workers:**
```bash
# Find worker PIDs
ps aux | grep celery | grep -v grep

# Send TERM signal (allows workers to finish current tasks)
kill -TERM <email_worker_pid>
kill -TERM <webhook_worker_pid>

# Wait 10 seconds, then force kill if still running
sleep 10
pkill -9 -f celery
```

**2. Stop API Server:**
```bash
# If running in foreground, press CTRL+C

# If running in background
kill -TERM <uvicorn_pid>
```

**3. Stop Redis:**
```bash
# If using systemd
sudo systemctl stop redis

# If started manually
redis-cli shutdown
```

### Verify All Stopped

```bash
# Check for remaining processes
ps aux | grep -E "(celery|uvicorn|redis)" | grep -v grep

# Should return no results
```

---

## 7. Troubleshooting

### Issue 1: Port 8000 Already in Use

**Error:**
```
ERROR: [Errno 98] Address already in use
```

**Solution:**
```bash
# Find process using port 8000
fuser 8000/tcp

# Kill the process
kill -9 $(fuser 8000/tcp 2>/dev/null | awk '{print $1}')

# Restart API
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Issue 2: Module Not Found Error

**Error:**
```
ModuleNotFoundError: No module named 'prometheus_client'
```

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep prometheus_client
```

### Issue 3: Database Connection Failed

**Error:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Start if not running
sudo systemctl start postgresql

# Test connection
psql -U postgres -d easeemail -c "SELECT 1;"

# Check DATABASE_URL in .env matches your setup
```

### Issue 4: Redis Connection Failed

**Error:**
```
redis.exceptions.ConnectionError: Error connecting to Redis
```

**Solution:**
```bash
# Check Redis is running
redis-cli ping

# Start if not running
sudo systemctl start redis

# Verify REDIS_HOST and REDIS_PORT in .env
```

### Issue 5: Celery Workers Not Processing Jobs

**Symptoms:**
- Jobs stuck in "queued" status
- No worker logs

**Solution:**
```bash
# Check if workers are running
ps aux | grep celery

# Check worker can connect to Redis
celery -A app.worker.celery_config inspect ping

# Expected: celery@hostname: pong

# Check active tasks
celery -A app.worker.celery_config inspect active

# Restart workers
pkill -f celery
celery -A app.worker.celery_config worker -Q email_delivery -c 4 &
celery -A app.worker.celery_config worker -Q webhook_delivery -c 2 &
```

### Issue 6: Frontend Not Loading

**Symptoms:**
- http://localhost:8000 shows 404
- Dashboard not accessible

**Solution:**
```bash
# Check if static files are built
ls -la app/static/

# If using separate frontend server
# Check if frontend build exists
# Restart API server
```

### Issue 7: Login Failed

**Symptoms:**
- Cannot login with admin@easeemail.com

**Solution:**
```bash
# Check user exists
psql -U postgres -d easeemail << EOF
SELECT email, is_active, is_superadmin, is_admin 
FROM users 
WHERE email = 'admin@easeemail.com';
EOF

# Verify credentials
# Email: admin@easeemail.com
# Password: admin@123 (hashed_password field in database)
```

---

## 8. Development Workflow

### 8.1 Making Code Changes

**Backend Changes (Python):**

1. Make changes to files in `app/`
2. If using `--reload` flag, server auto-restarts
3. If not using reload:
   ```bash
   pkill -f uvicorn
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

**Worker Changes (Celery tasks):**

1. Make changes to `app/worker/`
2. **Restart workers manually** (Celery doesn't auto-reload):
   ```bash
   pkill -f celery
   celery -A app.worker.celery_config worker -Q email_delivery -c 4 &
   celery -A app.worker.celery_config worker -Q webhook_delivery -c 2 &
   ```

### 8.2 Database Schema Changes

**Creating New Migration:**

1. Create migration SQL file:
   ```bash
   nano migrations/00X_description.sql
   ```

2. Write migration:
   ```sql
   -- Migration: 00X_description
   -- Date: 2026-02-09
   
   -- Forward migration
   ALTER TABLE table_name ADD COLUMN new_column TYPE;
   
   -- Rollback script (at end of file)
   -- ALTER TABLE table_name DROP COLUMN new_column;
   ```

3. Run migration:
   ```bash
   psql -U postgres -d easeemail -f migrations/00X_description.sql
   ```

### 8.3 Testing Changes

**Run Tests:**
```bash
# Activate venv
source venv/bin/activate

# Run pytest
pytest tests/

# Run specific test
pytest tests/test_email_worker.py -v
```

**Manual Testing:**
```bash
# Use verification script
python3 verify_async_email.py

# Or follow Phase 4 testing guide
cat Documents/Phase4_Manual_Testing_Guide.md
```

### 8.4 Viewing Logs

**Application Logs:**
```bash
# API logs (if using logfile)
tail -f logs/app.log

# Email worker logs
tail -f logs/email_worker.log

# Webhook worker logs
tail -f logs/webhook_worker.log
```

**Database Logs:**
```bash
sudo tail -f /var/log/postgresql/postgresql-*.log
```

**Redis Logs:**
```bash
sudo tail -f /var/log/redis/redis-server.log
```

---

## 9. Quick Reference Commands

### Start Everything

```bash
cd /home/sreelesh-p/MyOwnProjects/SMTP-Service/EaseEmail-Fullstack-New/EaseEmailNotifications
source venv/bin/activate
./run_local.sh
```

### Stop Everything

```bash
pkill -f celery
pkill -f uvicorn
```

### Restart Workers Only

```bash
pkill -f celery
source venv/bin/activate
celery -A app.worker.celery_config worker -Q email_delivery -c 4 &
celery -A app.worker.celery_config worker -Q webhook_delivery -c 2 &
```

### Check Status

```bash
# Health check
curl http://localhost:8000/api/v1/health/ready

# Workers status
celery -A app.worker.celery_config inspect stats

# Redis
redis-cli ping

# Database
psql -U postgres -d easeemail -c "SELECT COUNT(*) FROM email_jobs;"
```

### View Active Jobs

```bash
# Database
psql -U postgres -d easeemail << EOF
SELECT id, status, created_at, to_email 
FROM email_jobs 
ORDER BY created_at DESC 
LIMIT 10;
EOF

# Celery
celery -A app.worker.celery_config inspect active
```

---

## 10. Production Deployment Notes

### Before Deploying to Production:

- [ ] Change SECRET_KEY in .env
- [ ] Use production database credentials
- [ ] Configure HTTPS/SSL
- [ ] Set up monitoring (Prometheus + Grafana)
- [ ] Configure log aggregation
- [ ] Set up backup strategy for database
- [ ] Use proper process manager (systemd, supervisor)
- [ ] Set up reverse proxy (nginx)
- [ ] Configure firewall rules
- [ ] Review and update CORS_ORIGINS
- [ ] Enable rate limiting
- [ ] Set up database connection pooling

### Recommended Production Stack:

```
Internet → Nginx (reverse proxy) → FastAPI (Uvicorn/Gunicorn)
                                    ↓
                              PostgreSQL + Redis
                                    ↓
                            Celery Workers (systemd)
```

---

## Support & Documentation

- **API Documentation:** http://localhost:8000/docs
- **Phase 4 Testing Guide:** `Documents/Phase4_Manual_Testing_Guide.md`
- **Pending Enhancements:** `Documents/Pending_Enhancements_TODO.md`
- **Implementation Plan:** `Documents/Async_Email_Sending_Implementation_Plan.md`

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-09  
**Maintainer:** Development Team

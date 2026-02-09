# Error Resolution Guide

**Date:** 2026-02-09  
**Errors Fixed:** SyntaxError in api.py, DuplicateNodenameWarning in Celery

---

## Error 1: SyntaxError in `/app/api/v1/api.py`

### Problem:
```python
api_router.include_router(dashboard.router, prefix="", tags=["dashboard"])api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
```

**Issue:** Two statements on the same line without newline separator

### Fix Applied:
✅ **Fixed** - Separated into two lines:
```python
api_router.include_router(dashboard.router, prefix="", tags=["dashboard"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
```

**Status:** ✅ RESOLVED

---

## Error 2: DuplicateNodenameWarning in Celery

### Warning Message:
```
DuplicateNodenameWarning: Received multiple replies from node name: celery@sreeleshp-ThinkPad-T440.
Please make sure you give each node a unique nodename using the celery worker `-n` option.
```

### What It Means:
Multiple Celery workers are running with the **same node name** on your system. This can cause:
- Job duplication (same task executed multiple times)
- Unexpected behavior
- Resource conflicts

### Root Cause:
Your `run_local.sh` script likely starts Celery workers, but if you've also started workers manually or have workers from previous runs still active, they all have the default nodename.

### Solution:

#### Option 1: Kill All Existing Workers (Recommended)
```bash
# Stop the current run_local.sh
# Press CTRL+C in terminal

# Kill ALL Celery workers
pkill -9 -f celery

# Verify no workers running
ps aux | grep celery | grep -v grep
# Should return nothing

# Restart cleanly
./run_local.sh
```

#### Option 2: Give Each Worker a Unique Name

Update `run_local.sh` to give workers unique names:

```bash
# Email worker
celery -A app.worker.celery_config worker \
  -Q email_delivery \
  -c 4 \
  -n email_worker@%h \
  --loglevel=info &

# Webhook worker
celery -A app.worker.celery_config worker \
  -Q webhook_delivery \
  -c 2 \
  -n webhook_worker@%h \
  --loglevel=info &
```

**Explanation:**
- `-n email_worker@%h` - Sets unique node name (email_worker@hostname)
- `-n webhook_worker@%h` - Sets unique node name (webhook_worker@hostname)
- `%h` - Replaced with hostname automatically

#### Option 3: Quick Check for Running Workers

```bash
# Check how many Celery workers are running
ps aux | grep celery | grep -v grep | wc -l

# If more than expected, kill them all
pkill -f celery
```

---

## How to Prevent in Future

### 1. Always Stop Workers Before Restarting

```bash
# In run_local.sh, add cleanup at the start:
echo "Stopping existing workers..."
pkill -f celery
sleep 2

echo "Starting new workers..."
# Then start workers
```

### 2. Use Unique Node Names

Edit `/run_local.sh` or manual worker commands to always include `-n` flag:

```bash
celery -A app.worker.celery_config worker -Q email_delivery -n email@%h
celery -A app.worker.celery_config worker -Q webhook_delivery -n webhook@%h
```

### 3. Check Before Starting

```bash
# Before running run_local.sh
ps aux | grep celery
# If workers found, kill them first
```

---

## Testing the Fixes

### 1. Stop Everything

```bash
# Stop run_local.sh (CTRL+C in terminal)

# Kill all celery processes
pkill -9 -f celery

# Kill uvicorn
pkill -9 -f uvicorn
```

### 2. Verify Clean State

```bash
ps aux | grep -E "(celery|uvicorn)" | grep -v grep
# Should return nothing
```

### 3. Restart Application

```bash
./run_local.sh
```

### 4. Check for Errors

**Expected Output (No Errors):**
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
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.

-------------- celery@hostname ready.
```

**NO warnings about:**
- ❌ SyntaxError
- ❌ DuplicateNodenameWarning

---

## Current Status

| Error | Status | Action Taken |
|-------|--------|--------------|
| SyntaxError in api.py line 20 | ✅ FIXED | Separated two include_router statements |
| DuplicateNodenameWarning | ⚠️ ACTION REQUIRED | User needs to kill existing workers |

---

## Immediate Actions Required

1. **Stop `run_local.sh`** (CTRL+C in terminal)
2. **Kill all Celery workers:**
   ```bash
   pkill -9 -f celery
   ```
3. **Restart:**
   ```bash
   ./run_local.sh
   ```
4. **Verify:** No more duplicate nodename warnings

---

## Optional: Update run_local.sh

To prevent this issue in the future, update your `run_local.sh` script:

```bash
#!/bin/bash

# Cleanup existing processes
echo "Cleaning up existing processes..."
pkill -f celery
pkill -f uvicorn
sleep 2

# Start services
echo "Starting services..."
# ... rest of script
```

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-09 04:25  
**Status:** Syntax error fixed, awaiting user action for Celery cleanup

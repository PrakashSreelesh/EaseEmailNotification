# EaseEmail Notifications - Implementation Roadmap (FastAPI Monolith)

This document outlines the step-by-step plan to build the complete **EaseEmail Notifications** platform using a single **FastAPI** codebase. This replaces the previous hybrid Django/FastAPI approach.

## Phase 1: Foundation & Infrastructure ✅ (In Progress)
- [x] **Project Structure**: Set up `app/` directory with `core`, `models`, `schemas`, `api`, `worker`.
- [x] **Docker Environment**: Create `docker-compose.yml` with FastAPI, PostgreSQL, and Redis.
- [x] **Database Connectivity**: Configure `SQLAlchemy 2.0` (Async) and `Alembic` for migrations.
- [x] **Worker Setup**: Configure `Celery` with Redis for background tasks.
- [ ] **Authentication System**:
    - [ ] Implement JWT (JSON Web Tokens) backend logic.
    - [ ] Create `login` endpoint (`/api/v1/auth/login`).
    - [ ] Create `me` endpoint (`/api/v1/users/me`).
    - [ ] Implement RBAC (Super Admin vs Tenant Admin).

## Phase 2: Core Data Models (Control Plane)
- [x] **Tenants & Users**: Models for multi-tenancy.
- [x] **Applications**: Model for identifying client apps (with API Keys).
- [x] **Email Services**: Configuration for *how* to send emails.
- [ ] **SMTP Accounts**:
    - [ ] Create `SMTPAccount` model (Host, Port, User, Pass).
    - [ ] Encrypt sensitive passwords in DB.
- [ ] **Email Templates**:
    - [ ] Create `EmailTemplate` model (Subject, Body (HTML/Text)).
    - [ ] Add variable support (e.g., `{{ name }}`).
- [ ] **Logs**:
    - [ ] Create `EmailLog` model (Status, Response, Timestamp).

## Phase 3: API Endpoints (Management API)
Matches the sidebar navigation requirements:

- [ ] **Dashboard (`/api/v1/dashboard`)**:
    - [ ] Stats: Total Sent, Failed, Pending, Credits/Quota.
- [ ] **Applications (`/api/v1/applications`)**:
    - [ ] CRUD Endpoints.
    - [ ] API Key rotation logic.
- [ ] **SMTP Accounts (`/api/v1/smtp-accounts`)**:
    - [ ] CRUD Endpoints.
    - [ ] "Test Connection" endpoint.
- [ ] **Templates (`/api/v1/templates`)**:
    - [ ] CRUD Endpoints.
    - [ ] Preview render endpoint.
- [ ] **Email Services (`/api/v1/services`)**:
    - [ ] Operations to link App -> Template -> SMTP Account.
- [ ] **Logs (`/api/v1/logs`)**:
    - [ ] Read-only endpoints with filtering (by date, status, app).

## Phase 4: The Delivery Engine (Delivery Plane)
- [ ] **Sending API (`POST /api/v1/email/send`)**:
    - [ ] Validate API Key.
    - [ ] Validate Rate Limits (Redis).
    - [ ] Create `EmailJob` (Status: Queued).
    - [ ] Push to Celery.
- [ ] **Worker Logic**:
    - [ ] Fetch Job.
    - [ ] Load SMTP Config (Decrypted).
    - [ ] Render Template (Jinja2).
    - [ ] Send via `aiosmtplib`.
    - [ ] Update Job Status (Sent/Failed).
    - [ ] Write to `EmailLog`.
    - [ ] Handle Retries (Exponential Backoff).

## Phase 5: Webhooks (Optional/Future)
- [ ] **Webhook Services**: Register URL endpoints.
- [ ] **Event Dispatcher**: Worker to `POST` JSON payloads to external URLs.
- [ ] **Signature**: Add `X-Signature` HMAC headers for security.

## Phase 6: Frontend Integration
- [ ] **Template Rendering**:
    - [ ] Update `app/templates/dashboard.html` to include full sidebar.
        - Dashboard
        - Email Templates
        - SMTP Accounts
        - Email Logs
        - Applications
        - Email Services
        - User Management
        - Settings
    - [ ] Create distinct HTML templates for each section (or Single Page App approach).

## Execution Plan
1.  **Fix Sidebar**: Update `dashboard.html` immediately to reflect the full menu.
2.  **Database Migration**: Standardize all models in `app/models/all_models.py` and run migration.
3.  **Build APIs**: Implement endpoints one module at a time.

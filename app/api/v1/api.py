from fastapi import APIRouter
from app.api.v1.endpoints import email, applications, email_services, users, smtp, templates, webhooks, logs, tenants, send_email, dashboard, auth, health, jobs, metrics

api_router = APIRouter()

# Health endpoints (no prefix for /health/live and /health/ready)
api_router.include_router(health.router, tags=["health"])

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(email.router, prefix="/email", tags=["emails"])
api_router.include_router(applications.router, prefix="/applications", tags=["applications"])
api_router.include_router(email_services.router, prefix="/email-services", tags=["email-services"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(smtp.router, prefix="/smtp-accounts", tags=["smtp-accounts"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(logs.router, prefix="/logs", tags=["logs"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
api_router.include_router(send_email.router, prefix="/send", tags=["emails"])
api_router.include_router(dashboard.router, prefix="", tags=["dashboard"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])

# Metrics endpoint
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])

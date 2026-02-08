from fastapi import APIRouter
from app.api.v1.endpoints import email, applications, email_services, users, smtp, templates, webhooks, logs, tenants

api_router = APIRouter()

api_router.include_router(email.router, prefix="/email", tags=["emails"])
api_router.include_router(applications.router, prefix="/applications", tags=["applications"])
api_router.include_router(email_services.router, prefix="/email-services", tags=["email-services"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(smtp.router, prefix="/smtp-accounts", tags=["smtp-accounts"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(logs.router, prefix="/logs", tags=["logs"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["tenants"])

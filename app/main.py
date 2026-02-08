from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import RedirectResponse
from app.core.config import settings
from app.api.v1.api import api_router
from app.db.session import engine, Base
import os

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

# Ensure static directory exists
os.makedirs("app/static", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Create tables logic (for dev only, use Alembic in prod)
@app.on_event("startup")
async def init_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root(request: Request):
    return RedirectResponse(url="/dashboard")

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard")
def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/applications")
def applications_page(request: Request):
    return templates.TemplateResponse("applications.html", {"request": request})

@app.get("/smtp-accounts")
def smtp_accounts_page(request: Request):
    return templates.TemplateResponse("smtp_accounts.html", {"request": request})

@app.get("/email-services")
def email_services_page(request: Request):
    return templates.TemplateResponse("email_services.html", {"request": request})

@app.get("/templates")
def templates_page(request: Request):
    return templates.TemplateResponse("templates.html", {"request": request})

@app.get("/webhooks")
def webhooks_page(request: Request):
    return templates.TemplateResponse("webhooks.html", {"request": request})

@app.get("/users")
def users_page(request: Request):
    return templates.TemplateResponse("users.html", {"request": request})

@app.get("/logs")
def logs_page(request: Request):
    return templates.TemplateResponse("logs.html", {"request": request})

@app.get("/tenants")
def tenants_page(request: Request):
    return templates.TemplateResponse("tenants.html", {"request": request})

@app.get("/settings")
def settings_page(request: Request):
    return templates.TemplateResponse("settings.html", {"request": request})

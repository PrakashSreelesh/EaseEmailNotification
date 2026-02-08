from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import RedirectResponse
from app.core.config import settings
from app.api.v1.api import api_router
from app.db.session import engine, Base
import os
import asyncio

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

@app.post("/api/v1/reset-db")
async def reset_database():
    """Reset database schema and seed with sample data"""
    try:
        from app.db.session import engine
        from app.models.all_models import Base

        async with engine.begin() as conn:
            print("🗑️ Dropping all tables...")
            await conn.run_sync(Base.metadata.drop_all)
            print("✨ Creating all tables...")
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Tables recreated successfully.")

        # Now seed the data
        return await seed_database()

    except Exception as e:
        print(f"❌ Error resetting database: {e}")
        return {"message": f"Error resetting database: {str(e)}", "status": "error"}

@app.post("/api/v1/seed")
async def seed_database():
    """Seed the database with sample data for dashboard demo"""
    try:
        from app.db.session import AsyncSessionLocal
        from app.models.all_models import Tenant, User, Application, SMTPConfiguration, EmailTemplate, EmailService, ServiceConfiguration, WebhookService, EmailJob, EmailLog
        from sqlalchemy import text
        import uuid

        async with AsyncSessionLocal() as db:
            print("🌱 Starting database seed...")

            # 1. Create Tenant
            result = await db.execute(text("SELECT * FROM tenants WHERE name = 'Demo Corp'"))
            tenant = result.first()
            if not tenant:
                tenant_id = str(uuid.uuid4())
                await db.execute(text("INSERT INTO tenants (id, name) VALUES (:id, :name)"),
                               {"id": tenant_id, "name": "Demo Corp"})
                print("✅ Tenant Created")
            else:
                tenant_id = tenant[0]

            # 2. Create Users (2 total)
            # User 1 - Super Admin
            result = await db.execute(text("SELECT * FROM users WHERE email = :email"), {"email": "admin@easeemail.com"})
            if not result.first():
                await db.execute(text("""
                    INSERT INTO users (id, tenant_id, email, full_name, role, hashed_password, is_superadmin, is_admin)
                    VALUES (:id, :tenant_id, :email, :full_name, :role, :password, :is_superadmin, :is_admin)
                """), {
                    "id": str(uuid.uuid4()),
                    "tenant_id": tenant_id,
                    "email": "admin@easeemail.com",
                    "full_name": "System Admin",
                    "role": "super_admin",
                    "password": "admin@123",  # Plain password as requested
                    "is_superadmin": True,
                    "is_admin": True
                })
                print("✅ User 1 (Super Admin) Created")

            # User 2 - Regular User
            result = await db.execute(text("SELECT * FROM users WHERE email = :email"), {"email": "user@easeemail.com"})
            if not result.first():
                await db.execute(text("""
                    INSERT INTO users (id, tenant_id, email, full_name, role, hashed_password)
                    VALUES (:id, :tenant_id, :email, :full_name, :role, :password)
                """), {
                    "id": str(uuid.uuid4()),
                    "tenant_id": tenant_id,
                    "email": "user@easeemail.com",
                    "full_name": "Regular User",
                    "role": "viewer",
                    "password": "hashed_secret_password"
                })
                print("✅ User 2 (Regular User) Created")

            # 3. Create Applications (2 total)
            # Application 1 - Main App
            result = await db.execute(text("SELECT * FROM applications WHERE name = :name"), {"name": "Main App"})
            if not result.first():
                app1_id = str(uuid.uuid4())
                await db.execute(text("""
                    INSERT INTO applications (id, tenant_id, name, api_key, status)
                    VALUES (:id, :tenant_id, :name, :api_key, :status)
                """), {
                    "id": app1_id,
                    "tenant_id": tenant_id,
                    "name": "Main App",
                    "api_key": "sk_live_" + str(uuid.uuid4().hex),
                    "status": "active"
                })
                print("✅ Application 1 Created")

            # Application 2 - Secondary App
            result = await db.execute(text("SELECT * FROM applications WHERE name = :name"), {"name": "Secondary App"})
            if not result.first():
                await db.execute(text("""
                    INSERT INTO applications (id, tenant_id, name, api_key, status)
                    VALUES (:id, :tenant_id, :name, :api_key, :status)
                """), {
                    "id": str(uuid.uuid4()),
                    "tenant_id": tenant_id,
                    "name": "Secondary App",
                    "api_key": "sk_live_" + str(uuid.uuid4().hex),
                    "status": "active"
                })
                print("✅ Application 2 Created")

            # 4. Create SMTP Configurations (2 total)
            # SMTP 1 - Mailtrap
            result = await db.execute(text("SELECT * FROM smtp_configurations WHERE host = :host"), {"host": "smtp.mailtrap.io"})
            if not result.first():
                smtp1_id = str(uuid.uuid4())
                await db.execute(text("""
                    INSERT INTO smtp_configurations (id, tenant_id, name, provider, host, port, username, password_encrypted, use_tls)
                    VALUES (:id, :tenant_id, :name, :provider, :host, :port, :username, :password, :use_tls)
                """), {
                    "id": smtp1_id,
                    "tenant_id": tenant_id,
                    "name": "Mailtrap Shared Account",
                    "provider": "custom",
                    "host": "smtp.mailtrap.io",
                    "port": 2525,
                    "username": "test_user",
                    "password": "test_pass",
                    "use_tls": True
                })
                print("✅ SMTP Config 1 Created")

            # SMTP 2 - Gmail
            result = await db.execute(text("SELECT * FROM smtp_configurations WHERE host = :host"), {"host": "smtp.gmail.com"})
            if not result.first():
                smtp2_id = str(uuid.uuid4())
                await db.execute(text("""
                    INSERT INTO smtp_configurations (id, tenant_id, name, provider, host, port, username, password_encrypted, use_tls)
                    VALUES (:id, :tenant_id, :name, :provider, :host, :port, :username, :password, :use_tls)
                """), {
                    "id": smtp2_id,
                    "tenant_id": tenant_id,
                    "name": "Gmail Account",
                    "provider": "gmail",
                    "host": "smtp.gmail.com",
                    "port": 587,
                    "username": "noreply@easeemail.com",
                    "password": "app_password_here",
                    "use_tls": True
                })
                print("✅ SMTP Config 2 Created")

            # 5. Create Templates (3 total)
            # Template 1 - Welcome Email
            result = await db.execute(text("SELECT * FROM email_templates WHERE name = :name"), {"name": "Welcome Email"})
            if not result.first():
                tmpl1_id = str(uuid.uuid4())
                await db.execute(text("""
                    INSERT INTO email_templates (id, tenant_id, name, subject_template, body_template)
                    VALUES (:id, :tenant_id, :name, :subject, :body)
                """), {
                    "id": tmpl1_id,
                    "tenant_id": tenant_id,
                    "name": "Welcome Email",
                    "subject": "Welcome to EaseEmail, {{name}}!",
                    "body": "<h1>Hello {{name}},</h1><p>Thanks for signing up.</p>"
                })
                print("✅ Template 1 Created")

            # Template 2 - Password Reset
            result = await db.execute(text("SELECT * FROM email_templates WHERE name = :name"), {"name": "Password Reset"})
            if not result.first():
                await db.execute(text("""
                    INSERT INTO email_templates (id, tenant_id, name, subject_template, body_template)
                    VALUES (:id, :tenant_id, :name, :subject, :body)
                """), {
                    "id": str(uuid.uuid4()),
                    "tenant_id": tenant_id,
                    "name": "Password Reset",
                    "subject": "Reset your password",
                    "body": "<h1>Password Reset</h1><p>Click here to reset: {{reset_link}}</p>"
                })
                print("✅ Template 2 Created")

            # Template 3 - Newsletter
            result = await db.execute(text("SELECT * FROM email_templates WHERE name = :name"), {"name": "Newsletter"})
            if not result.first():
                await db.execute(text("""
                    INSERT INTO email_templates (id, tenant_id, name, subject_template, body_template)
                    VALUES (:id, :tenant_id, :name, :subject, :body)
                """), {
                    "id": str(uuid.uuid4()),
                    "tenant_id": tenant_id,
                    "name": "Newsletter",
                    "subject": "Monthly Newsletter - {{month}}",
                    "body": "<h1>Newsletter</h1><p>{{content}}</p><p>Best regards,<br>Team</p>"
                })
                print("✅ Template 3 Created")

            # 6. Create Email Job and Log for dashboard stats
            # Get IDs for the relationships
            result = await db.execute(text("SELECT id FROM applications WHERE name = :name"), {"name": "Main App"})
            app_row = result.first()
            if app_row:
                app_id = app_row[0]

                result = await db.execute(text("SELECT id FROM email_templates WHERE name = :name"), {"name": "Welcome Email"})
                tmpl_row = result.first()
                if tmpl_row:
                    tmpl_id = tmpl_row[0]

                    result = await db.execute(text("SELECT id FROM smtp_configurations WHERE host = :host"), {"host": "smtp.mailtrap.io"})
                    smtp_row = result.first()
                    if smtp_row:
                        smtp_id = smtp_row[0]

                        # Create email service
                        svc_id = str(uuid.uuid4())
                        await db.execute(text("""
                            INSERT INTO email_services (id, tenant_id, name, from_email, template_id, status)
                            VALUES (:id, :tenant_id, :name, :from_email, :template_id, :status)
                        """), {
                            "id": svc_id,
                            "tenant_id": tenant_id,
                            "name": "Onboarding Service",
                            "from_email": "welcome@democorp.com",
                            "template_id": tmpl_id,
                            "status": "active"
                        })

                        # Create service configuration
                        await db.execute(text("""
                            INSERT INTO service_configurations (id, email_service_id, application_id, smtp_configuration_id, is_active)
                            VALUES (:id, :service_id, :app_id, :smtp_id, :is_active)
                        """), {
                            "id": str(uuid.uuid4()),
                            "service_id": svc_id,
                            "app_id": app_id,
                            "smtp_id": smtp_id,
                            "is_active": True
                        })

                        # Create email job
                        job_id = str(uuid.uuid4())
                        await db.execute(text("""
                            INSERT INTO email_jobs (id, service_id, to_email, subject, body, status)
                            VALUES (:id, :service_id, :to_email, :subject, :body, :status)
                        """), {
                            "id": job_id,
                            "service_id": svc_id,
                            "to_email": "john@example.com",
                            "subject": "Welcome to EmailEase",
                            "body": "<h1>Welcome!</h1><p>Thanks for joining.</p>",
                            "status": "sent"
                        })

                        # Create email log
                        await db.execute(text("""
                            INSERT INTO email_logs (id, job_id, status, response_code, response_message)
                            VALUES (:id, :job_id, :status, :response_code, :response_message)
                        """), {
                            "id": str(uuid.uuid4()),
                            "job_id": job_id,
                            "status": "sent",
                            "response_code": 250,
                            "response_message": "Message delivered successfully"
                        })

                        print("✅ Email Service, Job and Log Created")

            await db.commit()
            print("\n🚀 Database Seeded Successfully!")
            return {"message": "Database seeded successfully", "status": "success"}

    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        return {"message": f"Error seeding data: {str(e)}", "status": "error"}

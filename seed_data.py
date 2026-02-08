import asyncio
import sys
import os
import uuid
from sqlalchemy.future import select

# Add project root to path
sys.path.append(os.getcwd())

from app.db.session import AsyncSessionLocal
from app.models.all_models import Tenant, User, Application, SMTPConfiguration, EmailTemplate, EmailService, WebhookService, EmailJob, EmailLog

async def seed_async():
    async with AsyncSessionLocal() as db:
        try:
            print("🌱 Starting database seed...")
            
            # 1. Create Tenant
            result = await db.execute(select(Tenant).where(Tenant.name == "Demo Corp"))
            tenant = result.scalars().first()
            if not tenant:
                tenant = Tenant(name="Demo Corp")
                db.add(tenant)
                await db.commit()
                await db.refresh(tenant)
                print("✅ Tenant Created")
            
            # 2. Create Users (2 total)
            # User 1 - Super Admin
            result = await db.execute(select(User).where(User.email == "admin@easeemail.com"))
            user1 = result.scalars().first()
            if not user1:
                user1 = User(
                    tenant_id=tenant.id,
                    email="admin@easeemail.com",
                    full_name="System Admin",
                    role="super_admin",
                    hashed_password="hashed_secret_password"
                )
                db.add(user1)
                await db.commit()
                await db.refresh(user1)
                print("✅ User 1 (Super Admin) Created")

            # User 2 - Regular User
            result = await db.execute(select(User).where(User.email == "user@easeemail.com"))
            user2 = result.scalars().first()
            if not user2:
                user2 = User(
                    tenant_id=tenant.id,
                    email="user@easeemail.com",
                    full_name="Regular User",
                    role="viewer",
                    hashed_password="hashed_secret_password"
                )
                db.add(user2)
                await db.commit()
                print("✅ User 2 (Regular User) Created")

            # 3. Create Applications (2 total)
            # Application 1 - Main App
            result = await db.execute(select(Application).where(Application.name == "Main App"))
            app1 = result.scalars().first()
            if not app1:
                app1 = Application(
                    tenant_id=tenant.id,
                    name="Main App",
                    api_key="sk_live_" + str(uuid.uuid4().hex)
                )
                db.add(app1)
                await db.commit()
                await db.refresh(app1)
                print("✅ Application 1 Created")

            # Application 2 - Secondary App
            result = await db.execute(select(Application).where(Application.name == "Secondary App"))
            app2 = result.scalars().first()
            if not app2:
                app2 = Application(
                    tenant_id=tenant.id,
                    name="Secondary App",
                    api_key="sk_live_" + str(uuid.uuid4().hex)
                )
                db.add(app2)
                await db.commit()
                await db.refresh(app2)
                print("✅ Application 2 Created")

            # 4. Create SMTP Configurations (2 total)
            # SMTP 1 - Mailtrap
            result = await db.execute(select(SMTPConfiguration).where(SMTPConfiguration.host == "smtp.mailtrap.io"))
            smtp1 = result.scalars().first()
            if not smtp1:
                smtp1 = SMTPConfiguration(
                    tenant_id=tenant.id,
                    name="Mailtrap Shared Account",
                    provider="custom",
                    host="smtp.mailtrap.io",
                    port=2525,
                    username="test_user",
                    password_encrypted="test_pass",
                    use_tls=True
                )
                db.add(smtp1)
                await db.commit()
                await db.refresh(smtp1)
                print("✅ SMTP Config 1 Created")

            # SMTP 2 - Gmail
            result = await db.execute(select(SMTPConfiguration).where(SMTPConfiguration.host == "smtp.gmail.com"))
            smtp2 = result.scalars().first()
            if not smtp2:
                smtp2 = SMTPConfiguration(
                    tenant_id=tenant.id,
                    name="Gmail Account",
                    provider="gmail",
                    host="smtp.gmail.com",
                    port=587,
                    username="noreply@easeemail.com",
                    password_encrypted="app_password_here",
                    use_tls=True
                )
                db.add(smtp2)
                await db.commit()
                await db.refresh(smtp2)
                print("✅ SMTP Config 2 Created")

            # 5. Create Templates (3 total)
            # Template 1 - Welcome Email
            result = await db.execute(select(EmailTemplate).where(EmailTemplate.name == "Welcome Email"))
            tmpl1 = result.scalars().first()
            if not tmpl1:
                tmpl1 = EmailTemplate(
                    tenant_id=tenant.id,
                    name="Welcome Email",
                    subject_template="Welcome to EaseEmail, {{name}}!",
                    body_template="<h1>Hello {{name}},</h1><p>Thanks for signing up.</p>"
                )
                db.add(tmpl1)
                await db.commit()
                await db.refresh(tmpl1)
                print("✅ Template 1 Created")

            # Template 2 - Password Reset
            result = await db.execute(select(EmailTemplate).where(EmailTemplate.name == "Password Reset"))
            tmpl2 = result.scalars().first()
            if not tmpl2:
                tmpl2 = EmailTemplate(
                    tenant_id=tenant.id,
                    name="Password Reset",
                    subject_template="Reset your password",
                    body_template="<h1>Password Reset</h1><p>Click here to reset: {{reset_link}}</p>"
                )
                db.add(tmpl2)
                await db.commit()
                await db.refresh(tmpl2)
                print("✅ Template 2 Created")

            # Template 3 - Newsletter
            result = await db.execute(select(EmailTemplate).where(EmailTemplate.name == "Newsletter"))
            tmpl3 = result.scalars().first()
            if not tmpl3:
                tmpl3 = EmailTemplate(
                    tenant_id=tenant.id,
                    name="Newsletter",
                    subject_template="Monthly Newsletter - {{month}}",
                    body_template="<h1>Newsletter</h1><p>{{content}}</p><p>Best regards,<br>Team</p>"
                )
                db.add(tmpl3)
                await db.commit()
                await db.refresh(tmpl3)
                print("✅ Template 3 Created")

            # 6. Create Email Service
            result = await db.execute(select(EmailService).where(EmailService.name == "Onboarding Service"))
            svc = result.scalars().first()
            if not svc:
                svc = EmailService(
                    tenant_id=tenant.id,
                    name="Onboarding Service",
                    template_id=tmpl1.id
                )
                db.add(svc)
                await db.commit()
                await db.refresh(svc)

                # Create service configuration linking app and SMTP
                from app.models.all_models import ServiceConfiguration
                svc_config = ServiceConfiguration(
                    email_service_id=svc.id,
                    application_id=app1.id,
                    smtp_configuration_id=smtp1.id
                )
                db.add(svc_config)
                await db.commit()
                print("✅ Email Service Created")

            # 7. Create Webhook
            result = await db.execute(select(WebhookService).where(WebhookService.name == "Slack Alert"))
            hook = result.scalars().first()
            if not hook:
                hook = WebhookService(
                    application_id=app1.id,
                    name="Slack Alert",
                    target_url="https://hooks.slack.com/services/xxx/yyy/zzz",
                    event_type="email.failed"
                )
                db.add(hook)
                await db.commit()
                print("✅ Webhook Created")

            # 8. Create Email Job and Log for dashboard stats
            # Create a sample email job
            job = EmailJob(
                service_id=svc.id,
                to_email="john@example.com",
                subject="Welcome to EmailEase",
                body="<h1>Welcome!</h1><p>Thanks for joining.</p>",
                status="sent"
            )
            db.add(job)
            await db.commit()
            await db.refresh(job)

            # Create email log entry
            log = EmailLog(
                job_id=job.id,
                status="sent",
                response_code=250,
                response_message="Message delivered successfully"
            )
            db.add(log)
            await db.commit()
            print("✅ Email Job and Log Created")

            print("\n🚀 Database Seeded Successfully!")

        except Exception as e:
            print(f"❌ Error seeding data: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(seed_async())

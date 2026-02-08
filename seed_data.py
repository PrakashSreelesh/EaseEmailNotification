import asyncio
import sys
import os
import uuid
from sqlalchemy.future import select

# Add project root to path
sys.path.append(os.getcwd())

from app.db.session import AsyncSessionLocal
from app.models.all_models import Tenant, User, Application, SMTPConfiguration, EmailTemplate, EmailService, WebhookService

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
            
            # 2. Create User
            result = await db.execute(select(User).where(User.email == "admin@easeemail.com"))
            user = result.scalars().first()
            if not user:
                user = User(
                    tenant_id=tenant.id,
                    email="admin@easeemail.com",
                    full_name="System Admin",
                    role="super_admin",
                    hashed_password="hashed_secret_password" 
                )
                db.add(user)
                await db.commit()
                print("✅ User Created")

            # 3. Create Application
            result = await db.execute(select(Application).where(Application.name == "Main App"))
            app = result.scalars().first()
            if not app:
                app = Application(
                    tenant_id=tenant.id,
                    name="Main App",
                    api_key="sk_live_" + str(uuid.uuid4().hex)
                )
                db.add(app)
                await db.commit()
                await db.refresh(app)
                print("✅ Application Created")

            # 4. Create SMTP Config
            result = await db.execute(select(SMTPConfiguration).where(SMTPConfiguration.host == "smtp.mailtrap.io"))
            smtp = result.scalars().first()
            if not smtp:
                smtp = SMTPConfiguration(
                    tenant_id=tenant.id,
                    name="Mailtrap Shared Account",
                    provider="custom",
                    host="smtp.mailtrap.io",
                    port=2525,
                    username="test_user",
                    password_encrypted="test_pass",
                    use_tls=True
                )
                db.add(smtp)
                await db.commit()
                await db.refresh(smtp)
                print("✅ SMTP Config Created")

            # 5. Create Template
            result = await db.execute(select(EmailTemplate).where(EmailTemplate.name == "Welcome Email"))
            tmpl = result.scalars().first()
            if not tmpl:
                tmpl = EmailTemplate(
                    tenant_id=tenant.id,
                    name="Welcome Email",
                    subject_template="Welcome to EaseEmail, {{name}}!",
                    body_template="<h1>Hello {{name}},</h1><p>Thanks for signing up.</p>"
                )
                db.add(tmpl)
                await db.commit()
                await db.refresh(tmpl)
                print("✅ Template Created")

            # 6. Create Email Service
            result = await db.execute(select(EmailService).where(EmailService.name == "Onboarding Service"))
            svc = result.scalars().first()
            if not svc:
                svc = EmailService(
                    application_id=app.id,
                    name="Onboarding Service",
                    from_email="welcome@democorp.com",
                    smtp_configuration_id=smtp.id,
                    template_id=tmpl.id
                )
                db.add(svc)
                await db.commit()
                print("✅ Email Service Created")

            # 7. Create Webhook
            result = await db.execute(select(WebhookService).where(WebhookService.name == "Slack Alert"))
            hook = result.scalars().first()
            if not hook:
                hook = WebhookService(
                    application_id=app.id,
                    name="Slack Alert",
                    target_url="https://hooks.slack.com/services/xxx/yyy/zzz",
                    event_type="email.failed"
                )
                db.add(hook)
                await db.commit()
                print("✅ Webhook Created")

            print("\n🚀 Database Seeded Successfully!")

        except Exception as e:
            print(f"❌ Error seeding data: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(seed_async())

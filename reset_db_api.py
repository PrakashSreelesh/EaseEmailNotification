#!/usr/bin/env python3
"""
Script to reset the database schema and seed with data.
This can be called via API endpoint or run directly.
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

async def reset_and_seed():
    """Reset database and seed with data"""
    try:
        from app.db.session import engine
        from app.models.all_models import Base

        # Reset database schema
        async with engine.begin() as conn:
            print("🗑️ Dropping all tables...")
            await conn.run_sync(Base.metadata.drop_all)
            print("✨ Creating all tables...")
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Tables recreated successfully.")

        # Seed the database
        from app.db.session import AsyncSessionLocal
        from app.models.all_models import Tenant, User, Application, SMTPConfiguration, EmailTemplate, EmailService, ServiceConfiguration, WebhookService, EmailJob, EmailLog
        import uuid

        async with AsyncSessionLocal() as db:
            print("🌱 Starting database seed...")

            # 1. Create Tenant
            result = await db.execute("SELECT * FROM tenants WHERE name = 'Demo Corp'")
            if not result.first():
                await db.execute("INSERT INTO tenants (id, name) VALUES ($1, $2)", str(uuid.uuid4()), "Demo Corp")
                print("✅ Tenant Created")

            # Get tenant id
            result = await db.execute("SELECT id FROM tenants WHERE name = 'Demo Corp'")
            tenant_row = result.first()
            tenant_id = tenant_row[0]

            # 2. Create Users (2 total)
            # User 1 - Super Admin
            result = await db.execute("SELECT * FROM users WHERE email = 'admin@easeemail.com'")
            if not result.first():
                await db.execute("""
                    INSERT INTO users (id, tenant_id, email, full_name, role, hashed_password, is_superadmin, is_admin)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """, str(uuid.uuid4()), tenant_id, "admin@easeemail.com", "System Admin", "super_admin", "hashed_secret_password", True, True)
                print("✅ User 1 (Super Admin) Created")

            # User 2 - Regular User
            result = await db.execute("SELECT * FROM users WHERE email = 'user@easeemail.com'")
            if not result.first():
                await db.execute("""
                    INSERT INTO users (id, tenant_id, email, full_name, role, hashed_password)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """, str(uuid.uuid4()), tenant_id, "user@easeemail.com", "Regular User", "viewer", "hashed_secret_password")
                print("✅ User 2 (Regular User) Created")

            # 3. Create Applications (2 total)
            # Application 1 - Main App
            result = await db.execute("SELECT * FROM applications WHERE name = 'Main App'")
            if not result.first():
                app1_id = str(uuid.uuid4())
                await db.execute("""
                    INSERT INTO applications (id, tenant_id, name, api_key, status)
                    VALUES ($1, $2, $3, $4, $5)
                """, app1_id, tenant_id, "Main App", "sk_live_" + str(uuid.uuid4().hex), "active")
                print("✅ Application 1 Created")

            # Application 2 - Secondary App
            result = await db.execute("SELECT * FROM applications WHERE name = 'Secondary App'")
            if not result.first():
                app2_id = str(uuid.uuid4())
                await db.execute("""
                    INSERT INTO applications (id, tenant_id, name, api_key, status)
                    VALUES ($1, $2, $3, $4, $5)
                """, app2_id, tenant_id, "Secondary App", "sk_live_" + str(uuid.uuid4().hex), "active")
                print("✅ Application 2 Created")

            # 4. Create SMTP Configurations (2 total)
            # SMTP 1 - Mailtrap
            result = await db.execute("SELECT * FROM smtp_configurations WHERE host = 'smtp.mailtrap.io'")
            if not result.first():
                smtp1_id = str(uuid.uuid4())
                await db.execute("""
                    INSERT INTO smtp_configurations (id, tenant_id, name, provider, host, port, username, password_encrypted, use_tls)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """, smtp1_id, tenant_id, "Mailtrap Shared Account", "custom", "smtp.mailtrap.io", 2525, "test_user", "test_pass", True)
                print("✅ SMTP Config 1 Created")

            # SMTP 2 - Gmail
            result = await db.execute("SELECT * FROM smtp_configurations WHERE host = 'smtp.gmail.com'")
            if not result.first():
                smtp2_id = str(uuid.uuid4())
                await db.execute("""
                    INSERT INTO smtp_configurations (id, tenant_id, name, provider, host, port, username, password_encrypted, use_tls)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """, smtp2_id, tenant_id, "Gmail Account", "gmail", "smtp.gmail.com", 587, "noreply@easeemail.com", "app_password_here", True)
                print("✅ SMTP Config 2 Created")

            # 5. Create Templates (3 total)
            # Template 1 - Welcome Email
            result = await db.execute("SELECT * FROM email_templates WHERE name = 'Welcome Email'")
            if not result.first():
                tmpl1_id = str(uuid.uuid4())
                await db.execute("""
                    INSERT INTO email_templates (id, tenant_id, name, subject_template, body_template)
                    VALUES ($1, $2, $3, $4, $5)
                """, tmpl1_id, tenant_id, "Welcome Email", "Welcome to EaseEmail, {{name}}!", "<h1>Hello {{name}},</h1><p>Thanks for signing up.</p>")
                print("✅ Template 1 Created")

            # Template 2 - Password Reset
            result = await db.execute("SELECT * FROM email_templates WHERE name = 'Password Reset'")
            if not result.first():
                tmpl2_id = str(uuid.uuid4())
                await db.execute("""
                    INSERT INTO email_templates (id, tenant_id, name, subject_template, body_template)
                    VALUES ($1, $2, $3, $4, $5)
                """, tmpl2_id, tenant_id, "Password Reset", "Reset your password", "<h1>Password Reset</h1><p>Click here to reset: {{reset_link}}</p>")
                print("✅ Template 2 Created")

            # Template 3 - Newsletter
            result = await db.execute("SELECT * FROM email_templates WHERE name = 'Newsletter'")
            if not result.first():
                tmpl3_id = str(uuid.uuid4())
                await db.execute("""
                    INSERT INTO email_templates (id, tenant_id, name, subject_template, body_template)
                    VALUES ($1, $2, $3, $4, $5)
                """, tmpl3_id, tenant_id, "Newsletter", "Monthly Newsletter - {{month}}", "<h1>Newsletter</h1><p>{{content}}</p><p>Best regards,<br>Team</p>")
                print("✅ Template 3 Created")

            # 6. Create Email Service, Job and Log for dashboard stats
            # Get IDs for the relationships
            result = await db.execute("SELECT id FROM applications WHERE name = 'Main App'")
            app_row = result.first()
            if app_row:
                app_id = app_row[0]

                result = await db.execute("SELECT id FROM email_templates WHERE name = 'Welcome Email'")
                tmpl_row = result.first()
                if tmpl_row:
                    tmpl_id = tmpl_row[0]

                    result = await db.execute("SELECT id FROM smtp_configurations WHERE host = 'smtp.mailtrap.io'")
                    smtp_row = result.first()
                    if smtp_row:
                        smtp_id = smtp_row[0]

                        # Create email service
                        svc_id = str(uuid.uuid4())
                        await db.execute("""
                            INSERT INTO email_services (id, tenant_id, name, from_email, template_id, status)
                            VALUES ($1, $2, $3, $4, $5, $6)
                        """, svc_id, tenant_id, "Onboarding Service", "welcome@democorp.com", tmpl_id, "active")

                        # Create service configuration
                        await db.execute("""
                            INSERT INTO service_configurations (id, email_service_id, application_id, smtp_configuration_id, is_active)
                            VALUES ($1, $2, $3, $4, $5)
                        """, str(uuid.uuid4()), svc_id, app_id, smtp_id, True)

                        # Create email job
                        job_id = str(uuid.uuid4())
                        await db.execute("""
                            INSERT INTO email_jobs (id, service_id, to_email, subject, body, status)
                            VALUES ($1, $2, $3, $4, $5, $6)
                        """, job_id, svc_id, "john@example.com", "Welcome to EmailEase", "<h1>Welcome!</h1><p>Thanks for joining.</p>", "sent")

                        # Create email log
                        await db.execute("""
                            INSERT INTO email_logs (id, job_id, status, response_code, response_message)
                            VALUES ($1, $2, $3, $4, $5)
                        """, str(uuid.uuid4()), job_id, "sent", 250, "Message delivered successfully")

                        print("✅ Email Service, Job and Log Created")

            await db.commit()
            print("\n🚀 Database reset and seeded successfully!")
            return {"message": "Database reset and seeded successfully", "status": "success"}

    except Exception as e:
        print(f"❌ Error: {e}")
        return {"message": f"Error: {str(e)}", "status": "error"}

if __name__ == "__main__":
    asyncio.run(reset_and_seed())
import logging
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.all_models import Application, EmailService, ServiceConfiguration, EmailTemplate, SMTPConfiguration, EmailJob, EmailLog
from app.core.security import decrypt_password
from jinja2 import Template as JinjaTemplate
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import HTTPException
import json

logger = logging.getLogger(__name__)

class EmailSenderService:
    @staticmethod
    async def send(
        db: Session,
        api_key: str,
        service_name: str,
        template_name: str,
        to_email: str,
        variables_data: dict
    ):
        # Step 1: Authenticate application
        logger.info(f"Authenticating application with API Key prefix: {api_key[:5]}...")
        result = await db.execute(select(Application).where(Application.api_key == api_key))
        application = result.scalars().first()
        if not application:
            logger.warning("Authentication failed: Invalid API key")
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        tenant_id = application.tenant_id

        # Step 2: Get email service
        logger.info(f"Fetching email service: {service_name} for tenant: {tenant_id}")
        result = await db.execute(
            select(EmailService).where(
                EmailService.name == service_name,
                EmailService.status == "active",
                EmailService.tenant_id == tenant_id
            )
        )
        service = result.scalars().first()
        if not service:
            logger.error(f"Invalid email service: {service_name}")
            raise HTTPException(status_code=400, detail="Invalid email service")

        # Step 3: Get SMTP configuration
        logger.info(f"Fetching active SMTP configuration for app: {application.id}")
        result = await db.execute(
            select(ServiceConfiguration).where(
                ServiceConfiguration.email_service_id == service.id,
                ServiceConfiguration.application_id == application.id,
                ServiceConfiguration.is_active == True
            )
        )
        config = result.scalars().first()
        if not config:
            logger.error("No active SMTP configuration found for this application and service")
            raise HTTPException(status_code=400, detail="No active SMTP configuration")

        result = await db.execute(select(SMTPConfiguration).where(SMTPConfiguration.id == config.smtp_configuration_id))
        smtp = result.scalars().first()
        if not smtp:
            logger.error("SMTP account details not found in database")
            raise HTTPException(status_code=400, detail="SMTP account details not found")

        # Step 4: Get template
        logger.info(f"Fetching template: {template_name} for tenant: {tenant_id}")
        result = await db.execute(
            select(EmailTemplate).where(
                EmailTemplate.name == template_name,
                EmailTemplate.tenant_id == tenant_id
            )
        )
        template = result.scalars().first()
        if not template:
            logger.error(f"Template not found: {template_name}")
            raise HTTPException(status_code=404, detail="Template not found")

        # Step 5: Render template
        logger.info("Rendering template subject and body")
        try:
            subject_tmpl = JinjaTemplate(template.subject_template)
            body_tmpl = JinjaTemplate(template.body_template)
            
            rendered_subject = subject_tmpl.render(**variables_data)
            rendered_body = body_tmpl.render(**variables_data)
        except Exception as e:
            logger.error(f"Template rendering error: {str(e)}")
            raise HTTPException(status_code=400, detail="Template rendering error")

        # Create Job for logging
        job = EmailJob(
            service_id=service.id,
            to_email=to_email,
            subject=rendered_subject,
            body=rendered_body,
            status="processing"
        )
        db.add(job)
        await db.flush()

        # Step 6: Send email
        logger.info(f"Sending email to {to_email} via {smtp.host}")
        try:
            password = decrypt_password(smtp.password_encrypted)
            
            message = MIMEMultipart("alternative")
            message["From"] = smtp.username
            message["To"] = to_email
            message["Subject"] = rendered_subject
            message.attach(MIMEText(rendered_body, "html"))

            use_implicit_tls = (smtp.port == 465)
            await aiosmtplib.send(
                message,
                hostname=smtp.host,
                port=smtp.port,
                username=smtp.username,
                password=password,
                use_tls=use_implicit_tls,
                start_tls=not use_implicit_tls and smtp.use_tls
            )
            
            job.status = "sent"
            log = EmailLog(job_id=job.id, status="sent", response_code=200, response_message="OK")
            db.add(log)
            await db.commit()
            
            logger.info("Email sent successfully")
            return {"status": "success", "message": "Email sent successfully"}
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to send email: {error_msg}")
            job.status = "failed"
            job.error_message = error_msg
            log = EmailLog(job_id=job.id, status="failed", response_code=500, response_message=error_msg)
            db.add(log)
            await db.commit()
            raise HTTPException(status_code=500, detail=f"Failed to send email: {error_msg}")

"""
Email Sender Service - Queue jobs for async processing.

This service validates requests and queues email jobs for worker processing.
CRITICAL: This does NOT send emails synchronously - it returns immediately with job_id.
"""

import logging
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jinja2 import Template as JinjaTemplate
from fastapi import HTTPException

from app.models.all_models import (
    Application, EmailService, ServiceConfiguration, 
    EmailTemplate, SMTPConfiguration, EmailJob
)
from app.worker.celery_config import celery_app

logger = logging.getLogger(__name__)


class EmailSenderService:
    @staticmethod
    async def validate_and_queue(
        db: AsyncSession,
        api_key: str,
        service_name: str,
        template_name: str,
        to_email: str,
        variables_data: dict
    ) -> dict:
        """
        Validate email request and queue for async delivery.
        
        This method:
        1. Authenticates application via API key
        2. Validates service, template, SMTP config
        3. Renders template
        4. Creates EmailJob (status: queued)
        5. Enqueues to Celery
        6. Returns job_id immediately (< 200ms)
        
        Args:
            db: Async database session
            api_key: Application API key
            service_name: EmailService name
            template_name: EmailTemplate name
            to_email: Recipient email
            variables_data: Template variables
            
        Returns:
            dict with job_id, status, message
            
        Raises:
            HTTPException: 401 (auth), 400 (validation), 404 (not found)
        """
        # ========================================
        # 1. Authenticate application
        # ========================================
        logger.info(f"Authenticating with API key prefix: {api_key[:8]}...")
        result = await db.execute(
            select(Application).where(Application.api_key == api_key)
        )
        application = result.scalars().first()
        
        if not application:
            logger.warning("Authentication failed: Invalid API key")
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        tenant_id = application.tenant_id
        
        # ========================================
        # 2. Get email service
        # ========================================
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
        
        # ========================================
        # 3. Validate SMTP configuration exists
        # ========================================
        logger.info(f"Validating SMTP config for app: {application.id}")
        result = await db.execute(
            select(ServiceConfiguration).where(
                ServiceConfiguration.email_service_id == service.id,
                ServiceConfiguration.application_id == application.id,
                ServiceConfiguration.is_active == True
            )
        )
        config = result.scalars().first()
        
        if not config:
            logger.error("No active SMTP configuration found")
            raise HTTPException(status_code=400, detail="No active SMTP configuration")
        
        result = await db.execute(
            select(SMTPConfiguration).where(SMTPConfiguration.id == config.smtp_configuration_id)
        )
        smtp = result.scalars().first()
        
        if not smtp:
            logger.error("SMTP account details not found")
            raise HTTPException(status_code=400, detail="SMTP account details not found")
        
        # ========================================
        # 4. Get and validate template
        # ========================================
        logger.info(f"Fetching template: {template_name}")
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
        
        # ========================================
        # 5. Render template
        # ========================================
        logger.info("Rendering template")
        try:
            subject_tmpl = JinjaTemplate(template.subject_template)
            body_tmpl = JinjaTemplate(template.body_template)
            
            rendered_subject = subject_tmpl.render(**variables_data)
            rendered_body = body_tmpl.render(**variables_data)
        except Exception as e:
            logger.error(f"Template rendering error: {e}")
            raise HTTPException(status_code=400, detail=f"Template rendering error: {e}")
        
        # ========================================
        # 6. Create EmailJob (status: queued)
        # ========================================
        job = EmailJob(
            service_id=service.id,
            tenant_id=tenant_id,
            application_id=application.id,
            to_email=to_email,
            subject=rendered_subject,
            body=rendered_body,
            status="queued"  # NOT processing - queued for worker
        )
        db.add(job)
        await db.flush()  # Get job.id
        
        job_id = str(job.id)
        
        # ========================================
        # 7. Enqueue to Celery
        # ========================================
        try:
            from app.worker.tasks import send_email_task
            send_email_task.delay(job_id)
            
            logger.info(f"Email queued: job_id={job_id}, to={to_email}")
        except Exception as e:
            logger.error(f"Failed to enqueue job: {e}")
            job.status = "failed"
            job.error_message = f"Failed to enqueue: {e}"
            await db.commit()
            raise HTTPException(status_code=500, detail="Failed to queue email")
        
        # ========================================
        # 8. Commit and return
        # ========================================
        await db.commit()
        
        return {
            "job_id": job_id,
            "status": "queued",
            "message": "Email queued for delivery",
        }

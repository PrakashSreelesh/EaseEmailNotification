import asyncio
import uuid
import logging
import json
from celery import Celery
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.all_models import EmailJob, EmailService, EmailLog
from app.schemas.schemas import EmailSendRequest
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from sqlalchemy.orm import joinedload
from jinja2 import Template
import aiosmtplib

# Celery Setup
celery_app = Celery("fullstack_worker", broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_BROKER_URL)

logger = logging.getLogger(__name__)

async def send_email_async(job_id: str):
    db = SessionLocal()
    try:
        # Fetch Job
        job = db.query(EmailJob).filter(EmailJob.id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found")
            return

        job.status = "processing"
        db.commit()

        # Fetch Service & Config with relationships
        service = db.query(EmailService).options(
            joinedload(EmailService.template),
            joinedload(EmailService.smtp_configuration)
        ).filter(EmailService.id == job.service_id).first()
        if not service:
            raise Exception("Email Service not found")

        # Determine Credentials (Legacy vs Linked Config)
        if service.smtp_configuration:
            smtp_host = service.smtp_configuration.host
            smtp_port = service.smtp_configuration.port
            smtp_user = service.smtp_configuration.username
            smtp_pass = service.smtp_configuration.password_encrypted # Decrypt in real app!
            use_tls = service.smtp_configuration.use_tls
        else:
            smtp_host = service.smtp_host
            smtp_port = service.smtp_port
            smtp_user = service.smtp_user
            smtp_pass = service.smtp_password
            use_tls = True # Default

        # Determine Content (Template vs Direct)
        subject = job.subject
        body = job.body

        if service.template:
            # Simple Jinja2 rendering if body is JSON
            try:
                data = json.loads(job.body) if job.body and job.body.startswith('{') else {}
            except:
                data = {}

            # Render Subject
            if service.template.subject_template:
                 subject_tmpl = Template(service.template.subject_template)
                 subject = subject_tmpl.render(data)
            
            # Render Body
            if service.template.body_template:
                body_tmpl = Template(service.template.body_template)
                body = body_tmpl.render(data)

        # Construct Email
        message = MIMEMultipart("alternative")
        message["From"] = service.from_email
        message["To"] = job.to_email
        message["Subject"] = subject
        
        # Attach HTML part
        message.attach(MIMEText(body, "html"))

        # Send via SMTP
        use_implicit_tls = (smtp_port == 465)
        await aiosmtplib.send(
            message,
            hostname=smtp_host,
            port=smtp_port,
            username=smtp_user,
            password=smtp_pass,
            use_tls=use_implicit_tls,
            start_tls=not use_implicit_tls and use_tls
        )

        # Update Job Success
        job.status = "sent"
        
        # Create Log
        log = EmailLog(job_id=job.id, status="sent", response_code=200, response_message="OK")
        db.add(log)
        db.commit()
        logger.info(f"Email sent successfully for job {job_id}")

    except Exception as e:
        logger.error(f"Failed to send email for job {job_id}: {str(e)}")
        job.status = "failed"
        job.error_message = str(e)
        
        # Create Error Log
        log = EmailLog(job_id=job.id, status="failed", response_code=500, response_message=str(e))
        db.add(log)
        db.commit()
    finally:
        db.close()

@celery_app.task(name="send_email_task")
def send_email_task(job_id: str):
    """
    Wrapper to run async function in Celery sync worker
    """
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    loop.run_until_complete(send_email_async(job_id))

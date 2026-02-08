"""
Synchronous SMTP email sending.

This module handles actual email delivery via SMTP using the synchronous smtplib.
CRITICAL: Uses sync smtplib, NOT aiosmtplib, to avoid event loop issues in Celery workers.
"""

import smtplib
import socket
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from sqlalchemy.orm import Session

from app.models.all_models import EmailJob, SMTPConfiguration, ServiceConfiguration
from app.core.security import decrypt_password
from app.worker.exceptions import PermanentFailure, TemporaryFailure, PERMANENT_SMTP_CODES, TEMPORARY_SMTP_CODES

logger = logging.getLogger(__name__)


def send_via_smtp(job: EmailJob, db: Session):
    """
    Send email via SMTP synchronously.
    
    This function:
    1. Fetches SMTP configuration
    2. Decrypts password
    3. Builds MIME message
    4. Sends via smtplib (SYNC)
    5. Classifies errors as permanent or temporary
    
    Args:
        job: EmailJob instance with populated service_id and application_id
        db: Database session
        
    Raises:
        PermanentFailure: Non-retryable error (bad recipient, auth failure)
        TemporaryFailure: Retryable error (connection timeout, rate limit)
    """
    # Fetch SMTP config via service configuration
    config = _get_smtp_config(job, db)
    
    if not config:
        raise PermanentFailure("No SMTP configuration found for this job")
    
    # Decrypt password
    try:
        password = decrypt_password(config.password_encrypted)
    except Exception as e:
        logger.error(f"Failed to decrypt SMTP password: {e}")
        raise PermanentFailure(f"Password decryption failed: {e}")
    
    # Build MIME message
    message = MIMEMultipart("alternative")
    message["From"] = config.username
    message["To"] = job.to_email
    message["Subject"] = job.subject or "No Subject"
    message.attach(MIMEText(job.body or "", "html"))
    
    try:
        # Create SMTP connection based on port
        if config.port == 465:
            # Implicit TLS (SMTP_SSL)
            logger.debug(f"Connecting to {config.host}:465 with implicit TLS")
            server = smtplib.SMTP_SSL(config.host, config.port, timeout=30)
        else:
            # STARTTLS
            logger.debug(f"Connecting to {config.host}:{config.port} with STARTTLS")
            server = smtplib.SMTP(config.host, config.port, timeout=30)
            if config.use_tls:
                server.starttls()
        
        # Login
        server.login(config.username, password)
        
        # Send email
        server.sendmail(config.username, job.to_email, message.as_string())
        
        # Quit
        server.quit()
        
        logger.info(
            f"Email sent successfully: job_id={job.id}, to={job.to_email}",
            extra={"job_id": str(job.id), "to_email": job.to_email}
        )
        
    except smtplib.SMTPRecipientsRefused as e:
        # Permanent: bad recipient
        logger.warning(f"Recipient refused: {e}")
        raise PermanentFailure(f"Recipient refused: {e}")
        
    except smtplib.SMTPAuthenticationError as e:
        # Permanent: bad credentials (system configuration issue)
        logger.critical(f"SMTP auth failed for config {config.id}: {e}")
        raise PermanentFailure(f"Authentication failed: {e}")
        
    except smtplib.SMTPResponseException as e:
        # Classify by SMTP code
        if e.smtp_code in PERMANENT_SMTP_CODES:
            logger.warning(f"Permanent SMTP error {e.smtp_code}: {e.smtp_error}")
            raise PermanentFailure(f"SMTP {e.smtp_code}: {e.smtp_error}")
        elif e.smtp_code in TEMPORARY_SMTP_CODES:
            logger.info(f"Temporary SMTP error {e.smtp_code}: {e.smtp_error}")
            raise TemporaryFailure(f"SMTP {e.smtp_code}: {e.smtp_error}")
        else:
            # Unknown code, treat as temporary to be safe
            logger.warning(f"Unknown SMTP error {e.smtp_code}: {e.smtp_error}")
            raise TemporaryFailure(f"SMTP {e.smtp_code}: {e.smtp_error}")
        
    except (socket.timeout, ConnectionError, OSError) as e:
        # Network issues are temporary
        logger.warning(f"Network error: {e}")
        raise TemporaryFailure(f"Connection error: {e}")
        
    except Exception as e:
        # Unexpected error, treat as temporary
        logger.error(f"Unexpected SMTP error: {e}", exc_info=True)
        raise TemporaryFailure(f"Unexpected error: {e}")


def _get_smtp_config(job: EmailJob, db: Session) -> SMTPConfiguration:
    """
    Fetch SMTP configuration for a job.
    
    Lookup path:
    EmailJob -> EmailService -> ServiceConfiguration -> SMTPConfiguration
    """
    from sqlalchemy import select
    
    # Get active service configuration for this job
    service_config = db.execute(
        select(ServiceConfiguration).where(
            ServiceConfiguration.email_service_id == job.service_id,
            ServiceConfiguration.application_id == job.application_id,
            ServiceConfiguration.is_active == True
        )
    ).scalars().first()
    
    if not service_config:
        logger.error(f"No active service configuration found for job {job.id}")
        return None
    
    # Get SMTP configuration
    smtp_config = db.execute(
        select(SMTPConfiguration).where(
            SMTPConfiguration.id == service_config.smtp_configuration_id
        )
    ).scalars().first()
    
    if not smtp_config:
        logger.error(f"SMTP configuration {service_config.smtp_configuration_id} not found")
        return None
    
    return smtp_config

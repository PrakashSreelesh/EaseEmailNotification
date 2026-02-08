"""
Webhook dispatcher for email status callbacks.

This module handles queuing webhook delivery tasks after email completion.
CRITICAL: This NEVER blocks email sending - webhooks are fire-and-forget.
"""

import logging
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.all_models import Application, WebhookDelivery, EmailJob, EmailService
from app.schemas.webhook_schemas import WebhookPayload

logger = logging.getLogger(__name__)


def queue_webhook_if_configured(
    db: Session,
    job: EmailJob,
    final_status: str,
    error_info: Optional[dict] = None
):
    """
    Check if application has webhook configured and queue delivery.
    
    CRITICAL: This runs inside the email worker but does NOT block.
    It only creates a WebhookDelivery record and enqueues a task.
    
    Args:
        db: Database session
        job: Completed EmailJob
        final_status: "sent" or "failed"
        error_info: Optional dict with "category" and "message" for failures
    """
    # Import here to avoid circular dependency
    from app.worker.webhook_tasks import deliver_webhook_task
    
    # Fetch application config
    application = db.execute(
        select(Application).where(Application.id == job.application_id)
    ).scalars().first()
    
    if not application:
        logger.warning(f"Application {job.application_id} not found for webhook")
        return
    
    # Check if webhook is enabled
    if not application.webhook_enabled or not application.webhook_url:
        logger.debug(f"Webhook not configured for application {application.id}")
        return
    
    # Check if this event type should trigger webhook
    event_type = "email.sent" if final_status == "sent" else "email.failed"
    allowed_events = application.webhook_events or []
    
    if event_type not in allowed_events:
        logger.debug(f"Event {event_type} not in allowed events for {application.id}")
        return
    
    # Fetch service name
    service = db.execute(
        select(EmailService).where(EmailService.id == job.service_id)
    ).scalars().first()
    service_name = service.name if service else "Unknown"
    
    # Build payload
    payload = WebhookPayload(
        event=event_type,
        timestamp=datetime.utcnow(),
        job_id=job.id,
        tenant_id=job.tenant_id,
        application_id=job.application_id,
        service_name=service_name,
        to_email=job.to_email,
        subject=job.subject,
        status=final_status,
        sent_at=job.sent_at,
        error_category=error_info.get("category") if error_info else None,
        error_message=error_info.get("message") if error_info else None,
        retry_count=job.retry_count,
    )
    
    # Create WebhookDelivery record
    delivery = WebhookDelivery(
        email_job_id=job.id,
        application_id=job.application_id,
        tenant_id=job.tenant_id,
        webhook_url=application.webhook_url,  # Snapshot URL at queue time
        event_type=event_type,
        payload=payload.model_dump(mode="json"),
        status="pending",
    )
    db.add(delivery)
    db.flush()  # Get ID
    
    # Mark job as having webhook requested
    job.webhook_requested = True
    
    # Enqueue webhook task (separate queue)
    try:
        deliver_webhook_task.delay(str(delivery.id))
        
        logger.info(
            f"Webhook queued: delivery_id={delivery.id}, job_id={job.id}, event={event_type}",
            extra={
                "delivery_id": str(delivery.id),
                "job_id": str(job.id),
                "event_type": event_type
            }
        )
    except Exception as e:
        # Webhook queuing failed, but email is already sent - just log
        logger.error(f"Failed to queue webhook task: {e}", exc_info=True)
        delivery.status = "failed"
        delivery.last_error = f"Failed to queue: {e}"

"""
Job status endpoint for polling email delivery status.

This endpoint allows clients to poll the status of queued/processing email jobs.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.db.session import get_db
from app.models.all_models import EmailJob, WebhookDelivery
from app.schemas import schemas
from app.schemas.webhook_schemas import WebhookDeliveryStatus

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/{job_id}", response_model=schemas.EmailJobStatusResponse)
async def get_job_status(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get email job status by ID.
    
    Returns detailed status including:
    - Current status (queued, processing, sent, failed)
    - Timing information
    - Error details if failed
    - Retry information
    - Webhook delivery status if configured
    
    Args:
        job_id: UUID of email job
        db: Database session
        
    Returns:
        EmailJobStatusResponse with current job state
        
    Raises:
        404: Job not found
    """
    try:
        job_uuid = UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")
    
    # Fetch job
    result = await db.execute(
        select(EmailJob).where(EmailJob.id == job_uuid)
    )
    job = result.scalars().first()
    
    if not job:
        logger.warning(f"Job not found: {job_id}")
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Convert to response
    response = schemas.EmailJobStatusResponse(
        id=str(job.id),
        status=job.status,
        to_email=job.to_email,
        subject=job.subject,
        created_at=job.created_at,
        processing_started_at=job.processing_started_at,
        sent_at=job.sent_at,
        error_message=job.error_message,
        error_category=job.error_category,
        retry_count=job.retry_count,
        max_retries=job.max_retries,
        next_retry_at=job.next_retry_at,
        webhook_requested=job.webhook_requested,
    )
    
    return response


@router.get("/{job_id}/full", response_model=dict)
async def get_job_full_status(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get complete job status including webhook delivery details.
    
    This extended endpoint includes webhook delivery information if configured.
    
    Args:
        job_id: UUID of email job
        db: Database session
        
    Returns:
        Dict with job status and webhook delivery status
    """
    try:
        job_uuid = UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")
    
    # Fetch job
    result = await db.execute(
        select(EmailJob).where(EmailJob.id == job_uuid)
    )
    job = result.scalars().first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Fetch webhook delivery if exists
    webhook_status = None
    if job.webhook_requested:
        result = await db.execute(
            select(WebhookDelivery).where(WebhookDelivery.email_job_id == job_uuid)
        )
        webhook = result.scalars().first()
        
        if webhook:
            webhook_status = {
                "id": str(webhook.id),
                "status": webhook.status,
                "event_type": webhook.event_type,
                "retry_count": webhook.retry_count,
                "delivered_at": webhook.delivered_at,
                "last_error": webhook.last_error,
                "last_response_code": webhook.last_response_code,
            }
    
    return {
        "job": {
            "id": str(job.id),
            "status": job.status,
            "to_email": job.to_email,
            "subject": job.subject,
            "created_at": job.created_at,
            "sent_at": job.sent_at,
            "error_message": job.error_message,
            "error_category": job.error_category,
        },
        "webhook_delivery": webhook_status,
    }

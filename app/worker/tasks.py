"""
Email worker tasks with idempotency and webhook integration.

This module handles asynchronous email sending with:
- Synchronous SMTP (no asyncio.run() in Celery)
- Idempotency guards (sent_at timestamp)
- Job locking (FOR UPDATE SKIP LOCKED)
- Failure classification (permanent vs temporary)
- Webhook dispatch after completion
"""

import logging
import time
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.worker.celery_config import celery_app
from app.worker.exceptions import PermanentFailure, TemporaryFailure
from app.worker.smtp_sender import send_via_smtp
from app.worker.webhook_dispatcher import queue_webhook_if_configured
from app.models.all_models import EmailJob, EmailLog
from app.db.session import SessionLocal
from app.core import metrics

logger = logging.getLogger(__name__)


@celery_app.task(
    name="send_email_task",
    bind=True,
    max_retries=3,
    autoretry_for=(TemporaryFailure,),
    retry_backoff=True,
    retry_backoff_max=600,  # Max 10 minutes
    retry_jitter=True,
)
def send_email_task(self, job_id: str):
    """
    Process email job with retry logic and webhook dispatch.
    
    Workflow:
    1. Acquire job lock (SELECT FOR UPDATE SKIP LOCKED)
    2. Check idempotency (already sent?)
    3. Send email via SMTP (sync)
    4. Classify result (permanent vs temporary failure)
    5. Update job status + create log
    6. Queue webhook if configured
    7. Commit atomically
    
    Retry strategy:
    - Retry 1: ~60 seconds
    - Retry 2: ~120 seconds
    - Retry 3: ~240 seconds
    
    Args:
        job_id: UUID of EmailJob to process
    """
    with SessionLocal() as db:
        start_time = time.time()  # Track processing duration
        
        # ========================================
        # 1. Acquire job lock
        # ========================================
        job = db.execute(
            select(EmailJob)
            .where(EmailJob.id == job_id)
            .with_for_update(skip_locked=True)
        ).scalars().first()
        
        if job is None:
            logger.warning(f"Job {job_id} not found or locked by another worker")
            return
        
        # ========================================
        # 2. Idempotency check
        # ========================================
        if job.sent_at is not None:
            logger.info(f"Job {job_id} already sent at {job.sent_at}, skipping")
            return
        
        # Check if stuck in processing (safety for stale retries)
        if job.status == "processing" and job.processing_started_at:
            elapsed = datetime.utcnow() - job.processing_started_at
            if elapsed < timedelta(minutes=2):
                logger.warning(f"Job {job_id} still processing, skipping")
                return
        
        # ========================================
        # 3. Mark as processing
        # ========================================
        job.status = "processing"
        job.processing_started_at = datetime.utcnow()
        db.commit()
        
        final_status = None
        error_info = None
        
        try:
            # ========================================
            # 4. Send email (SYNC)
            # ========================================
            smtp_start = time.time()
            send_via_smtp(job, db)
            smtp_duration = time.time() - smtp_start
            
            # Success
            job.status = "sent"
            job.sent_at = datetime.utcnow()
            final_status = "sent"
            
            # Track metrics
            metrics.emails_sent_total.labels(
                tenant_id=str(job.tenant_id),
                application_id=str(job.application_id),
                service_name="email"  # TODO: get from job
            ).inc()
            
            logger.info(
                f"Email sent successfully: job_id={job_id}",
                extra={"job_id": job_id, "to_email": job.to_email, "duration_ms": int(smtp_duration * 1000)}
            )
            
        except PermanentFailure as e:
            # ========================================
            # 5a. Permanent failure - no retry
            # ========================================
            job.status = "failed"
            job.error_message = str(e)
            job.error_category = "permanent"
            final_status = "failed"
            error_info = {"category": "permanent", "message": str(e)}
            
            # Track metrics
            metrics.emails_failed_total.labels(
                tenant_id=str(job.tenant_id),
                application_id=str(job.application_id),
                service_name="email",
                error_category="permanent"
            ).inc()
            
            logger.warning(
                f"Email permanently failed: job_id={job_id}, error={e}",
                extra={"job_id": job_id, "error": str(e)}
            )
            
        except TemporaryFailure as e:
            # ========================================
            # 5b. Temporary failure - check retry count
            # ========================================
            if self.request.retries >= self.max_retries:
                # Max retries exceeded - mark as failed
                job.status = "failed"
                job.error_message = f"Max retries exceeded: {e}"
                job.error_category = "temporary"
                final_status = "failed"
                error_info = {"category": "temporary", "message": str(e)}
                
                # Track metrics
                metrics.emails_failed_total.labels(
                    tenant_id=str(job.tenant_id),
                    application_id=str(job.application_id),
                    service_name="email",
                    error_category="temporary_exhausted"
                ).inc()
                
                logger.error(
                    f"Email failed after max retries: job_id={job_id}",
                    extra={"job_id": job_id, "retries": self.request.retries}
                )
            else:
                # Retry
                job.status = "retry_pending"
                job.error_message = str(e)
                job.retry_count += 1
                
                # Track retry metrics
                metrics.email_retries_total.labels(
                    tenant_id=str(job.tenant_id),
                    application_id=str(job.application_id)
                ).inc()
                
                # Calculate next retry time
                backoff = 60 * (2 ** self.request.retries)
                job.next_retry_at = datetime.utcnow() + timedelta(seconds=backoff)
                
                db.commit()
                
                logger.info(
                    f"Email retry scheduled: job_id={job_id}, attempt={job.retry_count}",
                    extra={"job_id": job_id, "next_retry": job.next_retry_at}
                )
                
                raise  # Celery handles retry
        
        except Exception as e:
            # ========================================
            # 5c. Unexpected error - treat as temporary
            # ========================================
            logger.error(f"Unexpected error for job {job_id}: {e}", exc_info=True)
            job.status = "failed"
            job.error_message = f"Unexpected error: {e}"
            job.error_category = "system"
            final_status = "failed"
            error_info = {"category": "system", "message": str(e)}
        
        # ========================================
        # 6. Create email log
        # ========================================
        log = EmailLog(
            job_id=job.id,
            status=job.status,
            response_code=200 if final_status == "sent" else 500,
            response_message="OK" if final_status == "sent" else job.error_message
        )
        db.add(log)
        
        # ========================================
        # 7. Queue webhook if configured
        # ========================================
        if final_status in ("sent", "failed"):
            queue_webhook_if_configured(db, job, final_status, error_info)
        
        # ========================================
        # 8. Commit atomically and track duration
        # ========================================
        db.commit()
        
        # Track processing duration
        processing_duration = time.time() - start_time
        metrics.email_processing_duration_seconds.labels(
            tenant_id=str(job.tenant_id),
            status=final_status
        ).observe(processing_duration)
        
        logger.info(
            f"Email job completed: job_id={job_id}, status={final_status}, duration={processing_duration:.2f}s",
            extra={"job_id": job_id, "final_status": final_status, "duration_s": processing_duration}
        )

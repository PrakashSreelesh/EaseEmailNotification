"""
Webhook delivery worker tasks.

This module handles asynchronous webhook delivery to external endpoints.
Webhooks are processed in a separate queue from email delivery for isolation.
"""

import logging
import httpx
from datetime import datetime, timedelta
from sqlalchemy import select

from app.worker.celery_config import celery_app
from app.worker.exceptions import WebhookDeliveryError
from app.models.all_models import WebhookDelivery, Application
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)

WEBHOOK_TIMEOUT = 10  # seconds
WEBHOOK_MAX_RETRIES = 3


@celery_app.task(
    name="deliver_webhook_task",
    bind=True,
    max_retries=WEBHOOK_MAX_RETRIES,
    retry_backoff=True,
    retry_backoff_max=300,  # Max 5 minutes
    retry_jitter=True,
)
def deliver_webhook_task(self, delivery_id: str):
    """
    Deliver webhook to external endpoint.
    
    Retry strategy:
    - Retry 1: ~30 seconds
    - Retry 2: ~60 seconds
    - Retry 3: ~120 seconds
    
    After max retries: mark as failed (no more attempts).
    
    Args:
        delivery_id: UUID of WebhookDelivery record
    """
    with SessionLocal() as db:
        delivery = db.execute(
            select(WebhookDelivery).where(WebhookDelivery.id == delivery_id)
        ).scalars().first()
        
        if not delivery:
            logger.error(f"WebhookDelivery {delivery_id} not found")
            return
        
        if delivery.status == "delivered":
            logger.info(f"Webhook {delivery_id} already delivered, skipping")
            return
        
        # Fetch API key at delivery time (not stored in delivery record for security)
        application = db.execute(
            select(Application).where(Application.id == delivery.application_id)
        ).scalars().first()
        
        if not application or not application.webhook_api_key:
            logger.warning(f"No API key for application {delivery.application_id}")
            # Still attempt without key - application may not require it
            api_key = None
        else:
            api_key = application.webhook_api_key
        
        # Build headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "EaseEmail-Webhook/1.0",
        }
        if api_key:
            headers["X-API-Key"] = api_key
        
        try:
            # Make HTTP request (sync httpx)
            with httpx.Client(timeout=WEBHOOK_TIMEOUT) as client:
                response = client.post(
                    delivery.webhook_url,
                    json=delivery.payload,
                    headers=headers,
                )
            
            delivery.last_response_code = response.status_code
            delivery.last_response_body = response.text[:1024]  # Truncate to 1KB
            
            if response.is_success:
                # Success (2xx)
                delivery.status = "delivered"
                delivery.delivered_at = datetime.utcnow()
                db.commit()
                
                logger.info(
                    f"Webhook delivered: delivery_id={delivery_id}, status={response.status_code}",
                    extra={
                        "delivery_id": delivery_id,
                        "job_id": str(delivery.email_job_id),
                        "response_code": response.status_code
                    }
                )
                return
            
            # Non-2xx response - retry
            logger.warning(
                f"Webhook HTTP error {response.status_code}: {response.text[:200]}",
                extra={"delivery_id": delivery_id, "status_code": response.status_code}
            )
            raise WebhookDeliveryError(f"HTTP {response.status_code}: {response.text[:200]}")
            
        except httpx.TimeoutException as e:
            delivery.last_error = f"Timeout: {e}"
            db.commit()
            logger.warning(f"Webhook timeout: delivery_id={delivery_id}")
            raise WebhookDeliveryError(f"Timeout: {e}")
            
        except httpx.RequestError as e:
            delivery.last_error = f"Connection error: {e}"
            db.commit()
            logger.warning(f"Webhook connection error: delivery_id={delivery_id}")
            raise WebhookDeliveryError(f"Connection error: {e}")
            
        except WebhookDeliveryError as e:
            delivery.retry_count += 1
            
            if delivery.retry_count >= WEBHOOK_MAX_RETRIES:
                # Max retries exceeded
                delivery.status = "failed"
                db.commit()
                
                logger.error(
                    f"Webhook failed permanently: delivery_id={delivery_id}",
                    extra={
                        "delivery_id": delivery_id,
                        "job_id": str(delivery.email_job_id),
                        "retries": delivery.retry_count
                    }
                )
                return
            
            # Calculate next retry time for visibility
            backoff = 30 * (2 ** delivery.retry_count)
            delivery.next_retry_at = datetime.utcnow() + timedelta(seconds=backoff)
            db.commit()
            
            logger.info(
                f"Webhook retry scheduled: delivery_id={delivery_id}, attempt={delivery.retry_count}",
                extra={"delivery_id": delivery_id, "next_retry_at": delivery.next_retry_at}
            )
            
            raise  # Celery handles retry
            
        except Exception as e:
            # Unexpected error
            logger.error(f"Unexpected webhook error: {e}", exc_info=True)
            delivery.last_error = f"Unexpected: {e}"
            delivery.status = "failed"
            db.commit()

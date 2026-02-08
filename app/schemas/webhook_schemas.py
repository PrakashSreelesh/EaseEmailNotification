"""
Webhook payload schemas for email status callbacks.

This module defines the Pydantic schemas for webhook payloads
sent to external applications when email delivery status changes.
"""

from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime


class WebhookPayload(BaseModel):
    """
    Standard webhook payload for email status callbacks.
    
    This payload is sent via HTTP POST to the application's webhook_url
    when email delivery status changes.
    
    Events:
    - email.sent: Email successfully delivered via SMTP
    - email.failed: Email permanently failed OR max retries exceeded
    """
    # Event metadata
    event: str  # "email.sent" | "email.failed"
    timestamp: datetime  # When this event occurred
    
    # Job identifiers
    job_id: UUID4
    tenant_id: UUID4
    application_id: UUID4
    service_name: str
    
    # Email details
    to_email: str
    subject: Optional[str] = None
    
    # Delivery status
    status: str  # "sent" | "failed"
    sent_at: Optional[datetime] = None  # Only for email.sent
    
    # Error details (only for email.failed)
    error_category: Optional[str] = None  # "permanent" | "temporary"
    error_message: Optional[str] = None
    retry_count: int = 0
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID4: lambda v: str(v),
        }


class WebhookDeliveryStatus(BaseModel):
    """Status information for a webhook delivery attempt."""
    id: UUID4
    status: str  # "pending" | "delivered" | "failed"
    event_type: str
    retry_count: int
    delivered_at: Optional[datetime] = None
    last_error: Optional[str] = None
    
    class Config:
        from_attributes = True

"""
Email sending endpoint with API key authentication.

This endpoint queues emails for async delivery and returns immediately.
"""

from fastapi import APIRouter, Depends, Header, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas import schemas
from app.services.email_sender_service import EmailSenderService

router = APIRouter()


@router.post("/email/", response_model=schemas.AsyncEmailJobResponse, status_code=202)
async def send_email_with_api_key(
    payload: schemas.APIKeyEmailSendRequest,
    template: str = Query(..., description="Template name"),
    x_api_key: str = Header(..., alias="XAPIKey"),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """
    Queue email for asynchronous delivery.
    
    This endpoint:
    1. Validates request (API key, service, template)
    2. Renders template
    3. Creates EmailJob
    4. Queues to Celery worker
    5. Returns job_id immediately (< 200ms)
    
    The email is sent asynchronously by a worker. Poll /api/v1/jobs/{job_id}
    to check delivery status.
    
    Headers:
        XAPIKey: Application API key for authentication
    
    Query Params:
        template: Email template name
    
    Body:
        service_name: EmailService name
        to_email: Recipient email address
        variables_data: Template variables (JSON object)
    
    Returns:
        202 Accepted with job_id and status
    
    Example:
        POST /api/v1/send/email/?template=welcome
        Headers: XAPIKey: your-api-key
        Body: {
            "service_name": "Welcome Emails",
            "to_email": "user@example.com",
            "variables_data": {"name": "John"}
        }
    """
    result = await EmailSenderService.validate_and_queue(
        db=db,
        api_key=x_api_key,
        service_name=payload.service_name,
        template_name=template,
        to_email=payload.to_email,
        variables_data=payload.variables_data
    )
    
    # Build poll URL
    if request:
        base_url = str(request.base_url).rstrip("/")
        result["poll_url"] = f"{base_url}/api/v1/jobs/{result['job_id']}"
    
    return result

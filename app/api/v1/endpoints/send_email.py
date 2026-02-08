from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas import schemas
from app.services.email_sender_service import EmailSenderService

router = APIRouter()

@router.post("/email/")
async def send_email_with_api_key(
    payload: schemas.APIKeyEmailSendRequest,
    template: str = Query(..., description="Template name"),
    x_api_key: str = Header(..., alias="XAPIKey"),
    db: Session = Depends(get_db)
):
    """
    Send email using Application API Key authentication.
    """
    return await EmailSenderService.send(
        db=db,
        api_key=x_api_key,
        service_name=payload.service_name,
        template_name=template,
        to_email=payload.to_email,
        variables_data=payload.variables_data
    )

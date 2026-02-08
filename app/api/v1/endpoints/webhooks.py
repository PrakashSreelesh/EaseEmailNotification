from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from typing import List
from app.schemas import schemas
from app.models.all_models import WebhookService
from app.db.session import get_db

router = APIRouter()

@router.post("/", response_model=schemas.WebhookResponse)
async def create_webhook(webhook: schemas.WebhookCreate, db: Session = Depends(get_db)):
    db_webhook = WebhookService(
        application_id=webhook.application_id,
        name=webhook.name,
        target_url=webhook.target_url,
        event_type=webhook.event_type,
        secret_token=webhook.secret_token
    )
    db.add(db_webhook)
    await db.commit()
    await db.refresh(db_webhook)
    return db_webhook

@router.get("/", response_model=List[schemas.WebhookResponse])
async def read_webhooks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    result = await db.execute(select(WebhookService).offset(skip).limit(limit))
    return result.scalars().all()

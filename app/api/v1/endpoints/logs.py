from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import desc
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.schemas import schemas
from app.models.all_models import EmailLog, EmailJob, EmailService, EmailTemplate
from app.db.session import get_db

router = APIRouter()

# Enriched log response model
class EnrichedLogResponse(BaseModel):
    id: str
    recipient: str
    status: str
    sender: Optional[str] = None
    template_name: Optional[str] = None
    service_name: Optional[str] = None
    sent_at: datetime
    retry_count: int
    subject: Optional[str] = None

    class Config:
        from_attributes = True

@router.get("/", response_model=List[EnrichedLogResponse])
async def read_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get enriched email logs with joined job, service, and template data"""
    # Temporary: just return basic log data until we fix the enrichment
    result = await db.execute(
        select(EmailLog)
        .order_by(desc(EmailLog.created_at))
        .offset(skip)
        .limit(limit)
    )

    enriched_logs = []
    for log in result.scalars():
        # Basic enrichment for now
        enriched_log = EnrichedLogResponse(
            id=str(log.id),
            recipient="unknown",  # Will be populated later
            status=log.status,
            sender=None,
            template_name=None,
            service_name=None,
            sent_at=log.created_at,
            retry_count=0,
            subject=None
        )
        enriched_logs.append(enriched_log)

    return enriched_logs

@router.get("/{log_id}", response_model=schemas.LogResponse)
async def read_log(log_id: str, db: Session = Depends(get_db)):
    result = await db.execute(select(EmailLog).where(EmailLog.id == log_id))
    db_log = result.scalars().first()
    if not db_log:
        raise HTTPException(status_code=404, detail="Log not found")
    return db_log

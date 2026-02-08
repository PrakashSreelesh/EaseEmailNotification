from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from typing import List
from app.schemas import schemas
from app.models.all_models import EmailLog
from app.db.session import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.LogResponse])
async def read_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    result = await db.execute(select(EmailLog).order_by(EmailLog.created_at.desc()).offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/{log_id}", response_model=schemas.LogResponse)
async def read_log(log_id: str, db: Session = Depends(get_db)):
    result = await db.execute(select(EmailLog).where(EmailLog.id == log_id))
    db_log = result.scalars().first()
    if not db_log:
        raise HTTPException(status_code=404, detail="Log not found")
    return db_log

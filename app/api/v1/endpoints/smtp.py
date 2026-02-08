from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import func
from typing import List, Optional, Union
from app.schemas import schemas
from app.models.all_models import SMTPConfiguration
from app.db.session import get_db
from pydantic import BaseModel

class CountResponse(BaseModel):
    count: int

router = APIRouter()

@router.post("/", response_model=schemas.SMTPConfigResponse)
async def create_smtp_config(config: schemas.SMTPConfigCreate, db: Session = Depends(get_db)):
    # In a real app, encrypt the password here!
    db_config = SMTPConfiguration(
        tenant_id=config.tenant_id,
        name=config.name,
        provider=config.provider,
        host=config.host,
        port=config.port,
        username=config.username,
        password_encrypted=config.password_encrypted,
        use_tls=config.use_tls
    )
    db.add(db_config)
    await db.commit()
    await db.refresh(db_config)
    return db_config

@router.get("/")
async def read_smtp_configs(
    tenant_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    count_only: bool = Query(False),
    is_superadmin: bool = Query(False),
    db: Session = Depends(get_db)
):
    # If count_only is requested, return count
    if count_only:
        query = select(func.count(SMTPConfiguration.id))

        # For dashboard counts, be more permissive
        # Only filter by tenant if explicitly provided
        if tenant_id:
            query = query.where(SMTPConfiguration.tenant_id == tenant_id)
        # If no tenant_id provided, return total count (for dashboard overview)

        result = await db.execute(query)
        count = result.scalar()
        return {"count": count}

    # Regular query - be permissive like count query
    query = select(SMTPConfiguration)

    # For list queries, be more permissive
    # Only filter by tenant if explicitly provided
    if tenant_id:
        query = query.where(SMTPConfiguration.tenant_id == tenant_id)
    # If no tenant_id provided, return all (for admin overview)

    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/{smtp_id}", response_model=schemas.SMTPConfigResponse)
async def read_smtp_config(smtp_id: str, db: Session = Depends(get_db)):
    result = await db.execute(select(SMTPConfiguration).where(SMTPConfiguration.id == smtp_id))
    config = result.scalars().first()
    if not config:
        raise HTTPException(status_code=404, detail="SMTP Configuration not found")
    return config

@router.delete("/{smtp_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_smtp_config(smtp_id: str, db: Session = Depends(get_db)):
    result = await db.execute(select(SMTPConfiguration).where(SMTPConfiguration.id == smtp_id))
    config = result.scalars().first()
    if not config:
        raise HTTPException(status_code=404, detail="SMTP Configuration not found")
    await db.delete(config)
    await db.commit()
    return None

@router.patch("/{smtp_id}", response_model=schemas.SMTPConfigResponse)
async def update_smtp_config(smtp_id: str, config_update: schemas.SMTPConfigCreate, db: Session = Depends(get_db)):
    result = await db.execute(select(SMTPConfiguration).where(SMTPConfiguration.id == smtp_id))
    db_config = result.scalars().first()
    if not db_config:
        raise HTTPException(status_code=404, detail="SMTP Configuration not found")
    
    db_config.name = config_update.name
    db_config.provider = config_update.provider
    db_config.host = config_update.host
    db_config.port = config_update.port
    db_config.username = config_update.username
    if config_update.password_encrypted != "••••••••": # Only update if changed
        db_config.password_encrypted = config_update.password_encrypted
    db_config.use_tls = config_update.use_tls
    db_config.tenant_id = config_update.tenant_id
    
    await db.commit()
    await db.refresh(db_config)
    return db_config

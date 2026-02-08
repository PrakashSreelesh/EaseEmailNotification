from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from typing import List
from app.schemas import schemas
from app.models.all_models import Application, Tenant
from app.db.session import get_db
import uuid

router = APIRouter()

@router.post("/", response_model=schemas.ApplicationResponse)
async def create_application(app: schemas.ApplicationCreate, db: Session = Depends(get_db)):
    db_app = Application(
        name=app.name, 
        tenant_id=app.tenant_id, 
        api_key=str(uuid.uuid4()),
        description=app.description,
        status=app.status or "active",
        webhook_url=app.webhook_url,
        api_key_expiry=app.api_key_expiry
    )
    db.add(db_app)
    await db.commit()
    await db.refresh(db_app)
    return db_app

@router.get("/", response_model=List[schemas.ApplicationResponse])
async def read_applications(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    result = await db.execute(select(Application).offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/{app_id}", response_model=schemas.ApplicationResponse)
async def read_application(app_id: str, db: Session = Depends(get_db)):
    result = await db.execute(select(Application).where(Application.id == app_id))
    db_app = result.scalars().first()
    if not db_app:
        raise HTTPException(status_code=404, detail="Application not found")
    return db_app

@router.delete("/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(app_id: str, db: Session = Depends(get_db)):
    result = await db.execute(select(Application).where(Application.id == app_id))
    db_app = result.scalars().first()
    if not db_app:
        raise HTTPException(status_code=404, detail="Application not found")
    await db.delete(db_app)
    await db.commit()
    return None

@router.patch("/{app_id}", response_model=schemas.ApplicationResponse)
async def update_application(app_id: str, app_update: schemas.ApplicationCreate, db: Session = Depends(get_db)):
    result = await db.execute(select(Application).where(Application.id == app_id))
    db_app = result.scalars().first()
    if not db_app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    db_app.name = app_update.name
    db_app.tenant_id = app_update.tenant_id
    db_app.description = app_update.description
    db_app.status = app_update.status or db_app.status
    db_app.webhook_url = app_update.webhook_url
    db_app.api_key_expiry = app_update.api_key_expiry
    
    await db.commit()
    await db.refresh(db_app)
    return db_app

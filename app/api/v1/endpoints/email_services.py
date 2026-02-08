from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from typing import List
from app.schemas import schemas
from app.models.all_models import EmailService, Application
from app.db.session import get_db

router = APIRouter()

@router.post("/", response_model=schemas.EmailServiceResponse)
async def create_email_service(service: schemas.EmailServiceCreate, db: Session = Depends(get_db)):
    # Check if application exists
    result = await db.execute(select(Application).where(Application.id == service.application_id))
    app = result.scalars().first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    db_service = EmailService(
        application_id=service.application_id,
        name=service.name,
        from_email=service.from_email,
        # Link to config/template if provided
        smtp_configuration_id=service.smtp_configuration_id,
        template_id=service.template_id,
        # Legacy/Direct support
        smtp_host=service.smtp_host,
        smtp_port=service.smtp_port,
        smtp_user=service.smtp_user,
        smtp_password=service.smtp_password
    )
    db.add(db_service)
    await db.commit()
    await db.refresh(db_service)
    return db_service

@router.get("/", response_model=List[schemas.EmailServiceResponse])
async def read_email_services(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    result = await db.execute(select(EmailService).offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/{service_id}", response_model=schemas.EmailServiceResponse)
async def read_email_service(service_id: str, db: Session = Depends(get_db)):
    result = await db.execute(select(EmailService).where(EmailService.id == service_id))
    db_service = result.scalars().first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Email Service not found")
    return db_service

@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_email_service(service_id: str, db: Session = Depends(get_db)):
    result = await db.execute(select(EmailService).where(EmailService.id == service_id))
    db_service = result.scalars().first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Email Service not found")
    await db.delete(db_service)
    await db.commit()
    return None

@router.patch("/{service_id}", response_model=schemas.EmailServiceResponse)
async def update_email_service(service_id: str, service_update: schemas.EmailServiceCreate, db: Session = Depends(get_db)):
    result = await db.execute(select(EmailService).where(EmailService.id == service_id))
    db_service = result.scalars().first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Email Service not found")
    
    db_service.application_id = service_update.application_id
    db_service.name = service_update.name
    db_service.from_email = service_update.from_email
    db_service.smtp_configuration_id = service_update.smtp_configuration_id
    db_service.template_id = service_update.template_id
    db_service.smtp_host = service_update.smtp_host
    db_service.smtp_port = service_update.smtp_port
    db_service.smtp_user = service_update.smtp_user
    db_service.smtp_password = service_update.smtp_password
    
    await db.commit()
    await db.refresh(db_service)
    return db_service

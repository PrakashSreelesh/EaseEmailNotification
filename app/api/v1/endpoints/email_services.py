from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from typing import List
from app.schemas import schemas
from app.models.all_models import EmailService, Application, ServiceConfiguration
from sqlalchemy.orm import selectinload
from app.db.session import get_db

router = APIRouter()

@router.post("/", response_model=schemas.EmailServiceResponse)
async def create_email_service(service: schemas.EmailServiceCreate, db: Session = Depends(get_db)):
    # Create Email Service
    db_service = EmailService(
        name=service.name,
        description=service.description,
        status=service.status or "active",
        template_id=service.template_id,
        created_by=service.created_by,
        tenant_id=service.tenant_id
    )
    db.add(db_service)
    await db.flush() # Get the ID before committing

    # Create configurations
    for config in service.configurations:
        db_config = ServiceConfiguration(
            email_service_id=db_service.id,
            application_id=config.application_id,
            smtp_configuration_id=config.smtp_configuration_id,
            is_active=config.is_active,
            created_by=config.created_by
        )
        db.add(db_config)
    
    await db.commit()
    await db.refresh(db_service)
    
    # Reload with configurations for response
    result = await db.execute(
        select(EmailService)
        .options(selectinload(EmailService.configurations))
        .where(EmailService.id == db_service.id)
    )
    return result.scalars().first()

@router.get("/", response_model=List[schemas.EmailServiceResponse])
async def read_email_services(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    result = await db.execute(
        select(EmailService)
        .options(selectinload(EmailService.configurations))
        .offset(skip).limit(limit)
    )
    return result.scalars().all()

@router.get("/{service_id}", response_model=schemas.EmailServiceResponse)
async def read_email_service(service_id: str, db: Session = Depends(get_db)):
    result = await db.execute(
        select(EmailService)
        .options(selectinload(EmailService.configurations))
        .where(EmailService.id == service_id)
    )
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
    result = await db.execute(
        select(EmailService)
        .options(selectinload(EmailService.configurations))
        .where(EmailService.id == service_id)
    )
    db_service = result.scalars().first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Email Service not found")
    
    db_service.name = service_update.name
    db_service.description = service_update.description
    db_service.status = service_update.status or db_service.status
    db_service.template_id = service_update.template_id
    
    # Update configurations (simplest: clear and recreate)
    # Delete existing
    from sqlalchemy import delete
    await db.execute(delete(ServiceConfiguration).where(ServiceConfiguration.email_service_id == db_service.id))
    
    # Add new
    for config in service_update.configurations:
        db_config = ServiceConfiguration(
            email_service_id=db_service.id,
            application_id=config.application_id,
            smtp_configuration_id=config.smtp_configuration_id,
            is_active=config.is_active,
            created_by=config.created_by
        )
        db.add(db_config)
    
    await db.commit()
    
    # Reload for response
    result = await db.execute(
        select(EmailService)
        .options(selectinload(EmailService.configurations))
        .where(EmailService.id == service_id)
    )
    return result.scalars().first()

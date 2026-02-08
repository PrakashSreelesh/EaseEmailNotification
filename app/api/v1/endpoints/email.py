from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas import schemas
from app.models.all_models import EmailJob, EmailService
from app.db.session import get_db
from sqlalchemy import select
from sqlalchemy.orm import joinedload
import json
# In a real app, import Celery task here
# from app.worker.tasks import send_email_task

router = APIRouter()

@router.post("/send", response_model=schemas.EmailJobResponse)
async def send_email(email_req: schemas.EmailSendRequest, db: Session = Depends(get_db)):
    # 1. Validate Service Exists
    result = await db.execute(
        select(EmailService)
        .options(joinedload(EmailService.template))
        .where(EmailService.id == email_req.service_id)
    )
    service = result.scalars().first()
    if not service:
        raise HTTPException(status_code=404, detail="Email Service not found")

    # 2. Create Job in DB
    # If using a template, the worker expects variables as JSON in the 'body' field
    if service.template_id:
        template_data = {**(email_req.subject_data or {}), **(email_req.body_data or {})}
        job_subject = email_req.subject or f"[Template] {service.template.name}"
        job_body = json.dumps(template_data)
    else:
        job_subject = email_req.subject or "No Subject"
        job_body = email_req.body or ""

    job = EmailJob(
        service_id=email_req.service_id,
        to_email=email_req.to_email,
        subject=job_subject, 
        body=job_body,
        status="queued"
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # 3. Trigger worker (Placeholder)
    # send_email_task.delay(str(job.id))
    
    return job

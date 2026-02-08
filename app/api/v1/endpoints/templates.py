from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from typing import List
from app.schemas import schemas
from app.models.all_models import EmailTemplate, SMTPConfiguration
from app.db.session import get_db
from jinja2 import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import aiosmtplib

router = APIRouter()

@router.post("/", response_model=schemas.TemplateResponse)
async def create_template(template: schemas.TemplateCreate, db: Session = Depends(get_db)):
    db_template = EmailTemplate(
        tenant_id=template.tenant_id,
        name=template.name,
        subject_template=template.subject_template,
        body_template=template.body_template,
        sample_data=template.sample_data
    )
    db.add(db_template)
    await db.commit()
    await db.refresh(db_template)
    return db_template

@router.get("/", response_model=List[schemas.TemplateResponse])
async def read_templates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    result = await db.execute(select(EmailTemplate).offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/{template_id}", response_model=schemas.TemplateResponse)
async def read_template(template_id: str, db: Session = Depends(get_db)):
    result = await db.execute(select(EmailTemplate).where(EmailTemplate.id == template_id))
    template = result.scalars().first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(template_id: str, db: Session = Depends(get_db)):
    result = await db.execute(select(EmailTemplate).where(EmailTemplate.id == template_id))
    template = result.scalars().first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    await db.delete(template)
    await db.commit()
    return None

@router.patch("/{template_id}", response_model=schemas.TemplateResponse)
async def update_template(template_id: str, template_update: schemas.TemplateCreate, db: Session = Depends(get_db)):
    result = await db.execute(select(EmailTemplate).where(EmailTemplate.id == template_id))
    db_template = result.scalars().first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    db_template.name = template_update.name
    db_template.subject_template = template_update.subject_template
    db_template.body_template = template_update.body_template
    db_template.sample_data = template_update.sample_data
    db_template.tenant_id = template_update.tenant_id
    
    await db.commit()
    await db.refresh(db_template)
    return db_template

@router.post("/test-send")
async def test_send_template(req: schemas.TemplateTestSendRequest, db: Session = Depends(get_db)):
    # 1. Fetch SMTP Config
    result = await db.execute(select(SMTPConfiguration).where(SMTPConfiguration.id == req.smtp_id))
    smtp_config = result.scalars().first()
    if not smtp_config:
        raise HTTPException(status_code=404, detail="SMTP Configuration not found")
    
    # 2. Render Template
    try:
        subject_tmpl = Template(req.subject_template)
        subject = subject_tmpl.render(req.sample_data)
        
        body_tmpl = Template(req.body_template)
        body = body_tmpl.render(req.sample_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Template rendering error: {str(e)}")
    
    # 3. Construct Message
    message = MIMEMultipart("alternative")
    message["From"] = smtp_config.username # Or a specified sender
    message["To"] = req.recipient
    message["Subject"] = subject
    message.attach(MIMEText(body, "html"))
    
    # 4. Send Email
    try:
        use_implicit_tls = (smtp_config.port == 465)
        await aiosmtplib.send(
            message,
            hostname=smtp_config.host,
            port=smtp_config.port,
            username=smtp_config.username,
            password=smtp_config.password_encrypted,
            use_tls=use_implicit_tls,
            start_tls=not use_implicit_tls and smtp_config.use_tls
        )
        return {"status": "success", "message": "Test email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SMTP error: {str(e)}")

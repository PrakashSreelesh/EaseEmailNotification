from pydantic import BaseModel, UUID4, EmailStr
from typing import Optional, List
from datetime import datetime

class TenantBase(BaseModel):
    name: str

class TenantCreate(TenantBase):
    pass

class TenantResponse(TenantBase):
    id: UUID4
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: Optional[str] = "viewer"
    is_superadmin: Optional[bool] = False
    is_admin: Optional[bool] = False
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str
    tenant_id: UUID4

class UserResponse(UserBase):
    id: UUID4
    tenant_id: UUID4
    tenant_name: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class ApplicationBase(BaseModel):
    name: str
    tenant_id: Optional[UUID4] = None # Optional for creation if inferred

class ApplicationCreate(ApplicationBase):
    pass

class ApplicationResponse(ApplicationBase):
    id: UUID4
    api_key: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class SMTPConfigBase(BaseModel):
    name: Optional[str] = None
    provider: Optional[str] = "custom"
    host: str
    port: int
    username: str
    password_encrypted: str
    use_tls: bool = True
    tenant_id: Optional[UUID4] = None

class SMTPConfigCreate(SMTPConfigBase):
    pass

class SMTPConfigResponse(SMTPConfigBase):
    id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True

class TemplateBase(BaseModel):
    name: str
    subject_template: str
    body_template: str
    sample_data: Optional[dict] = None
    tenant_id: Optional[UUID4] = None

class TemplateCreate(TemplateBase):
    pass

class TemplateResponse(TemplateBase):
    id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True

class TemplateTestSendRequest(BaseModel):
    recipient: EmailStr
    smtp_id: UUID4
    subject_template: str
    body_template: str
    sample_data: dict

class WebhookBase(BaseModel):
    name: str
    target_url: str
    event_type: str
    is_active: bool = True
    application_id: Optional[UUID4] = None

class WebhookCreate(WebhookBase):
    pass

class WebhookResponse(WebhookBase):
    id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True

class EmailServiceBase(BaseModel):
    name: str
    from_email: str
    application_id: Optional[UUID4] = None
    template_id: Optional[UUID4] = None
    smtp_configuration_id: Optional[UUID4] = None

class EmailServiceCreate(EmailServiceBase):
    pass

class EmailServiceResponse(EmailServiceBase):
    id: UUID4
    created_at: datetime
    
    class Config:
        from_attributes = True

class EmailSendRequest(BaseModel):
    to_email: EmailStr
    subject_data: Optional[dict] = {}
    body_data: Optional[dict] = {}
    subject: Optional[str] = None
    body: Optional[str] = None
    service_id: UUID4 

class EmailJobResponse(BaseModel):
    id: UUID4
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class EmailLogResponse(BaseModel):
    id: UUID4
    job_id: UUID4
    status: str
    response_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# Alias for compatibility if needed or explicit definition
class LogResponse(EmailLogResponse):
    pass

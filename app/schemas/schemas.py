from pydantic import BaseModel, UUID4, EmailStr, field_validator, ValidationInfo
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
    tenant_id: Optional[UUID4] = None

class UserResponse(UserBase):
    id: UUID4
    tenant_id: Optional[UUID4] = None
    tenant_name: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class ApplicationBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: Optional[str] = "active"
    webhook_url: Optional[str] = None
    api_key_expiry: Optional[datetime] = None
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
    category: Optional[str] = "General"
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

class ServiceConfigurationBase(BaseModel):
    application_id: UUID4
    smtp_configuration_id: UUID4
    is_active: Optional[bool] = True
    created_by: Optional[str] = None

class ServiceConfigurationCreate(ServiceConfigurationBase):
    pass

class ServiceConfigurationResponse(ServiceConfigurationBase):
    id: UUID4
    email_service_id: UUID4
    created_at: datetime
    
    class Config:
        from_attributes = True

class EmailServiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    from_email: Optional[str] = None
    template_id: Optional[UUID4] = None
    status: Optional[str] = "active"
    created_by: Optional[str] = None
    tenant_id: Optional[UUID4] = None

class EmailServiceCreate(EmailServiceBase):
    configurations: List[ServiceConfigurationCreate]

    @field_validator('configurations')
    @classmethod
    def validate_configurations(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one Application-SMTP configuration is required')
        return v

class EmailServiceResponse(BaseModel):
    id: UUID4
    name: str
    description: str = ""
    from_email: Optional[str] = None
    status: str = "active"
    created_by: str = "System"
    created_at: datetime
    template_id: Optional[UUID4] = None
    tenant_id: Optional[UUID4] = None
    configurations: List[ServiceConfigurationResponse] = []
    
    @field_validator('description', 'created_by', mode='before')
    @classmethod
    def set_defaults(cls, v, info: ValidationInfo):
        if v is None:
            if info.field_name == 'description': return ""
            if info.field_name == 'created_by': return "System"
        return v

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

class APIKeyEmailSendRequest(BaseModel):
    to_email: EmailStr
    variables_data: dict = {}
    service_name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    username: str
    role: str
    is_superadmin: bool
    is_admin: bool
    tenant_id: Optional[UUID4] = None

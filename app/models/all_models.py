from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, Text, JSON, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.session import Base

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    users = relationship("User", back_populates="tenant")
    applications = relationship("Application", back_populates="tenant")
    smtp_configurations = relationship("SMTPConfiguration", back_populates="tenant")
    email_templates = relationship("EmailTemplate", back_populates="tenant")

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"))
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, nullable=True)
    role = Column(String, default="viewer") # super_admin, admin, viewer
    is_superadmin = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tenant = relationship("Tenant", back_populates="users")

class Application(Base):
    __tablename__ = "applications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"))
    name = Column(String)
    description = Column(Text, nullable=True)
    status = Column(String, default="active")
    webhook_url = Column(String, nullable=True)
    api_key_expiry = Column(DateTime(timezone=True), nullable=True)
    api_key = Column(String, unique=True, index=True) # Could be hashed
    
    # Webhook configuration (NEW/ENHANCED for v3.0)
    webhook_api_key = Column(String, nullable=True)  # API key for outbound webhook calls
    webhook_enabled = Column(Boolean, default=False)  # Explicit webhook toggle
    webhook_events = Column(JSON, default=lambda: ["email.sent", "email.failed"])  # Event filter
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    tenant = relationship("Tenant", back_populates="applications")
    service_configurations = relationship("ServiceConfiguration", back_populates="application")
    webhooks = relationship("WebhookService", back_populates="application")
    email_jobs = relationship("EmailJob", back_populates="application")  # NEW
    webhook_deliveries = relationship("WebhookDelivery", back_populates="application")  # NEW

class SMTPConfiguration(Base):
    __tablename__ = "smtp_configurations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"))
    name = Column(String, nullable=True) # Account Name
    provider = Column(String, default="custom") # Gmail, Outlook, Amazon SES, etc.
    host = Column(String)
    port = Column(Integer)
    username = Column(String)
    password_encrypted = Column(String) # Placeholder for encrypted info
    use_tls = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    tenant = relationship("Tenant", back_populates="smtp_configurations")
    service_configurations = relationship("ServiceConfiguration", back_populates="smtp_configuration")

class EmailTemplate(Base):
    __tablename__ = "email_templates"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"))
    name = Column(String)
    category = Column(String, default="General")  # Category field added
    subject_template = Column(String)
    body_template = Column(Text) # HTML or Text
    sample_data = Column(JSON, nullable=True) # Sample variables data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    tenant = relationship("Tenant", back_populates="email_templates")
    email_services = relationship("EmailService", back_populates="template")

class EmailService(Base):
    __tablename__ = "email_services"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"))
    template_id = Column(UUID(as_uuid=True), ForeignKey("email_templates.id"), nullable=True)

    name = Column(String)
    description = Column(Text, nullable=True)
    from_email = Column(String, nullable=True)  # Sender email address
    status = Column(String, default="active")
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    template = relationship("EmailTemplate", back_populates="email_services")
    configurations = relationship("ServiceConfiguration", back_populates="email_service", cascade="all, delete-orphan")
    jobs = relationship("EmailJob", back_populates="service")

class ServiceConfiguration(Base):
    __tablename__ = "service_configurations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email_service_id = Column(UUID(as_uuid=True), ForeignKey("email_services.id"))
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id"))
    smtp_configuration_id = Column(UUID(as_uuid=True), ForeignKey("smtp_configurations.id"))
    
    is_active = Column(Boolean, default=True)
    is_delete = Column(Boolean, default=False)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    email_service = relationship("EmailService", back_populates="configurations")
    application = relationship("Application", back_populates="service_configurations")
    smtp_configuration = relationship("SMTPConfiguration", back_populates="service_configurations")

class EmailJob(Base):
    __tablename__ = "email_jobs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_id = Column(UUID(as_uuid=True), ForeignKey("email_services.id"))
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), index=True)  # NEW: For rate limiting
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id"))  # NEW: For webhook config
    
    to_email = Column(String)
    subject = Column(String)
    body = Column(Text)
    
    # Status tracking
    status = Column(String, default="queued", index=True)  # queued, processing, sent, failed, retry_pending
    
    # Idempotency fields (NEW for v3.0)
    sent_at = Column(DateTime(timezone=True), nullable=True)  # Set ONLY when email actually sent
    processing_started_at = Column(DateTime(timezone=True), nullable=True)
    
    # Error handling (ENHANCED)
    error_message = Column(Text, nullable=True)
    error_category = Column(String, nullable=True)  # "permanent" or "temporary"
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)  # NEW
    next_retry_at = Column(DateTime(timezone=True), nullable=True)  # NEW
    
    # Webhook tracking (NEW for v3.0)
    webhook_requested = Column(Boolean, default=False)  # Was webhook queued?
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    service = relationship("EmailService", back_populates="jobs")
    application = relationship("Application", back_populates="email_jobs")  # NEW
    logs = relationship("EmailLog", back_populates="job")
    webhook_deliveries = relationship("WebhookDelivery", back_populates="email_job")  # NEW

class EmailLog(Base):
    __tablename__ = "email_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("email_jobs.id"))
    status = Column(String)
    response_code = Column(Integer, nullable=True)
    response_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    job = relationship("EmailJob", back_populates="logs")

class WebhookService(Base):
    __tablename__ = "webhook_services"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id"))
    name = Column(String)
    target_url = Column(String)
    event_type = Column(String) # e.g. "email.sent", "email.failed"
    secret_token = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    application = relationship("Application", back_populates="webhooks")

class WebhookDelivery(Base):
    """
    Tracks individual webhook delivery attempts.
    One EmailJob can trigger one WebhookDelivery.
    """
    __tablename__ = "webhook_deliveries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    email_job_id = Column(UUID(as_uuid=True), ForeignKey("email_jobs.id"), nullable=False, index=True)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Webhook target (copied from Application at creation time)
    webhook_url = Column(String, nullable=False)
    # NOTE: webhook_api_key is NOT stored here - fetched at delivery time
    
    # Event info
    event_type = Column(String, nullable=False)  # "email.sent" | "email.failed"
    payload = Column(JSON, nullable=False)  # Serialized webhook body
    
    # Delivery status
    status = Column(String, default="pending", index=True)
    # Values: pending, delivered, failed
    
    # Retry tracking
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    next_retry_at = Column(DateTime(timezone=True), nullable=True)
    
    # Response tracking
    last_response_code = Column(Integer, nullable=True)
    last_response_body = Column(Text, nullable=True)  # Truncated to 1KB
    last_error = Column(Text, nullable=True)
    
    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    email_job = relationship("EmailJob", back_populates="webhook_deliveries")
    application = relationship("Application", back_populates="webhook_deliveries")

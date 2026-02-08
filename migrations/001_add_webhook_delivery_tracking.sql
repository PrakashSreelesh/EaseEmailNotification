-- Migration: Add webhook delivery tracking and enhance email job model
-- Date: 2026-02-09
-- Description: Implements async email with webhook callbacks (v3.0)

-- ========================================
-- 1. Update applications table
-- ========================================

-- Add webhook configuration fields
ALTER TABLE applications ADD COLUMN IF NOT EXISTS webhook_api_key VARCHAR;
ALTER TABLE applications ADD COLUMN IF NOT EXISTS webhook_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE applications ADD COLUMN IF NOT EXISTS webhook_events JSON DEFAULT '["email.sent", "email.failed"]';

COMMENT ON COLUMN applications.webhook_api_key IS 'API key for outbound webhook calls';
COMMENT ON COLUMN applications.webhook_enabled IS 'Explicit toggle for webhook functionality';
COMMENT ON COLUMN applications.webhook_events IS 'List of events that trigger webhooks';

-- ========================================
-- 2. Update email_jobs table
-- ========================================

-- Add foreign keys
ALTER TABLE email_jobs ADD COLUMN IF NOT EXISTS tenant_id UUID REFERENCES tenants(id);
ALTER TABLE email_jobs ADD COLUMN IF NOT EXISTS application_id UUID REFERENCES applications(id);

-- Add idempotency fields
ALTER TABLE email_jobs ADD COLUMN IF NOT EXISTS sent_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE email_jobs ADD COLUMN IF NOT EXISTS processing_started_at TIMESTAMP WITH TIME ZONE;

-- Add error handling fields
ALTER TABLE email_jobs ADD COLUMN IF NOT EXISTS error_category VARCHAR;
ALTER TABLE email_jobs ADD COLUMN IF NOT EXISTS max_retries INTEGER DEFAULT 3;
ALTER TABLE email_jobs ADD COLUMN IF NOT EXISTS next_retry_at TIMESTAMP WITH TIME ZONE;

-- Add webhook tracking
ALTER TABLE email_jobs ADD COLUMN IF NOT EXISTS webhook_requested BOOLEAN DEFAULT FALSE;

-- Update existing status column to add index if not exists
CREATE INDEX IF NOT EXISTS idx_email_jobs_status ON email_jobs(status);
CREATE INDEX IF NOT EXISTS idx_email_jobs_tenant_id ON email_jobs(tenant_id);

-- Comments for documentation
COMMENT ON COLUMN email_jobs.sent_at IS 'Timestamp when email was actually sent (idempotency key)';
COMMENT ON COLUMN email_jobs.processing_started_at IS 'When worker started processing this job';
COMMENT ON COLUMN email_jobs.error_category IS 'permanent or temporary - for smart retry logic';
COMMENT ON COLUMN email_jobs.webhook_requested IS 'Whether webhook was queued for this job';

-- ========================================
-- 3. Create webhook_deliveries table
-- ========================================

CREATE TABLE IF NOT EXISTS webhook_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign keys
    email_job_id UUID NOT NULL REFERENCES email_jobs(id) ON DELETE CASCADE,
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Webhook target (snapshot from application at queue time)
    webhook_url VARCHAR NOT NULL,
    
    -- Event info
    event_type VARCHAR NOT NULL,  -- 'email.sent' or 'email.failed'
    payload JSON NOT NULL,
    
    -- Delivery status
    status VARCHAR DEFAULT 'pending' NOT NULL,  -- pending, delivered, failed
    
    -- Retry tracking
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    next_retry_at TIMESTAMP WITH TIME ZONE,
    
    -- Response tracking
    last_response_code INTEGER,
    last_response_body TEXT,
    last_error TEXT,
    
    -- Timing
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    delivered_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_job ON webhook_deliveries(email_job_id);
CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_tenant ON webhook_deliveries(tenant_id);
CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_status ON webhook_deliveries(status);
CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_status_retry ON webhook_deliveries(status, next_retry_at);

-- Comments
COMMENT ON TABLE webhook_deliveries IS 'Tracks individual webhook delivery attempts for email status callbacks';
COMMENT ON COLUMN webhook_deliveries.webhook_url IS 'Snapshot of webhook URL from application at queue time';
COMMENT ON COLUMN webhook_deliveries.payload IS 'Full webhook payload as JSON';
COMMENT ON COLUMN webhook_deliveries.last_response_body IS 'Truncated to 1KB for storage';

-- ========================================
-- 4. Data migration (if needed)
-- ========================================

-- Backfill tenant_id for existing email_jobs from their service
UPDATE email_jobs
SET tenant_id = (
    SELECT email_services.tenant_id
    FROM email_services
    WHERE email_services.id = email_jobs.service_id
)
WHERE tenant_id IS NULL AND service_id IS NOT NULL;

-- Backfill application_id for existing email_jobs from service_configurations
-- This assumes one configuration per service (pick the first active one)
UPDATE email_jobs
SET application_id = (
    SELECT sc.application_id
    FROM service_configurations sc
    WHERE sc.email_service_id = email_jobs.service_id
    AND sc.is_active = TRUE
    LIMIT 1
)
WHERE application_id IS NULL AND service_id IS NOT NULL;

-- ========================================
-- 5. Rollback script (OPTIONAL - for reference)
-- ========================================

-- To rollback this migration:
/*
DROP TABLE IF EXISTS webhook_deliveries CASCADE;

ALTER TABLE email_jobs DROP COLUMN IF EXISTS webhook_requested;
ALTER TABLE email_jobs DROP COLUMN IF EXISTS next_retry_at;
ALTER TABLE email_jobs DROP COLUMN IF EXISTS max_retries;
ALTER TABLE email_jobs DROP COLUMN IF EXISTS error_category;
ALTER TABLE email_jobs DROP COLUMN IF EXISTS processing_started_at;
ALTER TABLE email_jobs DROP COLUMN IF EXISTS sent_at;
ALTER TABLE email_jobs DROP COLUMN IF EXISTS application_id;
ALTER TABLE email_jobs DROP COLUMN IF EXISTS tenant_id;

ALTER TABLE applications DROP COLUMN IF EXISTS webhook_events;
ALTER TABLE applications DROP COLUMN IF EXISTS webhook_enabled;
ALTER TABLE applications DROP COLUMN IF EXISTS webhook_api_key;

DROP INDEX IF EXISTS idx_email_jobs_tenant_id;
DROP INDEX IF EXISTS idx_email_jobs_status;
*/

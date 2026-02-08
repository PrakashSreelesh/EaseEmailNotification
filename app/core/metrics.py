"""
Prometheus metrics for EaseEmail Notifications platform.

This module defines all metrics for monitoring email and webhook delivery.
Metrics are exposed at /metrics endpoint for Prometheus scraping.
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# =====================================================
# EMAIL METRICS
# =====================================================

emails_queued_total = Counter(
    "easeemail_emails_queued_total",
    "Total number of emails queued for delivery",
    ["tenant_id", "application_id", "service_name"]
)

emails_sent_total = Counter(
    "easeemail_emails_sent_total",
    "Total number of emails successfully sent",
    ["tenant_id", "application_id", "service_name"]
)

emails_failed_total = Counter(
    "easeemail_emails_failed_total",
    "Total number of emails that failed permanently",
    ["tenant_id", "application_id", "service_name", "error_category"]
)

email_retries_total = Counter(
    "easeemail_email_retries_total",
    "Total number of email retry attempts",
    ["tenant_id", "application_id"]
)

email_processing_duration_seconds = Histogram(
    "easeemail_email_processing_duration_seconds",
    "Time spent processing email jobs (queued to completion)",
    ["tenant_id", "status"],
    buckets=[1, 5, 10, 30, 60, 120, 300, 600]
)

email_smtp_duration_seconds = Histogram(
    "easeemail_email_smtp_duration_seconds",
    "Time spent in SMTP send operation",
    ["tenant_id", "smtp_host"],
    buckets=[0.1, 0.5, 1, 2, 5, 10, 30]
)

# =====================================================
# WEBHOOK METRICS
# =====================================================

webhooks_queued_total = Counter(
    "easeemail_webhooks_queued_total",
    "Total number of webhooks queued for delivery",
    ["tenant_id", "application_id", "event_type"]
)

webhooks_delivered_total = Counter(
    "easeemail_webhooks_delivered_total",
    "Total number of webhooks successfully delivered",
    ["tenant_id", "application_id", "event_type"]
)

webhooks_failed_total = Counter(
    "easeemail_webhooks_failed_total",
    "Total number of webhooks that failed permanently",
    ["tenant_id", "application_id", "event_type"]
)

webhook_retries_total = Counter(
    "easeemail_webhook_retries_total",
    "Total number of webhook retry attempts",
    ["tenant_id", "application_id"]
)

webhook_delivery_duration_seconds = Histogram(
    "easeemail_webhook_delivery_duration_seconds",
    "Time to deliver webhook (HTTP request duration)",
    ["tenant_id", "event_type", "status_code"],
    buckets=[0.1, 0.5, 1, 2, 5, 10, 30]
)

webhook_http_errors_total = Counter(
    "easeemail_webhook_http_errors_total",
    "Total webhook HTTP errors by status code",
    ["tenant_id", "status_code"]
)

# =====================================================
# SYSTEM METRICS
# =====================================================

worker_tasks_active = Gauge(
    "easeemail_worker_tasks_active",
    "Number of active tasks by worker type",
    ["worker_type", "queue"]
)

worker_tasks_total = Counter(
    "easeemail_worker_tasks_total",
    "Total tasks processed by worker",
    ["worker_type", "queue", "status"]
)

api_requests_total = Counter(
    "easeemail_api_requests_total",
    "Total API requests",
    ["method", "endpoint", "status_code"]
)

api_request_duration_seconds = Histogram(
    "easeemail_api_request_duration_seconds",
    "API request duration",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5]
)

# =====================================================
# DATABASE METRICS
# =====================================================

db_jobs_by_status = Gauge(
    "easeemail_db_jobs_by_status",
    "Number of email jobs by status",
    ["status"]
)

db_webhook_deliveries_by_status = Gauge(
    "easeemail_db_webhook_deliveries_by_status",
    "Number of webhook deliveries by status",
    ["status"]
)

# =====================================================
# HELPER FUNCTIONS
# =====================================================

def get_metrics():
    """Return metrics in Prometheus format"""
    return generate_latest()


def get_metrics_content_type():
    """Return content type for metrics endpoint"""
    return CONTENT_TYPE_LATEST

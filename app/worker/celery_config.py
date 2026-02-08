"""
Celery configuration for async email and webhook delivery.

This module configures Celery with production-ready settings:
- Prefork worker pool (NOT eventlet/gevent)
- Memory-safe worker recycling
- Separate queues for email and webhooks
- Task acks late for reliability
"""

from celery import Celery
from kombu import Queue

from app.core.config import settings

# Create Celery app
celery_app = Celery("easeemail_worker")

# Celery configuration
celery_app.conf.update(
    # ========================================
    # Broker & Backend
    # ========================================
    broker_url=settings.CELERY_BROKER_URL,
    result_backend=settings.CELERY_RESULT_BACKEND,
    
    # ========================================
    # Serialization
    # ========================================
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # ========================================
    # Worker Settings (CRITICAL for memory safety)
    # ========================================
    worker_pool="prefork",              # NOT eventlet/gevent - pure sync workers
    worker_concurrency=4,               # 4 processes per container
    worker_prefetch_multiplier=1,       # One task at a time per worker
    worker_max_tasks_per_child=500,     # Recycle after 500 tasks (memory safety)
    worker_disable_rate_limits=False,   # Enable rate limiting
    
    # ========================================
    # Task Behavior (for reliability)
    # ========================================
    task_acks_late=True,                # Ack after completion (not before)
    task_reject_on_worker_lost=True,    # Requeue if worker dies
    task_time_limit=120,                # Hard kill after 2 minutes
    task_soft_time_limit=90,            # Graceful timeout after 90 seconds
    task_ignore_result=False,           # Store results for debugging
    
    # ========================================
    # Queues (separate email and webhook)
    # ========================================
    task_queues=(
        Queue("email_delivery", routing_key="email.#"),
        Queue("email_delivery_high", routing_key="email.high.#"),
        Queue("email_delivery_bulk", routing_key="email.bulk.#"),
        Queue("webhook_delivery", routing_key="webhook.#"),  # Separate webhook queue
    ),
    task_default_queue="email_delivery",
    
    # ========================================
    # Task Routing
    # ========================================
    task_routes={
        "send_email_task": {"queue": "email_delivery"},
        "deliver_webhook_task": {"queue": "webhook_delivery"},
    },
    
    # ========================================
    # Result Backend
    # ========================================
    result_expires=3600,  # Results expire after 1 hour
    result_backend_transport_options={"master_name": "mymaster"},
    
    # ========================================
    # Logging
    # ========================================
    worker_redirect_stdouts=True,
    worker_redirect_stdouts_level="INFO",
)

# Import tasks to register them
from app.worker import tasks
from app.worker import webhook_tasks

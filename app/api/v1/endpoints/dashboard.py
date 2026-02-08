from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, desc, case
from typing import List
from pydantic import BaseModel
from app.db.session import get_db
from app.models.all_models import EmailLog, EmailJob, EmailService, EmailTemplate, EmailTemplate, User, Application, SMTPConfiguration, Tenant

router = APIRouter()

# Response models
class EmailStats(BaseModel):
    sent: int
    delivered: int
    failed: int
    pending: int

class RecentActivityItem(BaseModel):
    icon: str
    title: str
    subtitle: str
    time: str

class QuickStats(BaseModel):
    delivery_rate: float
    bounce_rate: float
    open_rate: float

@router.get("/email-stats", response_model=EmailStats)
async def get_email_stats(db: AsyncSession = Depends(get_db)):
    """Get email statistics aggregated from email jobs and logs

    Status classification:
    - sent: EmailJob.status == 'sent' (successfully sent to SMTP)
    - delivered: For simplicity, we count sent emails as delivered (no delivery tracking)
    - failed: EmailJob.status == 'failed' (bounced or rejected)
    - pending: EmailJob.status in ('queued', 'processing') (still in queue)
    """
    # Count EmailJob statuses for more accurate analytics
    result = await db.execute(
        select(
            func.count(case((EmailJob.status == 'sent', 1))).label('sent_jobs'),
            func.count(case((EmailJob.status == 'failed', 1))).label('failed_jobs'),
            func.count(case((EmailJob.status.in_(['queued', 'processing']), 1))).label('pending_jobs'),
            func.count(EmailJob.id).label('total_jobs')
        )
    )
    row = result.first()

    # For this simple system, we assume sent = delivered (no delivery confirmation tracking)
    sent = row.sent_jobs or 0
    delivered = sent  # Assume sent emails are delivered
    failed = row.failed_jobs or 0
    pending = row.pending_jobs or 0

    return EmailStats(
        sent=sent,
        delivered=delivered,
        failed=failed,
        pending=pending
    )

@router.get("/recent-activity", response_model=List[RecentActivityItem])
async def get_recent_activity(db: AsyncSession = Depends(get_db)):
    """Get recent email activities (last 5 items) from real DB data."""
    # Join EmailLog with EmailJob to get details like subject, to_email
    stmt = (
        select(EmailLog, EmailJob)
        .outerjoin(EmailJob, EmailLog.job_id == EmailJob.id)
        .order_by(desc(EmailLog.created_at))
        .limit(5)
    )
    result = await db.execute(stmt)
    rows = result.all()

    if not rows:
        return []

    activities = []
    import datetime

    now = datetime.datetime.utcnow()

    for log, job in rows:
        # 1. Determine Icon
        # default to 'mail'
        icon = 'mail'
        if log.status == 'sent':
            icon = 'check-circle'
        elif log.status == 'failed':
            icon = 'alert-circle'
        elif log.status == 'queued':
            icon = 'clock'
        elif log.status == 'delivered':
            icon = 'check-circle'

        # 2. Determine Title/Subtitle
        if job:
            if log.status == 'sent':
                title = "Email Sent Successfully"
                subtitle = f"To: {job.to_email}"
            elif log.status == 'failed':
                title = "Email Delivery Failed"
                subtitle = f"To: {job.to_email}"
            elif log.status == 'queued':
                title = "Email Queued"
                subtitle = f"To: {job.to_email}"
            else:
                title = f"Email {log.status.capitalize()}"
                subtitle = f"To: {job.to_email}"
        else:
            # Fallback if job is missing (orphaned log?)
            title = f"Email {log.status.capitalize()}"
            subtitle = "Unknown Recipient"

        # 3. Calculate Time Ago
        diff = now - log.created_at
        seconds = diff.total_seconds()
        
        if seconds < 60:
            time_str = "Just now"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            time_str = f"{minutes} min{'s' if minutes != 1 else ''} ago"
        elif seconds < 86400:
            hours = int(seconds // 3600)
            time_str = f"{hours} hour{'s' if hours != 1 else ''} ago"
        else:
            days = int(seconds // 86400)
            time_str = f"{days} day{'s' if days != 1 else ''} ago"

        activities.append(RecentActivityItem(
            icon=icon,
            title=title,
            subtitle=subtitle,
            time=time_str.upper()
        ))

    return activities

@router.get("/quick-stats", response_model=QuickStats)
async def get_quick_stats(db: AsyncSession = Depends(get_db)):
    """Calculate quick statistics (delivery rate, bounce rate, open rate)"""
    # Get total counts
    result = await db.execute(
        select(
            func.count(case((EmailLog.status == 'sent', 1))).label('total_sent'),
            func.count(case((EmailLog.status == 'delivered', 1))).label('delivered'),
            func.count(case((EmailLog.status == 'failed', 1))).label('failed')
        )
    )
    row = result.first()

    total_sent = row.total_sent or 0
    delivered = row.delivered or 0
    failed = row.failed or 0

    # Calculate rates (avoid division by zero)
    delivery_rate = (delivered / total_sent * 100) if total_sent > 0 else 0.0
    bounce_rate = (failed / total_sent * 100) if total_sent > 0 else 0.0
    open_rate = 0.0  # Placeholder - would need tracking data for actual open rates

    return QuickStats(
        delivery_rate=round(delivery_rate, 1),
        bounce_rate=round(bounce_rate, 1),
        open_rate=open_rate
    )
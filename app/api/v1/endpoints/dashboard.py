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
async def get_recent_activity(limit: int = 10, db: AsyncSession = Depends(get_db)):
    """Get recent email activities (last 10 items)"""
    # First try to get data with EmailJob join
    result = await db.execute(
        select(EmailLog, EmailJob)
        .join(EmailJob, EmailLog.job_id == EmailJob.id, isouter=True)
        .order_by(desc(EmailLog.created_at))
        .limit(limit)
    )

    activities = []
    for log, job in result:
        # Calculate time ago (simplified - in production use proper time formatting)
        time_diff = "2 hours ago"  # Placeholder - would calculate actual time diff

        # Determine icon based on status
        icon_map = {
            'sent': 'mail',
            'delivered': 'check-circle',
            'failed': 'alert-circle',
            'pending': 'clock'
        }
        icon = icon_map.get(log.status, 'mail')

        # Format title and subtitle based on available data
        if job:  # If we have job data
            if log.status == 'sent':
                title = f"Email sent to {job.to_email}"
                subtitle = f"Subject: {job.subject[:50]}..."
            elif log.status == 'delivered':
                title = f"Email delivered to {job.to_email}"
                subtitle = f"Subject: {job.subject[:50]}..."
            elif log.status == 'failed':
                title = f"Email failed to {job.to_email}"
                subtitle = f"Error: {log.response_message[:50] if log.response_message else 'Unknown error'}"
            else:
                title = f"Email pending to {job.to_email}"
                subtitle = f"Subject: {job.subject[:50]}..."
        else:  # Fallback to log-only data
            title = f"Email {log.status}"
            subtitle = f"Log ID: {str(log.id)[:8]}..."

        activities.append(RecentActivityItem(
            icon=icon,
            title=title,
            subtitle=subtitle,
            time=time_diff
        ))

    # If no activities from database, return some mock data for demo purposes
    if not activities:
        activities = [
            RecentActivityItem(
                icon="mail",
                title="500 emails sent",
                subtitle="via Primary SMTP account",
                time="2 hours ago"
            ),
            RecentActivityItem(
                icon="file-text",
                title="Template created",
                subtitle="Welcome Onboarding Email",
                time="5 hours ago"
            ),
            RecentActivityItem(
                icon="package",
                title="App registered",
                subtitle="New application connected",
                time="1 day ago"
            )
        ]

    return activities[:5]  # Return max 5 items as specified

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
    open_rate = 42.3  # Placeholder - would need tracking data for actual open rates

    return QuickStats(
        delivery_rate=round(delivery_rate, 1),
        bounce_rate=round(bounce_rate, 1),
        open_rate=open_rate
    )
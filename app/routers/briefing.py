from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from datetime import date, datetime, timedelta, timezone
from app.database import get_db
from app.models import Lead, Client, Deliverable, OutreachLog, DailyBriefing, SystemLog
from app.schemas import BriefingOut

router = APIRouter(prefix="/api/briefing", tags=["briefing"])

IST = timezone(timedelta(hours=5, minutes=30))


@router.get("/today")
async def today_briefing(db: AsyncSession = Depends(get_db)):
    """Compile the morning briefing from live database state."""
    today = datetime.now(IST).date()
    yesterday = today - timedelta(days=1)
    month_start = today.replace(day=1)

    # New leads (last 24h)
    new_leads_result = await db.execute(
        select(func.count(Lead.id)).where(Lead.created_at >= datetime.combine(yesterday, datetime.min.time()))
    )
    new_leads_count = new_leads_result.scalar() or 0

    # Lead breakdown by city (new leads)
    city_breakdown_result = await db.execute(
        select(Lead.city, func.count(Lead.id))
        .where(Lead.created_at >= datetime.combine(yesterday, datetime.min.time()))
        .group_by(Lead.city)
    )
    leads_by_city = {row[0] or "Unknown": row[1] for row in city_breakdown_result.all()}

    # Outreach stats (last 24h)
    outreach_sent = await db.execute(
        select(func.count(OutreachLog.id)).where(OutreachLog.sent_at >= datetime.combine(yesterday, datetime.min.time()))
    )
    sent_count = outreach_sent.scalar() or 0

    outreach_opened = await db.execute(
        select(func.count(OutreachLog.id)).where(
            OutreachLog.opened_at >= datetime.combine(yesterday, datetime.min.time())
        )
    )
    opened_count = outreach_opened.scalar() or 0

    outreach_replied = await db.execute(
        select(func.count(OutreachLog.id)).where(
            OutreachLog.replied_at >= datetime.combine(yesterday, datetime.min.time())
        )
    )
    replied_count = outreach_replied.scalar() or 0

    # Pending deliverables (status = "ready", awaiting approval)
    pending_result = await db.execute(
        select(func.count(Deliverable.id)).where(Deliverable.status == "ready")
    )
    pending_approvals = pending_result.scalar() or 0

    # Revenue — active clients this month
    revenue_result = await db.execute(
        select(func.sum(Client.monthly_rate)).where(Client.status == "active")
    )
    revenue_month = revenue_result.scalar() or 0

    # Pipeline — leads that responded but not yet converted
    pipeline_result = await db.execute(
        select(func.count(Lead.id)).where(Lead.status == "responded")
    )
    pipeline_count = pipeline_result.scalar() or 0

    # Recent errors
    errors_result = await db.execute(
        select(func.count(SystemLog.id)).where(
            SystemLog.status.in_(["failed", "needs_review"]),
            SystemLog.timestamp >= datetime.combine(yesterday, datetime.min.time()),
        )
    )
    error_count = errors_result.scalar() or 0

    briefing = {
        "date": str(today),
        "leads": {
            "new_count": new_leads_count,
            "by_city": leads_by_city,
        },
        "outreach": {
            "sent_yesterday": sent_count,
            "opened": opened_count,
            "replied": replied_count,
        },
        "deliverables": {
            "pending_approval": pending_approvals,
        },
        "revenue": {
            "monthly_recurring": revenue_month,
            "pipeline_leads": pipeline_count,
        },
        "system": {
            "errors_last_24h": error_count,
        },
    }

    # Save briefing to database
    existing = await db.execute(
        select(DailyBriefing).where(DailyBriefing.date == today)
    )
    record = existing.scalar_one_or_none()
    if record:
        record.briefing_json = briefing
        record.new_leads_count = new_leads_count
        record.pending_approvals_count = pending_approvals
        record.revenue_month = revenue_month
        record.generated_at = func.now()
    else:
        record = DailyBriefing(
            date=today,
            briefing_json=briefing,
            new_leads_count=new_leads_count,
            pending_approvals_count=pending_approvals,
            revenue_month=revenue_month,
        )
        db.add(record)

    await db.commit()
    return briefing


@router.get("/history", response_model=list[BriefingOut])
async def briefing_history(days: int = 7, db: AsyncSession = Depends(get_db)):
    """Get past briefings."""
    cutoff = date.today() - timedelta(days=days)
    result = await db.execute(
        select(DailyBriefing)
        .where(DailyBriefing.date >= cutoff)
        .order_by(DailyBriefing.date.desc())
    )
    return result.scalars().all()

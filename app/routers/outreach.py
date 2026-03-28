from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import OutreachLog
from app.schemas import OutreachCreate, OutreachUpdate, OutreachOut

router = APIRouter(prefix="/api/outreach", tags=["outreach"])


@router.post("/", response_model=OutreachOut, status_code=201)
async def create_outreach(data: OutreachCreate, db: AsyncSession = Depends(get_db)):
    entry = OutreachLog(**data.model_dump())
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.get("/", response_model=list[OutreachOut])
async def list_outreach(
    status: str | None = None,
    channel: str | None = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    q = select(OutreachLog)
    if status:
        q = q.where(OutreachLog.status == status)
    if channel:
        q = q.where(OutreachLog.channel == channel)
    q = q.order_by(OutreachLog.sent_at.desc()).offset(skip).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/stats")
async def outreach_stats(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(OutreachLog.status, func.count(OutreachLog.id)).group_by(OutreachLog.status)
    )
    return {row[0]: row[1] for row in result.all()}


@router.get("/{outreach_id}", response_model=OutreachOut)
async def get_outreach(outreach_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(OutreachLog).where(OutreachLog.id == outreach_id))
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Outreach entry not found")
    return entry


@router.patch("/{outreach_id}", response_model=OutreachOut)
async def update_outreach(outreach_id: int, data: OutreachUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(OutreachLog).where(OutreachLog.id == outreach_id))
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Outreach entry not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(entry, field, value)
    await db.commit()
    await db.refresh(entry)
    return entry

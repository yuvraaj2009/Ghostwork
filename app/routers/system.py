from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import SystemLog
from app.schemas import SystemLogCreate, SystemLogOut

router = APIRouter(prefix="/api/system", tags=["system"])


@router.post("/log", response_model=SystemLogOut, status_code=201)
async def create_log(data: SystemLogCreate, db: AsyncSession = Depends(get_db)):
    entry = SystemLog(**data.model_dump())
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.get("/logs", response_model=list[SystemLogOut])
async def list_logs(
    agent_name: str | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    q = select(SystemLog)
    if agent_name:
        q = q.where(SystemLog.agent_name == agent_name)
    if status:
        q = q.where(SystemLog.status == status)
    q = q.order_by(SystemLog.timestamp.desc()).offset(skip).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/logs/errors")
async def recent_errors(limit: int = 20, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(SystemLog)
        .where(SystemLog.status.in_(["failed", "needs_review"]))
        .order_by(SystemLog.timestamp.desc())
        .limit(limit)
    )
    return [SystemLogOut.model_validate(e) for e in result.scalars().all()]


@router.get("/logs/summary")
async def log_summary(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(SystemLog.agent_name, SystemLog.status, func.count(SystemLog.id))
        .group_by(SystemLog.agent_name, SystemLog.status)
    )
    summary = {}
    for agent, status, count in result.all():
        if agent not in summary:
            summary[agent] = {}
        summary[agent][status] = count
    return summary

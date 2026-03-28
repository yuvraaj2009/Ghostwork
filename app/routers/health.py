from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {e}"
    return {
        "status": "alive",
        "database": db_status,
        "service": "ghostwork-api",
    }


@router.get("/ping")
async def ping():
    """Keep-alive endpoint for cron-job.org (every 14 min)."""
    return {"pong": True}

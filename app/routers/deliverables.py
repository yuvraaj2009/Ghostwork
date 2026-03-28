from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import Deliverable
from app.schemas import DeliverableCreate, DeliverableUpdate, DeliverableOut

router = APIRouter(prefix="/api/deliverables", tags=["deliverables"])


@router.post("/", response_model=DeliverableOut, status_code=201)
async def create_deliverable(data: DeliverableCreate, db: AsyncSession = Depends(get_db)):
    deliverable = Deliverable(**data.model_dump())
    db.add(deliverable)
    await db.commit()
    await db.refresh(deliverable)
    return deliverable


@router.get("/", response_model=list[DeliverableOut])
async def list_deliverables(
    status: str | None = None,
    client_id: int | None = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    q = select(Deliverable)
    if status:
        q = q.where(Deliverable.status == status)
    if client_id:
        q = q.where(Deliverable.client_id == client_id)
    q = q.order_by(Deliverable.generated_at.desc()).offset(skip).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/pending")
async def pending_deliverables(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Deliverable).where(Deliverable.status == "ready").order_by(Deliverable.generated_at.desc())
    )
    return [DeliverableOut.model_validate(d) for d in result.scalars().all()]


@router.get("/{deliverable_id}", response_model=DeliverableOut)
async def get_deliverable(deliverable_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Deliverable).where(Deliverable.id == deliverable_id))
    deliverable = result.scalar_one_or_none()
    if not deliverable:
        raise HTTPException(status_code=404, detail="Deliverable not found")
    return deliverable


@router.patch("/{deliverable_id}", response_model=DeliverableOut)
async def update_deliverable(deliverable_id: int, data: DeliverableUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Deliverable).where(Deliverable.id == deliverable_id))
    deliverable = result.scalar_one_or_none()
    if not deliverable:
        raise HTTPException(status_code=404, detail="Deliverable not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(deliverable, field, value)
    await db.commit()
    await db.refresh(deliverable)
    return deliverable


@router.delete("/{deliverable_id}", status_code=204)
async def delete_deliverable(deliverable_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Deliverable).where(Deliverable.id == deliverable_id))
    deliverable = result.scalar_one_or_none()
    if not deliverable:
        raise HTTPException(status_code=404, detail="Deliverable not found")
    await db.delete(deliverable)
    await db.commit()

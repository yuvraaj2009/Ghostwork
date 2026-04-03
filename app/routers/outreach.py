from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.schemas import OutreachCreate, OutreachUpdate, OutreachOut, SingleOutreachRequest, BatchOutreachRequest
from app.models import Lead, OutreachLog
from services.outreach_engine import send_outreach_email, send_batch_outreach

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


@router.post("/send-single")
async def send_single_outreach(request: SingleOutreachRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Lead).where(Lead.id == request.lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    lead_data = {
        "id": lead.id,
        "business_name": lead.business_name,
        "city": lead.city,
        "contact_email": lead.contact_email,
        "website_url": lead.website_url,
        "status": lead.status
    }
    
    send_result = send_outreach_email(lead_data, request.template_type)
    
    # Log to DB manually
    status = "sent" if send_result.get("success") else "failed"
    log_entry = OutreachLog(
        lead_id=lead.id,
        template_id=request.template_type,
        channel="email",
        status=status
    )
    db.add(log_entry)
    
    # Update lead status if sent
    if status == "sent" and lead.status == "new":
        lead.status = "outreach_sent"
        
    await db.commit()
    await db.refresh(log_entry)
    
    return {"log_id": log_entry.id, "result": send_result}


@router.post("/send-batch")
async def send_batch_outreach_endpoint(request: BatchOutreachRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Lead).where(Lead.id.in_(request.lead_ids)))
    leads = result.scalars().all()
    
    lead_data_list = []
    for lead in leads:
        lead_data_list.append({
            "id": lead.id,
            "business_name": lead.business_name,
            "city": lead.city,
            "contact_email": lead.contact_email,
            "website_url": lead.website_url,
            "status": lead.status
        })
        
    # Send batch via the engine
    batch_results = await send_batch_outreach(
        lead_data_list, 
        db=db, 
        template_type=request.template_type, 
        daily_limit=request.daily_limit
    )
    
    # Update lead status for those successful
    # Note: send_batch_outreach already handles logging to OutreachLog
    successful_lead_ids = [r["lead_id"] for r in batch_results if r["result"].get("success")]
    if successful_lead_ids:
        for lead in leads:
            if lead.id in successful_lead_ids and lead.status == "new":
                lead.status = "outreach_sent"
        await db.commit()
        
    return {"processed": len(batch_results), "results": batch_results}

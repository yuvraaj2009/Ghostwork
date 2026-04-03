from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import Lead
from app.schemas import LeadCreate, LeadUpdate, LeadOut
from typing import List
from pydantic import BaseModel
from services.lead_prospector import find_restaurant_leads

class ProspectRequest(BaseModel):
    city: str
    min_results: int = 20

class ScoredLead(BaseModel):
    name: str
    address: str
    rating: float
    total_reviews: int
    phone: str
    website: str
    email: str | None = None
    place_id: str
    pain_score: float

router = APIRouter(prefix="/api/leads", tags=["leads"])


@router.post("/", response_model=LeadOut, status_code=201)
async def create_lead(data: LeadCreate, db: AsyncSession = Depends(get_db)):
    lead = Lead(**data.model_dump())
    db.add(lead)
    await db.commit()
    await db.refresh(lead)
    return lead


@router.get("/", response_model=list[LeadOut])
async def list_leads(
    status: str | None = None,
    city: str | None = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    q = select(Lead)
    if status:
        q = q.where(Lead.status == status)
    if city:
        q = q.where(Lead.city == city)
    q = q.order_by(Lead.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/stats")
async def lead_stats(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Lead.status, func.count(Lead.id)).group_by(Lead.status)
    )
    return {row[0]: row[1] for row in result.all()}


@router.get("/{lead_id}", response_model=LeadOut)
async def get_lead(lead_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.patch("/{lead_id}", response_model=LeadOut)
async def update_lead(lead_id: int, data: LeadUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(lead, field, value)
    await db.commit()
    await db.refresh(lead)
    return lead


@router.delete("/{lead_id}", status_code=204)
async def delete_lead(lead_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    await db.delete(lead)
    await db.commit()

@router.post("/prospect", response_model=List[ScoredLead])
async def prospect_leads(request: ProspectRequest):
    try:
        leads = find_restaurant_leads(request.city, request.min_results)
        return leads
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/prospect-and-save", response_model=List[LeadOut])
async def prospect_and_save_leads(request: ProspectRequest, db: AsyncSession = Depends(get_db)):
    try:
        leads = find_restaurant_leads(request.city, request.min_results)
        
        saved_leads = []
        top_leads = leads[:20]
        
        for lead_data in top_leads:
            q = select(Lead).where(
                Lead.business_name == lead_data["name"],
                Lead.city == request.city
            )
            result = await db.execute(q)
            existing_lead = result.scalar_one_or_none()
            
            if not existing_lead:
                new_lead = Lead(
                    business_name=lead_data["name"],
                    city=request.city,
                    category="restaurant",
                    google_rating=lead_data["rating"],
                    review_count=lead_data["total_reviews"],
                    website_url=lead_data["website"],
                    contact_phone=lead_data["phone"],
                    contact_email=lead_data.get("email"),
                    status="new",
                    pain_points_json={"pain_score": lead_data["pain_score"], "place_id": lead_data["place_id"]}
                )
                db.add(new_lead)
                saved_leads.append(new_lead)
                
            else:
                # Still include existing ones in the "saved/processed" return so we know they were top 20
                saved_leads.append(existing_lead)
        
        if saved_leads:
            await db.commit()
            for sl in saved_leads:
                await db.refresh(sl)
            
        return saved_leads
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

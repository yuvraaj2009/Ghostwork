from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import Client, Deliverable, SystemLog
from services.review_generator import generate_review_responses

router = APIRouter(
    prefix="/api/factory",
    tags=["factory"]
)

class ReviewResponseRequest(BaseModel):
    restaurant_name: str
    restaurant_type: str
    tone: str
    reviews: List[str]

@router.post("/review-responses")
async def create_review_responses(request: ReviewResponseRequest, db: AsyncSession = Depends(get_db)):
    try:
        responses = generate_review_responses(
            restaurant_name=request.restaurant_name,
            restaurant_type=request.restaurant_type,
            tone=request.tone,
            reviews_list=request.reviews
        )
        
        # We try to attach the deliverable to an existing client, or create a dummy one
        stmt = select(Client).where(Client.business_name == request.restaurant_name)
        result = await db.execute(stmt)
        client = result.scalar_one_or_none()
        
        if not client:
            client = Client(business_name=request.restaurant_name, service_type="review_responses")
            db.add(client)
            await db.flush()  # to get the client id
        
        # Log to the deliverables table
        deliverable = Deliverable(
            client_id=client.id,
            type="review_responses",
            status="ready",
            content_json={"responses": responses}
        )
        db.add(deliverable)
        
        # Log this generation request to systemic action logs 
        log = SystemLog(
            agent_name="Head of Operations / The Factory (Agent 3)",
            action="generated_review_responses",
            details_json={"restaurant": request.restaurant_name, "count": len(request.reviews)},
            status="success"
        )
        db.add(log)
        
        await db.commit()
        
        return responses
        
    except Exception as e:
        await db.rollback()
        try:
            log = SystemLog(
                agent_name="Head of Operations / The Factory (Agent 3)",
                action="generated_review_responses",
                details_json={"restaurant": request.restaurant_name, "error": str(e)},
                status="failed"
            )
            db.add(log)
            await db.commit()
        except Exception:
            pass
            
        raise HTTPException(status_code=500, detail=str(e))

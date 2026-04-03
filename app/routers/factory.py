from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import Client, Deliverable, SystemLog
from services.review_generator import generate_review_responses
from services.menu_rewriter import rewrite_menu_descriptions
from services.social_media_generator import generate_social_media_pack

router = APIRouter(
    prefix="/api/factory",
    tags=["factory"]
)

class ReviewResponseRequest(BaseModel):
    restaurant_name: str
    restaurant_type: str
    tone: str
    reviews: List[str]

class MenuItemRequest(BaseModel):
    dish_name: str
    current_description: str
    price: float | str

class MenuRewriteRequest(BaseModel):
    restaurant_name: str
    restaurant_type: str
    menu_items: List[MenuItemRequest]

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

@router.post("/menu-rewrite")
async def create_menu_rewrite(request: MenuRewriteRequest, db: AsyncSession = Depends(get_db)):
    try:
        menu_items_dicts = [
            {"dish_name": item.dish_name, "current_description": item.current_description, "price": item.price}
            for item in request.menu_items
        ]
        
        responses = rewrite_menu_descriptions(
            restaurant_name=request.restaurant_name,
            restaurant_type=request.restaurant_type,
            menu_items=menu_items_dicts
        )
        
        stmt = select(Client).where(Client.business_name == request.restaurant_name)
        result = await db.execute(stmt)
        client = result.scalar_one_or_none()
        
        if not client:
            client = Client(business_name=request.restaurant_name, service_type="menu_rewrite")
            db.add(client)
            await db.flush()
        
        deliverable = Deliverable(
            client_id=client.id,
            type="menu_rewrite",
            status="ready",
            content_json={"menu_items": responses}
        )
        db.add(deliverable)
        
        log = SystemLog(
            agent_name="Head of Operations / The Factory (Agent 3)",
            action="generated_menu_rewrite",
            details_json={"restaurant": request.restaurant_name, "count": len(request.menu_items)},
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
                action="generated_menu_rewrite",
                details_json={"restaurant": request.restaurant_name, "error": str(e)},
                status="failed"
            )
            db.add(log)
            await db.commit()
        except Exception:
            pass
            
        raise HTTPException(status_code=500, detail=str(e))

class SocialMediaPackRequest(BaseModel):
    restaurant_name: str
    restaurant_type: str
    cuisine: str
    location: str
    tone: str
    days: int = 30

@router.post("/social-media-pack")
async def create_social_media_pack(request: SocialMediaPackRequest, db: AsyncSession = Depends(get_db)):
    try:
        pack = generate_social_media_pack(
            restaurant_name=request.restaurant_name,
            restaurant_type=request.restaurant_type,
            cuisine=request.cuisine,
            location=request.location,
            tone=request.tone,
            days=request.days
        )
        
        stmt = select(Client).where(Client.business_name == request.restaurant_name)
        result = await db.execute(stmt)
        client = result.scalar_one_or_none()
        
        if not client:
            client = Client(business_name=request.restaurant_name, service_type="social_media_pack")
            db.add(client)
            await db.flush()
        
        deliverable = Deliverable(
            client_id=client.id,
            type="social_media_pack",
            status="ready",
            content_json={"pack": pack}
        )
        db.add(deliverable)
        
        log = SystemLog(
            agent_name="Head of Operations / The Factory (Agent 3)",
            action="generated_social_media_pack",
            details_json={"restaurant": request.restaurant_name, "days": request.days},
            status="success"
        )
        db.add(log)
        
        await db.commit()
        return pack
        
    except Exception as e:
        await db.rollback()
        try:
            log = SystemLog(
                agent_name="Head of Operations / The Factory (Agent 3)",
                action="generated_social_media_pack",
                details_json={"restaurant": request.restaurant_name, "error": str(e)},
                status="failed"
            )
            db.add(log)
            await db.commit()
        except Exception:
            pass
            
        raise HTTPException(status_code=500, detail=str(e))

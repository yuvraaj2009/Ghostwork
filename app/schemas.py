from pydantic import BaseModel
from datetime import datetime, date
from typing import Any


# ── Leads ──

class LeadCreate(BaseModel):
    business_name: str
    city: str | None = None
    category: str | None = None
    google_rating: float | None = None
    review_count: int | None = None
    website_url: str | None = None
    pain_points_json: Any | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    status: str = "new"

class LeadUpdate(BaseModel):
    business_name: str | None = None
    city: str | None = None
    category: str | None = None
    google_rating: float | None = None
    review_count: int | None = None
    website_url: str | None = None
    pain_points_json: Any | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    status: str | None = None
    outreach_template_used: str | None = None
    last_contacted_at: datetime | None = None

class LeadOut(BaseModel):
    id: int
    business_name: str
    city: str | None
    category: str | None
    google_rating: float | None
    review_count: int | None
    website_url: str | None
    pain_points_json: Any | None
    contact_email: str | None
    contact_phone: str | None
    status: str
    outreach_template_used: str | None
    last_contacted_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Clients ──

class ClientCreate(BaseModel):
    business_name: str
    owner_name: str | None = None
    email: str | None = None
    service_type: str | None = None
    plan: str | None = None
    monthly_rate: float = 0

class ClientUpdate(BaseModel):
    business_name: str | None = None
    owner_name: str | None = None
    email: str | None = None
    service_type: str | None = None
    plan: str | None = None
    monthly_rate: float | None = None
    status: str | None = None

class ClientOut(BaseModel):
    id: int
    business_name: str
    owner_name: str | None
    email: str | None
    service_type: str | None
    plan: str | None
    monthly_rate: float
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Deliverables ──

class DeliverableCreate(BaseModel):
    client_id: int
    type: str
    content_json: Any | None = None
    status: str = "generating"

class DeliverableUpdate(BaseModel):
    status: str | None = None
    content_json: Any | None = None
    feedback_notes: str | None = None
    approved_at: datetime | None = None
    delivered_at: datetime | None = None

class DeliverableOut(BaseModel):
    id: int
    client_id: int
    type: str
    status: str
    content_json: Any | None
    generated_at: datetime
    approved_at: datetime | None
    delivered_at: datetime | None
    feedback_notes: str | None

    model_config = {"from_attributes": True}


# ── Outreach Log ──

class OutreachCreate(BaseModel):
    lead_id: int
    template_id: str | None = None
    channel: str = "email"

class OutreachUpdate(BaseModel):
    opened_at: datetime | None = None
    replied_at: datetime | None = None
    response_sentiment: str | None = None
    follow_up_scheduled: datetime | None = None
    status: str | None = None

class OutreachOut(BaseModel):
    id: int
    lead_id: int
    template_id: str | None
    channel: str
    sent_at: datetime
    opened_at: datetime | None
    replied_at: datetime | None
    response_sentiment: str | None
    follow_up_scheduled: datetime | None
    status: str

    model_config = {"from_attributes": True}


# ── Daily Briefing ──

class BriefingOut(BaseModel):
    id: int
    date: date
    briefing_json: Any | None
    new_leads_count: int
    pending_approvals_count: int
    revenue_today: float
    revenue_month: float
    generated_at: datetime

    model_config = {"from_attributes": True}


# ── System Log ──

class SystemLogCreate(BaseModel):
    agent_name: str
    action: str
    details_json: Any | None = None
    status: str = "success"

class SystemLogOut(BaseModel):
    id: int
    agent_name: str
    action: str
    details_json: Any | None
    status: str
    timestamp: datetime

    model_config = {"from_attributes": True}

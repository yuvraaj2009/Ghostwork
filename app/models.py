from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from app.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    business_name = Column(String(255), nullable=False)
    city = Column(String(100))
    category = Column(String(100))
    google_rating = Column(Float)
    review_count = Column(Integer)
    website_url = Column(String(500))
    pain_points_json = Column(JSON)
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    status = Column(String(50), default="new", index=True)  # new, outreach_sent, responded, converted, rejected
    outreach_template_used = Column(String(100))
    last_contacted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    business_name = Column(String(255), nullable=False)
    owner_name = Column(String(255))
    email = Column(String(255))
    service_type = Column(String(50))  # review_responses, social_content, menu_rewrite
    plan = Column(String(50))  # one_time, monthly
    monthly_rate = Column(Float, default=0)
    status = Column(String(50), default="active", index=True)  # active, paused, churned
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Deliverable(Base):
    __tablename__ = "deliverables"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # review_responses, social_content, menu_rewrite
    status = Column(String(50), default="generating", index=True)  # generating, ready, approved, delivered
    content_json = Column(JSON)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    feedback_notes = Column(Text)


class OutreachLog(Base):
    __tablename__ = "outreach_log"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False, index=True)
    template_id = Column(String(100))
    channel = Column(String(50))  # email, linkedin, whatsapp
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    opened_at = Column(DateTime(timezone=True))
    replied_at = Column(DateTime(timezone=True))
    response_sentiment = Column(String(50))
    follow_up_scheduled = Column(DateTime(timezone=True))
    status = Column(String(50), default="sent", index=True)  # sent, opened, replied, converted, dead


class DailyBriefing(Base):
    __tablename__ = "daily_briefing"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, unique=True, index=True)
    briefing_json = Column(JSON)
    new_leads_count = Column(Integer, default=0)
    pending_approvals_count = Column(Integer, default=0)
    revenue_today = Column(Float, default=0)
    revenue_month = Column(Float, default=0)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())


class SystemLog(Base):
    __tablename__ = "system_log"

    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String(100), nullable=False, index=True)
    action = Column(String(255), nullable=False)
    details_json = Column(JSON)
    status = Column(String(50), default="success", index=True)  # success, failed, needs_review
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

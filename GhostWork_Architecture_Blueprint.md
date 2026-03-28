# AUTONOMOUS BUSINESS OS — Architecture Blueprint v1.0
## Codename: GhostWork

---

## 1. SYSTEM PHILOSOPHY

You are the architect and the approver. Everything else is automated.

The system operates on a **"build → run → report → approve"** loop:
- Agents BUILD deliverables and find leads while you sleep/study
- The server RUNS 24/7 on Render (free tier)
- Every morning, the system REPORTS to you via Cowork
- You APPROVE/REJECT in 15 minutes, then walk away

---

## 2. SYSTEM LAYERS

### Layer 0: Always-On Backend (Render + Neon + Cron)
This is the engine that never sleeps. Runs on your proven free stack.

**Components:**
- FastAPI server on Render (free tier)
- PostgreSQL on Neon (Mumbai region)
- cron-job.org pings every 14 min (keep-alive)
- Groq API for all AI inference (free tier)
- Scheduled tasks via APScheduler or cron-job.org webhooks

**What it does while you sleep:**
- Runs lead scraping jobs (Google Maps API / web scraping)
- Processes incoming emails/messages via webhook
- Generates deliverables for active client orders
- Sends scheduled outreach emails
- Logs everything to the database

**Database Schema (Neon PostgreSQL):**
```
leads
├── id, business_name, city, category
├── google_rating, review_count, website_url
├── pain_points_json (AI-extracted from reviews)
├── contact_email, contact_phone
├── status: [new, outreach_sent, responded, converted, rejected]
├── outreach_template_used, last_contacted_at
└── created_at, updated_at

clients
├── id, business_name, owner_name, email
├── service_type: [review_responses, social_content, menu_rewrite]
├── plan: [one_time, monthly]
├── monthly_rate, status: [active, paused, churned]
└── created_at

deliverables
├── id, client_id, type, status: [generating, ready, approved, delivered]
├── content_json (the actual generated content)
├── generated_at, approved_at, delivered_at
└── feedback_notes

outreach_log
├── id, lead_id, template_id, channel: [email, linkedin, whatsapp]
├── sent_at, opened_at, replied_at
├── response_sentiment, follow_up_scheduled
└── status: [sent, opened, replied, converted, dead]

daily_briefing
├── id, date, briefing_json
├── new_leads_count, pending_approvals_count
├── revenue_today, revenue_month
└── generated_at

system_log
├── id, agent_name, action, details_json
├── status: [success, failed, needs_review]
└── timestamp
```

### Layer 1: Claude Cowork (Your Command Center)
This is your 15-minute morning interface. Cowork connects to the backend via API calls and Chrome browser automation.

**Morning Briefing Flow:**
1. You open Cowork
2. Ask: "Give me today's briefing"
3. Cowork hits your FastAPI `/briefing` endpoint
4. Displays: new leads found, deliverables ready for approval, outreach responses received, revenue summary, and anything that needs your attention
5. You approve/reject items one by one
6. Cowork sends your decisions back to the API
7. Backend executes (sends deliverables, follows up, etc.)

**Cowork MCP Connection:**
- Custom MCP server wrapping your FastAPI backend
- OR: Cowork uses Chrome to access a simple admin dashboard you build
- Both approaches work — MCP is cleaner, Chrome dashboard is faster to build first

### Layer 2: Chrome Integration (For Web-Based Tasks)
When Cowork needs to do something on the web that your API can't handle:

- Navigate to Google Business profiles to pull reviews
- Access Fiverr/Upwork to check new orders
- Open Gmail for email context
- Use Google AI Studio or other web tools if needed

---

## 3. THE FIVE AGENTS (Detailed)

### Agent 0: Morning Briefing Agent
**Runs:** On-demand when you open Cowork
**Tech:** Cowork → FastAPI `/api/briefing` endpoint
**Produces:**
```
📊 GHOSTWORK DAILY BRIEFING — March 28, 2026
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 LEADS: 12 new restaurants found overnight
   → 4 in Delhi with <3.5 star ratings (high pain)
   → 3 in Mumbai with no social media presence
   → 5 in Bangalore with poor review responses

📬 OUTREACH: 8 emails sent yesterday
   → 2 opened, 1 replied (interested!)
   → Lead: "Café Zephyr, Delhi" — wants social media help
   → ACTION NEEDED: Approve proposal draft

📦 DELIVERABLES: 3 ready for review
   → 25 review responses for "Tandoor Tales"
   → 30-day content plan for "Brew & Bite"
   → Menu rewrite for "Spice Junction"

💰 REVENUE: ₹0 this month (system just started)
   → Pipeline value: ₹4,500 (3 proposals pending)

⚠️ NEEDS YOUR ATTENTION:
   1. Approve proposal for Café Zephyr
   2. Review 25 responses for Tandoor Tales
   3. Fiverr: 1 new message (check via Chrome)
```

### Agent 1: Lead Prospector
**Runs:** Every night at 2 AM IST (via cron-job.org → FastAPI webhook)
**Tech:** FastAPI + Google Places API (or web scraping) + Groq
**Process:**
1. Searches target cities for restaurants
2. Pulls their Google reviews
3. Groq analyzes reviews for pain points
4. Scores leads by "pain level" (bad ratings + no responses + common complaints)
5. Extracts contact info where available
6. Stores in `leads` table with status "new"
7. Logs action in `system_log`

**Targeting Algorithm:**
- Priority 1: Restaurants with 50+ reviews but < 3.5 stars (lots of pain, lots of data)
- Priority 2: Restaurants that never respond to reviews (easy sell: "you're losing customers")
- Priority 3: Restaurants with no social media or dead social accounts
- Priority 4: New restaurants with < 20 reviews (need visibility)

### Agent 2: Outreach Agent
**Runs:** Every morning at 8 AM IST (before you wake up)
**Tech:** FastAPI + email sending (free SMTP or Resend free tier) + Groq
**Process:**
1. Pulls leads with status "new" (approved by you or auto-approved based on score)
2. Groq generates personalized cold email using lead's pain points
3. Sends email via SMTP
4. Updates `outreach_log`
5. Schedules follow-up for Day 3 and Day 7 if no response
6. When someone replies → flags for your morning briefing

**Email Template (AI-personalized per lead):**
```
Subject: I noticed [Restaurant Name] has some reviews that need attention

Hi [Owner Name],

I came across [Restaurant Name] on Google and noticed you have
[X] reviews that haven't been responded to. Responding to reviews
(especially negative ones) can increase customer return rate by 33%.

I've already drafted responses to your 5 most recent negative reviews
— completely free, no strings attached. Want me to send them over?

— Yuvraaj
AI Product Builder | [your-domain.in]
```

**Key design choice:** The free sample is the hook. Agent 3 pre-generates
this for every lead so it's ready to send immediately if they say yes.

### Agent 3: The Factory (Deliverable Generator)
**Runs:** On-demand when triggered by new order OR pre-generates samples for outreach
**Tech:** FastAPI + Groq API + template system
**Products it can build:**

**Product A: Review Response Pack**
- Input: Google Business reviews (scraped or provided)
- Process: Groq generates personalized, on-brand responses
- Output: Google Sheet or formatted document with all responses
- Time to generate: ~2 minutes for 50 reviews

**Product B: Social Media Content Pack**
- Input: Restaurant name, menu, vibe/aesthetic
- Process: Groq generates 30 days of Instagram captions, post ideas, reel scripts, hashtags
- Output: Content calendar spreadsheet
- Time to generate: ~5 minutes

**Product C: Menu Description Rewrite**
- Input: Current menu (photo or text)
- Process: Groq rewrites each item description to sound appetizing
- Output: Formatted document with before/after
- Time to generate: ~3 minutes

**Product D: Free Sample Generator (for outreach)**
- For every new lead, auto-generates 5 sample review responses
- Stored in database, ready to send instantly when lead shows interest
- This is what makes the outreach powerful — immediate value delivery

### Agent 4: Analytics & Reporter
**Runs:** Weekly summary on Sunday night, daily metrics logged continuously
**Tech:** FastAPI + Neon queries + Groq for insights
**Produces:**
```
📈 WEEKLY REPORT — Week of March 22, 2026
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FUNNEL:
  Leads found:     87
  Outreach sent:   34
  Opened:          12 (35% open rate)
  Replied:          4 (12% reply rate)
  Converted:        1 (new client!)

REVENUE:
  This week:    ₹1,500
  This month:   ₹3,000
  LTV estimate: ₹6,000/month at current trajectory

WHAT'S WORKING:
  → "Free sample" emails get 3x more replies than generic pitch
  → Review response service has highest conversion
  → Delhi restaurants respond faster than Mumbai

RECOMMENDATION:
  → Double down on Delhi targeting
  → Create Fiverr gig for review responses (supplement inbound)
  → Consider raising price from ₹500 to ₹800 (demand supports it)
```

---

## 4. TECHNICAL IMPLEMENTATION PLAN

### Phase 1: Foundation (Week 1-2)
Build the backend skeleton and database.

- [ ] FastAPI project setup with the database schema above
- [ ] Basic CRUD endpoints for leads, clients, deliverables
- [ ] `/api/briefing` endpoint that compiles the morning report
- [ ] Deploy to Render + Neon
- [ ] cron-job.org keep-alive ping

### Phase 2: The Factory — Agent 3 (Week 2-3)
This is the revenue engine, so it comes first.

- [ ] Review response generator (Groq API integration)
- [ ] Social media content generator
- [ ] Menu description rewriter
- [ ] Output formatting (JSON → Google Sheets / downloadable docs)
- [ ] `/api/generate/{product_type}` endpoint

### Phase 3: Lead Prospector — Agent 1 (Week 3-4)
- [ ] Google Places API integration (or scraping fallback)
- [ ] Review scraping + Groq pain-point analysis
- [ ] Lead scoring algorithm
- [ ] Scheduled nightly runs via cron webhook
- [ ] Free sample auto-generation for each new lead

### Phase 4: Outreach — Agent 2 (Week 4-5)
- [ ] Email template system with Groq personalization
- [ ] SMTP integration (Resend free tier: 100 emails/day)
- [ ] Follow-up scheduling (Day 3, Day 7)
- [ ] Reply detection (webhook or polling)
- [ ] Status tracking in outreach_log

### Phase 5: Command Center — Agent 0 + Cowork (Week 5-6)
- [ ] Build simple admin dashboard (Next.js on Vercel)
- [ ] Morning briefing page with approve/reject buttons
- [ ] Connect Cowork to dashboard via Chrome
- [ ] OR: Build custom MCP server for direct API access
- [ ] Test the full morning workflow

### Phase 6: Analytics — Agent 4 (Week 6-7)
- [ ] Weekly report generation endpoint
- [ ] Funnel metrics calculation
- [ ] Groq-powered insight generation
- [ ] Auto-email weekly report to yourself

### Phase 7: Polish & Scale (Week 7+)
- [ ] Fiverr/Upwork gig listings (using deliverables as samples)
- [ ] Client onboarding flow
- [ ] Payment integration (Razorpay for Indian clients)
- [ ] Multi-city expansion
- [ ] Add more product types based on demand

---

## 5. COST ANALYSIS (Monthly)

| Service | Cost | Notes |
|---------|------|-------|
| Render (backend) | ₹0 | Free tier |
| Neon (database) | ₹0 | Free tier, Mumbai region |
| Groq API | ₹0 | Free tier (generous limits) |
| Vercel (dashboard) | ₹0 | Free tier |
| cron-job.org | ₹0 | Free tier |
| Resend (email) | ₹0 | 100 emails/day free |
| Google Places API | ₹0* | $200/month free credit |
| Domain (.in) | ~₹500/year | One-time investment |
| **TOTAL** | **₹0/month** | Until you hit scale limits |

*Google Places API gives $200 free monthly credit = ~10,000 place searches.
At scale, this is the first thing that might cost money.

---

## 6. REVENUE PROJECTIONS (Conservative)

| Month | Clients | Avg Revenue/Client | Monthly Revenue |
|-------|---------|-------------------|-----------------|
| 1 | 2 | ₹750 | ₹1,500 |
| 2 | 5 | ₹1,000 | ₹5,000 |
| 3 | 10 | ₹1,200 | ₹12,000 |
| 6 | 20 | ₹1,500 | ₹30,000 |

These assume a mix of one-time and monthly clients.
₹30,000/month while studying for JEE. That's the target.

---

## 7. RISK MITIGATION

| Risk | Mitigation |
|------|-----------|
| Groq rate limits | Queue system + retry logic |
| Render cold starts | cron-job.org pings every 14 min |
| Email deliverability | Use Resend (good reputation) + warm up slowly |
| No clients respond | Iterate email templates based on Agent 4 data |
| Google API costs | Start with scraping, upgrade to API when revenue covers it |
| Cowork server busy | Dashboard works independently — Cowork is convenience, not dependency |

---

## 8. KEY ARCHITECTURAL DECISIONS

1. **Cowork is the UI, not the engine.** If Cowork is down or busy, everything still runs. You can use the web dashboard directly.

2. **Backend-first design.** Every agent's logic lives in FastAPI. Cowork just calls endpoints. This means you can swap Cowork for any other interface later.

3. **Database is the source of truth.** Every action, every lead, every deliverable is logged. Nothing happens in memory only.

4. **AI is a function call, not a dependency.** Groq is called via simple API endpoints. If Groq dies, swap to another provider in one line of code.

5. **Free until proven.** Zero cost until the system proves it makes money. Only invest when revenue demands it.

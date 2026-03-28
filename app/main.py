from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.database import Base, init_engine
from app.routers import leads, clients, deliverables, outreach, briefing, system, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: init DB engine and create all tables
    init_engine()
    from app.database import engine, AsyncSessionLocal

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Log startup
    async with AsyncSessionLocal() as db:
        from app.models import SystemLog
        log = SystemLog(agent_name="system", action="server_started", status="success")
        db.add(log)
        await db.commit()

    yield

    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="GhostWork API",
    description="Autonomous Business OS for restaurant client acquisition and service delivery",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router)
app.include_router(leads.router)
app.include_router(clients.router)
app.include_router(deliverables.router)
app.include_router(outreach.router)
app.include_router(briefing.router)
app.include_router(system.router)


@app.get("/")
async def root():
    return {
        "service": "GhostWork API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/debug/tables")
async def debug_tables():
    """List all tables in the database — debug endpoint."""
    from app.database import AsyncSessionLocal
    init_engine()
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        )
        tables = [row[0] for row in result.all()]
    return {"tables": tables}


@app.get("/debug/counts")
async def debug_counts():
    """Row counts for all tables — debug endpoint."""
    from app.database import AsyncSessionLocal
    init_engine()
    table_names = ["leads", "clients", "deliverables", "outreach_log", "daily_briefing", "system_log"]
    counts = {}
    async with AsyncSessionLocal() as db:
        for table in table_names:
            result = await db.execute(text(f"SELECT COUNT(*) FROM {table}"))  # noqa: S608 — internal debug only, no user input
            counts[table] = result.scalar()
    return counts

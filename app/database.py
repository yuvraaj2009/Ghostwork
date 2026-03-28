from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


engine = None
AsyncSessionLocal = None


def init_engine():
    global engine, AsyncSessionLocal
    if engine is not None:
        return

    from app.config import get_settings
    settings = get_settings()

    engine = create_async_engine(
        settings.database_url,
        echo=settings.environment == "development",
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    init_engine()
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

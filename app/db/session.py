from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine 
from app.core.config import settings

# Async Engine (for FastAPI)
engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, echo=True)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Sync Engine (for Celery / Scripts)
# We need to replace 'postgresql+asyncpg' with 'postgresql' for sync driver
SYNC_DATABASE_URI = settings.SQLALCHEMY_DATABASE_URI.replace("postgresql+asyncpg", "postgresql")
sync_engine = create_engine(SYNC_DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

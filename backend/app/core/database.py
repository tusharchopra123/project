import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import logging
from dotenv import load_dotenv
import os
from pathlib import Path

# Load .env from backend/ directory (two levels up from app/core/)
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Production: Use DATABASE_URL env var (Postgres)
# Local: Fallback to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./finance.db")

# Sanitize input (remove potential spaces or quotes from .env copy-paste)
if DATABASE_URL:
    DATABASE_URL = DATABASE_URL.strip().strip("'").strip('"')

    # Force async driver for SQLAlchemy (asyncpg)
    # Handle "postgres://" (Railway/Heroku style)
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
    # Handle "postgresql://" (Supabase/Standard style)
    elif DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

print(f"DEBUG: Connecting to Database -> {'POSTGRES (Cloud)' if 'postgres' in DATABASE_URL else 'SQLITE (Local)'}")
# print(f"DEBUG: URL Prefix -> {DATABASE_URL.split('://')[0] if '://' in DATABASE_URL else 'INVALID'}") # Safe debug

# Create async engine
engine = create_async_engine(
    DATABASE_URL, 
    echo=False, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Session factory
SessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Base class for models
class Base(DeclarativeBase):
    pass

# Dependency to get DB session
async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Initialize DB (create tables)
# Import models to ensure they are registered
from ..models import User, PortfolioSnapshot

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

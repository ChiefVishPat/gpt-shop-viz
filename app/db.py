"""
Database configuration for asynchronous SQLAlchemy.

- Loads environment variables for Postgres connection.
- Creates AsyncEngine and async_sessionmaker for DB sessions.
- init_models() can be used to auto-create tables if not using Alembic.
"""

import os

from dotenv import load_dotenv
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

load_dotenv()
DATABASE_URL = URL.create(
    drivername='postgresql+asyncpg',
    username=os.environ['POSTGRES_USER'],
    password=os.environ['POSTGRES_PASSWORD'],
    host=os.environ['POSTGRES_HOST'],
    port=int(os.environ['POSTGRES_PORT']),
    database=os.environ['POSTGRES_DB'],
)

engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_models() -> None:
    """Optional: auto-create tables at startup if you’re not using Alembic."""
    from app.models import Base

    async with engine.begin() as conn:
        # Create database tables based on ORM metadata if not using Alembic
        await conn.run_sync(Base.metadata.create_all)

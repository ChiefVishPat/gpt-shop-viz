import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

load_dotenv()
# build SQLALCHEMY_DATABASE_URL from POSTGRES_* vars if necessary to expand placeholders
if all(
    k in os.environ
    for k in ('POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_HOST', 'POSTGRES_PORT', 'POSTGRES_DB')
):
    os.environ['SQLALCHEMY_DATABASE_URL'] = (
        f'postgresql+asyncpg://{os.environ["POSTGRES_USER"]}:{os.environ["POSTGRES_PASSWORD"]}'
        f'@{os.environ["POSTGRES_HOST"]}:{os.environ["POSTGRES_PORT"]}/{os.environ["POSTGRES_DB"]}'
    )
DATABASE_URL: str = os.environ['SQLALCHEMY_DATABASE_URL']

engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_models() -> None:
    """Optional: auto-create tables at startup if you’re not using Alembic."""
    from app.models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

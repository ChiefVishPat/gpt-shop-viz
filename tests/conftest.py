import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

import app.db as app_db
from app.main import app as fastapi_app
from app.models import Base


@pytest.fixture
async def engine():
    """
    Create a fresh in-memory SQLite database for the test session.
    Requires the 'aiosqlite' package to be installed.
    """
    try:
        import aiosqlite  # noqa: F401
    except ImportError:
        pytest.skip('aiosqlite is required for database tests')
    url = 'sqlite+aiosqlite:///:memory:'
    engine = create_async_engine(
        url,
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
        future=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(engine):
    """
    Provide a transactional session for a test, rolling back at the end.
    """
    maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
def override_db(monkeypatch, db_session):
    """
    Override the database dependency and session maker to use the test DB.
    """
    # Patch AsyncSessionLocal to return our test session
    monkeypatch.setattr(app_db, 'AsyncSessionLocal', lambda: db_session)
    # Override FastAPI dependency
    import app.main as app_main

    async def _get_test_db():
        yield db_session

    app_main.app.dependency_overrides[app_main.get_db] = _get_test_db


@pytest.fixture
async def client():
    """
    Async HTTP client for testing FastAPI endpoints using ASGI transport.
    """
    import httpx

    transport = httpx.ASGITransport(app=fastapi_app)
    async with httpx.AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac

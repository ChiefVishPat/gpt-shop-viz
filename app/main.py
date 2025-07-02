"""
FastAPI REST API for gpt-shop-viz.

Provides endpoints to create and list products, manage snapshots,
and query snapshot history and best price information.
"""

from contextlib import asynccontextmanager
from datetime import date, datetime, time, timezone
from typing import AsyncGenerator, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.db import AsyncSessionLocal
from scraper.openai_client import fetch_shopping_items


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore
    # auto-create tables if they do not exist, retry until the database is ready
    import asyncio

    from app.db import init_models

    retries = 5
    while True:
        try:
            await init_models()
            break
        except Exception:
            retries -= 1
            if not retries:
                raise
            await asyncio.sleep(2)
    yield


app = FastAPI(title='gpt-shop-viz', lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


# Use module-level constants for Query defaults to satisfy lint rules (B008)
_DEFAULT_DATE_QUERY = Query(None)


@app.get('/health', tags=['health'])
async def health_check() -> dict[str, str]:
    return {'status': 'ok'}


# The database initialization has been moved into the lifespan context above.


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    session: AsyncSession = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()


db_dep = Depends(get_db)


@app.post('/products', response_model=schemas.ProductRead)
async def create_product(
    product_in: schemas.ProductCreate, db: AsyncSession = db_dep
) -> schemas.ProductRead:
    # create product entry and bootstrap initial snapshots via OpenAI
    product = await crud.create_product(db, product_in)
    items = await fetch_shopping_items(product.prompt or product.name)
    for item in items:
        snap_in = schemas.SnapshotCreate(
            product_id=product.id,
            title=item['title'],
            price=item.get('price'),
            urls=item.get('urls', []),
        )
        await crud.create_snapshot(db, snap_in)
    return product


@app.get('/products', response_model=List[schemas.ProductRead])
async def list_products(
    db: AsyncSession = db_dep,
) -> List[schemas.ProductRead]:
    return await crud.get_products(db)


@app.get('/products/{product_id}', response_model=schemas.ProductRead)
async def read_product(
    product_id: int,
    db: AsyncSession = db_dep,
) -> schemas.ProductRead:
    """Get a single product and all its snapshots."""
    prod = await crud.get_product(db, product_id)
    if not prod:
        raise HTTPException(status_code=404, detail='Product not found')
    return prod


@app.post('/snapshot', response_model=schemas.SnapshotRead)
async def create_snapshot(
    snap_in: schemas.SnapshotCreate, db: AsyncSession = db_dep
) -> schemas.SnapshotRead:
    # ensure the parent product exists
    product = await crud.get_product(db, snap_in.product_id)
    if not product:
        raise HTTPException(status_code=404, detail='Product not found')
    return await crud.create_snapshot(db, snap_in)


@app.get('/products/{product_id}/latest', response_model=List[schemas.SnapshotRead])
async def latest_snapshots(
    product_id: int,
    db: AsyncSession = db_dep,
) -> List[schemas.SnapshotRead]:
    """
    Get all snapshots for a product at the most recent capture time.
    """
    snaps = await crud.get_latest_snapshots(db, product_id)
    if not snaps:
        raise HTTPException(status_code=404, detail='Snapshot not found')
    return snaps


@app.get('/products/{product_id}/history', response_model=List[schemas.SnapshotRead])
async def snapshot_history(
    product_id: int, days: int = 7, db: AsyncSession = db_dep
) -> List[schemas.SnapshotRead]:
    return await crud.get_snapshot_history(db, product_id, days)


@app.get('/products/{product_id}/best_price', response_model=schemas.SnapshotRead)
async def best_price(
    product_id: int,
    start_date: Optional[date] = _DEFAULT_DATE_QUERY,
    end_date: Optional[date] = _DEFAULT_DATE_QUERY,
    db: AsyncSession = db_dep,
) -> schemas.SnapshotRead:
    """
    Get the snapshot with the lowest price for a product between start_date and end_date inclusive.
    If start_date is missing, includes all snapshots from the earliest capture timestamp.
    If end_date is missing, uses the current UTC timestamp as the upper bound.
    """
    # Convert query dates to UTC datetimes or leave lower bound unbounded
    start_dt = (
        datetime.combine(start_date, time.min).replace(tzinfo=timezone.utc) if start_date else None
    )
    end_dt = (
        datetime.combine(end_date, time.max).replace(tzinfo=timezone.utc)
        if end_date
        else datetime.now(timezone.utc)
    )
    snap = await crud.get_lowest_price_period(db, product_id, start_dt, end_dt)
    if not snap:
        raise HTTPException(status_code=404, detail='No snapshots found in the given date range')
    return snap

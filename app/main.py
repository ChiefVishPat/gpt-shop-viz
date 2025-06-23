from typing import AsyncGenerator, List

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.db import AsyncSessionLocal

app = FastAPI(title='gpt-shop-viz')


@app.get('/health', tags=['health'])
async def health_check() -> dict[str, str]:
    return {'status': 'ok'}


# Load environment variables from .env before app startup
load_dotenv()


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
    return await crud.create_product(db, product_in)


@app.get('/products', response_model=List[schemas.ProductRead])
async def list_products(
    db: AsyncSession = db_dep,
) -> List[schemas.ProductRead]:
    return await crud.get_products(db)


@app.post('/snapshot', response_model=schemas.SnapshotRead)
async def create_snapshot(
    snap_in: schemas.SnapshotCreate, db: AsyncSession = db_dep
) -> schemas.SnapshotRead:
    # ensure the parent product exists
    product = await crud.get_product(db, snap_in.product_id)
    if not product:
        raise HTTPException(status_code=404, detail='Product not found')
    return await crud.create_snapshot(db, snap_in)


@app.get('/products/{product_id}/latest', response_model=schemas.SnapshotRead)
async def latest_snapshot(product_id: int, db: AsyncSession = db_dep) -> schemas.SnapshotRead:
    snap = await crud.get_latest_snapshot(db, product_id)
    if not snap:
        raise HTTPException(status_code=404, detail='Snapshot not found')
    return snap


@app.get('/products/{product_id}/history', response_model=List[schemas.SnapshotRead])
async def snapshot_history(
    product_id: int, days: int = 7, db: AsyncSession = db_dep
) -> List[schemas.SnapshotRead]:
    return await crud.get_snapshot_history(db, product_id, days)

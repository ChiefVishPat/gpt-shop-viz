from datetime import datetime
from typing import List, Optional

from sqlalchemy import func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models import Product, Snapshot
from app.schemas import (
    ProductCreate,
    ProductRead,
    SnapshotCreate,
    SnapshotRead,
)


async def get_or_create_product(db: AsyncSession, name: str, prompt: str) -> Product:
    result = await db.execute(select(Product).where(Product.prompt == prompt))
    prod = result.scalar_one_or_none()
    if prod:
        return prod

    prod = Product(name=name, prompt=prompt)
    db.add(prod)
    await db.commit()
    await db.refresh(prod)
    return prod


async def create_product(db: AsyncSession, product_in: ProductCreate) -> ProductRead:
    # 1) Insert the Product
    db_obj = Product(**product_in.model_dump())
    db.add(db_obj)
    await db.commit()

    # 2) Re-load it with snapshots eagerly fetched (will be [])
    result = await db.execute(
        select(Product).where(Product.id == db_obj.id).options(selectinload(Product.snapshots))
    )
    prod = result.scalar_one()

    # 3) Return via Pydantic
    return ProductRead.model_validate(prod)


async def get_products(db: AsyncSession) -> List[ProductRead]:
    result = await db.execute(
        select(Product).options(selectinload(Product.snapshots)).order_by(Product.id)
    )
    return [ProductRead.model_validate(p) for p in result.scalars().all()]


async def get_product(db: AsyncSession, product_id: int) -> ProductRead | None:
    result = await db.execute(
        select(Product).where(Product.id == product_id).options(selectinload(Product.snapshots))
    )
    prod = result.scalar_one_or_none()
    return ProductRead.model_validate(prod) if prod else None


async def create_snapshot(db: AsyncSession, snapshot: SnapshotCreate) -> SnapshotRead:
    # Exclude None values to allow database default for captured_at when not specified.
    db_obj = Snapshot(**snapshot.model_dump(exclude_none=True))
    db.add(db_obj)
    # commit immediately so it's visible in the DB
    await db.commit()
    await db.refresh(db_obj)
    return SnapshotRead.model_validate(db_obj)


async def get_latest_snapshots(db: AsyncSession, product_id: int) -> list[SnapshotRead]:
    """
    Return all snapshots for product_id having the most recent timestamp.
    """
    # find the most recent capture time for this product
    max_ts_res = await db.execute(
        select(func.max(Snapshot.captured_at)).where(Snapshot.product_id == product_id)
    )
    max_ts = max_ts_res.scalar_one_or_none()
    if not max_ts:
        return []

    # fetch all snapshots at that timestamp
    result = await db.execute(
        select(Snapshot).where(
            Snapshot.product_id == product_id,
            Snapshot.captured_at == max_ts,
        )
    )
    return [SnapshotRead.model_validate(s) for s in result.scalars().all()]


async def get_snapshot_history(db: AsyncSession, product_id: int, days: int) -> List[SnapshotRead]:
    interval_str = text(f"interval '{days} days'")
    result = await db.execute(
        select(Snapshot)
        .where(
            Snapshot.product_id == product_id,
            Snapshot.captured_at >= func.now() - interval_str,
        )
        .order_by(Snapshot.captured_at)
    )
    return [SnapshotRead.model_validate(s) for s in result.scalars().all()]


async def get_lowest_price_period(
    db: AsyncSession,
    product_id: int,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> SnapshotRead | None:
    """
    Return the snapshot with the lowest price for product_id between start and end datetimes.
    If start is None, no lower bound is applied. If end is None, no upper bound is applied.
    """
    stmt = (
        select(Snapshot).where(Snapshot.product_id == product_id).where(Snapshot.price.is_not(None))
    )
    if start is not None:
        stmt = stmt.where(Snapshot.captured_at >= start)
    if end is not None:
        stmt = stmt.where(Snapshot.captured_at <= end)
    stmt = stmt.order_by(Snapshot.price.asc(), Snapshot.captured_at.asc()).limit(1)

    result = await db.execute(stmt)
    snap = result.scalar_one_or_none()
    return SnapshotRead.model_validate(snap) if snap else None

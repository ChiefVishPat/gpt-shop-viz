"""
CRUD operations for Product and Snapshot entities.

Provides async functions to create, retrieve, and query products and their snapshots.
"""

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
    """
    Retrieve a Product by prompt, or create it if it does not exist.

    :param db: Async database session
    :param name: The product name to store if creating
    :param prompt: The unique prompt used as lookup key
    :return: The existing or newly created Product instance
    """
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
    """
    Create a new Product and return it with its initial empty snapshots list.

    :param db: Async database session
    :param product_in: ProductCreate schema with name and prompt
    :return: ProductRead schema including snapshots field
    """
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
    """
    Retrieve all products with their snapshots.

    :param db: Async database session
    :return: List of ProductRead schemas
    """
    result = await db.execute(
        select(Product).options(selectinload(Product.snapshots)).order_by(Product.id)
    )
    return [ProductRead.model_validate(p) for p in result.scalars().all()]


async def get_product(db: AsyncSession, product_id: int) -> ProductRead | None:
    """
    Retrieve a single product by ID, including its snapshots.

    :param db: Async database session
    :param product_id: ID of the product to retrieve
    :return: ProductRead schema or None if not found
    """
    result = await db.execute(
        select(Product).where(Product.id == product_id).options(selectinload(Product.snapshots))
    )
    prod = result.scalar_one_or_none()
    return ProductRead.model_validate(prod) if prod else None


async def create_snapshot(db: AsyncSession, snapshot: SnapshotCreate) -> SnapshotRead:
    """
    Create a new Snapshot record for a product.

    :param db: Async database session
    :param snapshot: SnapshotCreate schema with product_id, title, price, urls, and optional captured_at
    :return: SnapshotRead schema of the newly created snapshot
    """
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
    """
    Return the list of snapshots for a product over the past N days.

    :param db: Async database session
    :param product_id: ID of the product to query
    :param days: Number of days to look back from now
    :return: List of SnapshotRead schemas ordered by captured_at
    """
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
    If multiple snapshots share the same lowest price, return the most recent one.
    If start is None, no lower bound is applied. If end is None, no upper bound is applied.
    """
    stmt = (
        select(Snapshot).where(Snapshot.product_id == product_id).where(Snapshot.price.is_not(None))
    )
    if start is not None:
        stmt = stmt.where(Snapshot.captured_at >= start)
    if end is not None:
        stmt = stmt.where(Snapshot.captured_at <= end)
    stmt = stmt.order_by(Snapshot.price.asc(), Snapshot.captured_at.desc()).limit(1)

    result = await db.execute(stmt)
    snap = result.scalar_one_or_none()
    return SnapshotRead.model_validate(snap) if snap else None

from typing import List

from sqlalchemy import func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import Product, Snapshot
from app.schemas import (
    ProductCreate,
    ProductRead,
    SnapshotCreate,
    SnapshotRead,
)


async def get_or_create_product(db: AsyncSession, name: str, prompt: str) -> Product:
    q = await db.execute(select(Product).where(Product.prompt == prompt))
    prod = q.scalar_one_or_none()
    if prod:
        return prod

    prod = Product(name=name, prompt=prompt)
    db.add(prod)
    await db.commit()
    await db.refresh(prod)
    return prod


async def create_product(db: AsyncSession, product_in: ProductCreate) -> ProductRead:
    db_obj = Product(**product_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return ProductRead.model_validate(db_obj)


async def get_products(db: AsyncSession) -> List[ProductRead]:
    result = await db.execute(select(Product).order_by(Product.id))
    return [ProductRead.model_validate(p) for p in result.scalars().all()]


async def get_product(db: AsyncSession, product_id: int) -> ProductRead | None:
    result = await db.execute(select(Product).where(Product.id == product_id))
    prod = result.scalar_one_or_none()
    return ProductRead.model_validate(prod) if prod else None


async def create_snapshot(db: AsyncSession, snapshot: SnapshotCreate) -> SnapshotRead:
    db_obj = Snapshot(**snapshot.model_dump())
    db.add(db_obj)
    await db.flush()
    await db.refresh(db_obj)
    return SnapshotRead.model_validate(db_obj)


async def get_latest_snapshot(db: AsyncSession, product_id: int) -> SnapshotRead | None:
    stmt = (
        select(Snapshot)
        .where(Snapshot.product_id == product_id)
        .order_by(Snapshot.captured_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    snap = result.scalar_one_or_none()
    return SnapshotRead.model_validate(snap) if snap else None


async def get_snapshot_history(db: AsyncSession, product_id: int, days: int) -> List[SnapshotRead]:
    interval_literal = text(f"interval '{days} days'")
    stmt = (
        select(Snapshot)
        .where(
            Snapshot.product_id == product_id,
            Snapshot.captured_at >= func.now() - interval_literal,
        )
        .order_by(Snapshot.captured_at)
    )
    result = await db.execute(stmt)
    return [SnapshotRead.model_validate(s) for s in result.scalars().all()]

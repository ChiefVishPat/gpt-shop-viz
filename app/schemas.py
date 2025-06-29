from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


# ─── Snapshot Schemas ──────────────────────────────────────────────────────
class SnapshotBase(BaseModel):
    product_id: int
    title: str
    price: Optional[Decimal] = None
    urls: List[str] = Field(default_factory=list)


class SnapshotCreate(SnapshotBase):
    """Fields required to create a snapshot."""

    pass


class SnapshotRead(SnapshotBase):
    """Fields returned in API responses."""

    id: int
    captured_at: datetime

    class Config:
        from_attributes = True


# ─── Product Schemas ───────────────────────────────────────────────────────
class ProductBase(BaseModel):
    name: str
    prompt: Optional[str] = None


class ProductCreate(ProductBase):
    """Fields required to create a product."""

    pass


class ProductRead(ProductBase):
    """Fields returned in API responses."""

    id: int
    created_at: datetime
    snapshots: List[SnapshotRead] = Field(default_factory=list)

    class Config:
        from_attributes = True

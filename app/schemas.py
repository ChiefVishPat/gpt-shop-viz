"""
Pydantic schemas for gpt-shop-viz API models.

Defines base, create, and read schemas for Product and Snapshot entities.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


# ─── Snapshot Schemas ──────────────────────────────────────────────────────
class SnapshotBase(BaseModel):
    product_id: int
    title: str
    price: Optional[Decimal] = None
    urls: List[str] = Field(default_factory=list)


class SnapshotCreate(SnapshotBase):
    """Fields required to create a snapshot."""

    # Optional timestamp for when the snapshot was captured. If not provided, defaults to now.
    captured_at: Optional[datetime] = None


class SnapshotRead(SnapshotBase):
    """Fields returned in API responses."""

    id: int
    captured_at: datetime

    model_config = ConfigDict(from_attributes=True)


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

    model_config = ConfigDict(from_attributes=True)

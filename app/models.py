from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    JSON,
    TIMESTAMP,
    ForeignKey,
    Integer,
    Numeric,
    Text,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text('NOW()'),
    )
    snapshots: Mapped[List['Snapshot']] = relationship(
        'Snapshot', back_populates='product', cascade='all, delete-orphan'
    )


class Snapshot(Base):
    __tablename__ = 'snapshots'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey('products.id', ondelete='CASCADE'), nullable=False
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    urls: Mapped[list[str]] = mapped_column(JSON, nullable=True)
    captured_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text('NOW()'),
    )
    product: Mapped['Product'] = relationship('Product', back_populates='snapshots')

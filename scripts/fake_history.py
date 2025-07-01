"""
Seed fake price history for existing products.

Generates and inserts 30 days of randomized snapshots per product
using realistic timestamps and price fluctuations.
"""

import asyncio
import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from faker import Faker
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.crud import create_snapshot
from app.db import AsyncSessionLocal
from app.models import Product
from app.schemas import SnapshotCreate

# Initialize Faker for generating realistic timestamps
fake = Faker()


async def seed_fake_history() -> None:
    """
    Generate and insert 30 days of fake price history for each product.
    Each snapshot will have a realistic timestamp within the target day.
    """
    async with AsyncSessionLocal() as db:
        # Load all products along with their existing snapshots
        result = await db.execute(select(Product).options(selectinload(Product.snapshots)))
        products = result.scalars().all()

        for product in products:
            # Skip products without any initial snapshot
            if not product.snapshots:
                continue

            # Determine the base price from the most recent snapshot
            latest = max(product.snapshots, key=lambda s: s.captured_at)
            base_price = float(latest.price or 0)

            # Generate a snapshot for each of the past 30 days
            for days_ago in range(1, 31):
                # Compute a random timestamp within the target day
                target_day = datetime.now(timezone.utc) - timedelta(days=days_ago)
                start = target_day.replace(hour=0, minute=0, second=0, microsecond=0)
                end = target_day.replace(hour=23, minute=59, second=59, microsecond=999999)
                captured_at = fake.date_time_between_dates(
                    datetime_start=start,
                    datetime_end=end,
                    tzinfo=timezone.utc,
                )

                # Apply a small random price fluctuation (+/-10%) and convert to Decimal
                price_float = round(base_price * random.uniform(0.9, 1.1), 2)
                price = Decimal(price_float).quantize(Decimal('0.01'))

                # Create and insert the fake snapshot
                snapshot_in = SnapshotCreate(
                    product_id=product.id,
                    title=product.name,
                    price=price,
                    urls=latest.urls,
                    captured_at=captured_at,
                )
                await create_snapshot(db, snapshot_in)

    print('✅ Seeded 30 days of fake price history for each product.')


def main() -> None:
    """Entry point for the script."""
    asyncio.run(seed_fake_history())


if __name__ == '__main__':
    main()

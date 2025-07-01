"""
Bulk load products and initial snapshots from CSV.

Parses an CSV of sales data, converts prices to USD, upserts products,
and creates initial snapshots with product links.
"""

import asyncio
import csv
import re
from decimal import Decimal
from pathlib import Path

from app.crud import create_product, create_snapshot
from app.db import AsyncSessionLocal
from app.schemas import ProductCreate, SnapshotCreate

# Locate the CSV file in the project root (one level above this script)
SCRIPT_DIR = Path(__file__).resolve().parent
CSV_FILE = SCRIPT_DIR.parent / 'amazon-sales.csv'

# Exchange rate from Indian Rupees to US Dollars
INR_TO_USD = Decimal('0.012')


async def load_products() -> None:
    """
    Bulk load products from the CSV file, convert prices from INR to USD,
    upsert each product, and create an initial price snapshot.
    """
    async with AsyncSessionLocal() as db:
        # Open the CSV file and read row by row
        with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Use discounted_price if available, otherwise fall back to actual_price
                price_str = row.get('discounted_price') or row.get('actual_price')
                if not price_str:
                    continue

                # Remove currency symbols, commas, and any non-numeric characters
                raw = re.sub(r'[^\d.]', '', price_str)
                if not raw:
                    continue
                price_inr = Decimal(raw)

                # Convert INR to USD and round to 2 decimal places
                price_usd = (price_inr * INR_TO_USD).quantize(Decimal('0.01'))

                # Prepare product data
                name = row.get('product_name', '').strip()
                prompt = name

                # Upsert product
                product_in = ProductCreate(name=name, prompt=prompt)
                product = await create_product(db, product_in)

                # Create initial snapshot with product link URL
                urls = []
                link = row.get('product_link')
                if link:
                    urls.append(link.strip())

                snapshot_in = SnapshotCreate(
                    product_id=product.id,
                    title=name,
                    price=price_usd,
                    urls=urls,
                )
                await create_snapshot(db, snapshot_in)

    print('✅ Loaded products and created initial snapshots.')


def main() -> None:
    """Entry point for the script."""
    asyncio.run(load_products())


if __name__ == '__main__':
    main()

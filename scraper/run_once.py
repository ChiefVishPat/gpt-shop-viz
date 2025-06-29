"""
Entry point for the scraping job.
Fetches shopping items from OpenAI and persists snapshots to the database.
"""

import argparse
import asyncio
import logging
import pprint

from dotenv import load_dotenv

from app import crud, schemas
from app.db import AsyncSessionLocal, init_models
from scraper.openai_client import fetch_shopping_items

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main(prompt: str, no_db: bool) -> None:
    """Fetch items for the given prompt and optionally save to the database."""
    # 1) pull data from OpenAI
    items = await fetch_shopping_items(prompt)

    # 2) print out the raw result
    print('\n✅ Parsed JSON:')
    pprint.pp(items)

    # 3) bail out early if user passed --no-db
    if no_db:
        return

    # 4) ensure tables exist (only if you're not running migrations)
    await init_models()

    # 5) open a single transactional session
    async with AsyncSessionLocal() as db:
        # upsert the Product row (keyed by prompt)
        product = await crud.get_or_create_product(
            db,
            name=prompt,
            prompt=prompt,
        )

        # 6) write each Snapshot in turn
        for idx, item in enumerate(items, start=1):
            snap_in = schemas.SnapshotCreate(
                product_id=product.id,
                title=item['title'],
                price=item.get('price'),
                urls=item.get('urls', []),
            )
            snap = await crud.create_snapshot(db, snap_in)
            print(f'✅ Saved snapshot {snap.id} (rank {idx})')


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for scraper."""
    parser = argparse.ArgumentParser(description='Fetch shopping items and optionally save to DB')
    parser.add_argument('-p', '--prompt', required=True, help='Shopping prompt for OpenAI')
    parser.add_argument(
        '--no-db', action='store_true', help='Only print results, do not persist to DB'
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    asyncio.run(main(args.prompt, args.no_db))

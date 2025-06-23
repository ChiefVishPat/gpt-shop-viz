"""
Entry point for the scraping job.
Currently a stub that should be implemented with actual scraping logic.
"""

import asyncio
import logging

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    logger.info('Scraper stub: no implementation yet')


if __name__ == '__main__':
    asyncio.run(main())

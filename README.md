# gpt-shop-viz

gpt-shop-viz is a Python service that takes shopping prompts (e.g. "Show me headsets under $150 for PS5")
and returns a JSON array of products via OpenAI. It persists each run as a Snapshot in Postgres and exposes
both history and real-time views via a FastAPI REST API.

## Features

- Async SQLAlchemy 2.0 models & Pydantic v2 schemas
- Alembic migrations
- OpenAI integration
- CLI tool for one-off fetches
- FastAPI REST API (health, products list, latest snapshot, history)
- Dockerized services (Postgres, API, scraper)

## Prerequisites

- Docker & Docker Compose
- An OpenAI API key

## Setup

1. Copy the example environment file and update credentials:
   ```bash
   cp .env.example .env
   ```
   Update `.env` with your OpenAI API key and Postgres credentials.

2. Build and start containers:
   ```bash
   docker-compose up --build -d
   ```

3. Run database migrations:
   ```bash
   docker-compose exec api alembic upgrade head
   ```

4. (Optional) Run a one-off scrape via the CLI:
   ```bash
   docker-compose exec scraper python -m scraper.run_once -p "Show me headsets under $150 for PS5"
   ```

5. Explore the API (on port 8000):
   ```bash
  
   curl -X 'GET' \
  'http://localhost:8000/health' \
  -H 'accept: application/json'


   curl http://localhost:8000/products
   curl http://localhost:8000/products/{product_id}
   curl http://localhost:8000/products/{product_id}/latest
   curl http://localhost:8000/products/{product_id}/history?days=7
   ```

## Local Development

Alternatively, to run locally without Docker:

```bash
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python -m scraper.run_once -p "Your shopping prompt"
uvicorn app.main:app --reload
```
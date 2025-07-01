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

5. Explore the interactive API docs at http://localhost:8000/docs

## Local Development

Alternatively, to run locally without Docker:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
cp .env.example .env
alembic upgrade head
python -m scraper.run_once -p "Your shopping prompt"
uvicorn app.main:app --reload
```

## Architecture

gpt-shop-viz consists of three main components:

- **Scraper**: A CLI tool that sends shopping prompts to OpenAI and stores JSON snapshots in Postgres.
- **API**: A FastAPI service exposing REST endpoints for health checks, listing products, fetching snapshots, history queries, and best price lookups.
- **Frontend**: A Next.js + TypeScript + Tailwind CSS application displaying dashboards for products and snapshots.

## Project Structure

```
.
├── app                 # FastAPI application, CRUD logic, database models & schemas
├── scraper             # OpenAI-based scraper CLI and client logic
├── scripts             # Utility scripts for seeding fake history and bulk-loading products
├── frontend            # Next.js dashboard application
├── docker-compose.yml  # Orchestration for Postgres, API, and scraper services
├── alembic             # Database migrations via Alembic
└── ...
```

## API Endpoints

| Path                             | Method | Description                                         |
|----------------------------------|--------|-----------------------------------------------------|
| `/health`                        | GET    | Health check                                        |
| `/products`                      | GET    | List all products and their snapshots               |
| `/products`                      | POST   | Create a new product and perform an initial scrape   |
| `/products/{product_id}`         | GET    | Get a product and all its snapshots                 |
| `/snapshot`                      | POST   | Create a snapshot for an existing product           |
| `/products/{product_id}/latest`  | GET    | Get latest snapshots for a product                  |
| `/products/{product_id}/history` | GET    | Get snapshot history for a product (default last 7d) |
| `/products/{product_id}/best`    | GET    | Get the best price snapshot within an optional date range |

## CLI Usage

### Run a one-off scrape

```bash
python -m scraper.run_once -p "Your shopping prompt"
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
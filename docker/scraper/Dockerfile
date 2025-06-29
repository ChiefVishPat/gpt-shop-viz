FROM python:3.11-slim
# install curl and netcat-openbsd for waiting on Postgres
RUN apt-get update \
    && apt-get install -y curl netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml requirements.in requirements.txt ./
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install playwright \
    && playwright install chromium
COPY . .
CMD ["sh", "-c", \
    "echo 'Waiting for Postgres...' && \
    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do sleep 2; done && \
    echo 'Postgres is up - running scraper' && \
    python -m scraper.run_once"]
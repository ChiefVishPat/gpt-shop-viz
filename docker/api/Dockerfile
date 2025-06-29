FROM python:3.11-slim

# install netcat-openbsd so we can wait for Postgres before startup
RUN apt-get update \
    && apt-get install -y netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml requirements.in requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .

CMD ["sh", "-c", \
    "echo 'Waiting for Postgres...' && \
    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do sleep 2; done && \
    echo 'Postgres is up - starting Uvicorn' && \
    uvicorn app.main:app --host 0.0.0.0 --port 8000"]
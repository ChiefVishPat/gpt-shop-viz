FROM python:3.11-slim
RUN apt-get update && apt-get install -y curl \
    && pip install --upgrade pip \
    && pip install playwright \
    && playwright install chromium
WORKDIR /app
COPY . .
CMD ["python", "-m", "scraper.run_once"]
# gpt-shop-viz Frontend

This is the Next.js + TypeScript + Tailwind CSS frontend for the gpt-shop-viz dashboard.

## Setup

1. Copy environment variables:
   ```bash
   cp .env.local.example .env.local
   ```
2. Edit `.env.local` and set:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```
3. Install dependencies:
   ```bash
   npm install
   ```
4. Run development server:
   ```bash
   npm run dev
   ```
5. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Docker

Build and run the production image:

```bash
docker build -t gpt-shop-viz-frontend .
docker run -p 3000:3000 gpt-shop-viz-frontend
```

## Best Price Feature

On each product’s detail page (click **View** on the dashboard), you’ll find a **Best Price** section under the latest snapshot.
Select a start and/or end date and click **Fetch Best Price** to see the lowest‐price snapshot in that range.
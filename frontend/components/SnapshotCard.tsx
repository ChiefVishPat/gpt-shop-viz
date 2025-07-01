
/**
 * Renders details of a single price snapshot.
 *
 * @param snapshot SnapshotRead object containing title, price, URLs, and capture time.
 */
import React from 'react'
import { SnapshotRead } from '@/utils/api'

interface SnapshotCardProps {
  snapshot: SnapshotRead
}

export default function SnapshotCard({ snapshot }: SnapshotCardProps) {
  return (
    <div className="bg-gray-800 p-4 rounded-lg shadow">
      <h3 className="font-semibold">{snapshot.title}</h3>
      <p className="text-sm text-gray-400">
        {new Date(snapshot.captured_at).toLocaleString()}
      </p>
      <ul className="mt-2 flex flex-col gap-1">
        {snapshot.urls.map((entry) => {
          const url = typeof entry === 'string' ? entry : entry.url
          const rawPrice = typeof entry === 'string' ? snapshot.price : entry.price
          const priceNum = rawPrice != null ? Number(rawPrice) : null
          let host: string
          try {
            host = new URL(url).hostname
          } catch {
            host = url
          }

          return (
            <li key={url} className="flex items-center space-x-2 text-sm">
              <a
                href={url}
                target="_blank"
                rel="noopener noreferrer"
                className="underline"
              >
                {host}
              </a>
              <span className="text-gray-400">
                — {priceNum != null && !isNaN(priceNum) ? `$${priceNum.toFixed(2)}` : 'N/A'}
              </span>
            </li>
          )
        })}
      </ul>
    </div>
  )
}
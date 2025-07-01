import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Head from 'next/head'
import useSWR from 'swr'
import SnapshotChart from '@/components/SnapshotChart'
import SnapshotTable from '@/components/SnapshotTable'
import BestPriceForm from '@/components/BestPriceForm'
import { getBestPrice, SnapshotRead, UrlPrice } from '@/utils/api'

interface ProductDetail {
  id: number
  name: string
  snapshots: SnapshotRead[]
}

const fetcher = (url: string) => fetch(url).then((res) => res.json())
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function ProductPage() {
  const router = useRouter()
  const { id } = router.query

  // Snapshot view mode: 'realtime' shows latest only; 'history' shows full history
  const [viewMode, setViewMode] = useState<'realtime' | 'history'>('realtime')
  const [loadingSnapshots, setLoadingSnapshots] = useState(false)
  const [snapshotError, setSnapshotError] = useState<string | null>(null)
  const [latestSnapshots, setLatestSnapshots] = useState<SnapshotRead[]>([])
  const [historySnapshots, setHistorySnapshots] = useState<SnapshotRead[]>([])

  // Best price state
  const [bestPrice, setBestPrice] = useState<SnapshotRead | null>(null)
  const [bestError, setBestError] = useState<string | null>(null)
  const [bestLoading, setBestLoading] = useState(false)

  useEffect(() => {
    if (!id) return
    setSnapshotError(null)
    setLoadingSnapshots(true)
    const url =
      viewMode === 'realtime'
        ? `${API_BASE}/products/${id}/latest`
        : `${API_BASE}/products/${id}/history?days=30`
    fetch(url)
      .then((res) => {
        if (!res.ok) throw new Error(`Error ${res.status}: ${res.statusText}`)
        return res.json()
      })
      .then((data) => {
        if (viewMode === 'realtime') {
          setLatestSnapshots(data)
        } else {
          setHistorySnapshots(data)
        }
      })
      .catch((err: any) => setSnapshotError(err.message || 'Error loading snapshots'))
      .finally(() => setLoadingSnapshots(false))
  }, [id, viewMode]);

  const { data, error } = useSWR<ProductDetail>(
    id ? `${API_BASE}/products/${id}` : null,
    fetcher
  );

  if (error) return <div className="p-6">Error loading product.</div>
  if (!data) return <div className="p-6">Loading...</div>

  return (
    <>
      <Head>
        <title>{data.name}</title>
      </Head>
      <main className="p-6">
        <h1 className="text-2xl font-bold mb-4">{data.name}</h1>
        {/* Toggle Real-time vs. History */}
        <div className="flex space-x-2 mb-4">
          <button
            onClick={() => setViewMode('realtime')}
            className={`px-4 py-2 rounded ${
              viewMode === 'realtime'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-400'
            }`}
          >
            Real-time
          </button>
          <button
            onClick={() => setViewMode('history')}
            className={`px-4 py-2 rounded ${
              viewMode === 'history'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-400'
            }`}
          >
            History
          </button>
        </div>

        {/* Loading & error states */}
        {loadingSnapshots && <div>Loading {viewMode}...</div>}
        {snapshotError && <div className="text-red-400">{snapshotError}</div>}

        {/* Real-time: latest snapshots */}
        {!loadingSnapshots && !snapshotError && viewMode === 'realtime' && latestSnapshots.length > 0 && (
          <div className="mb-6">
            <h2 className="text-xl mb-2">Latest Snapshots</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {latestSnapshots.map((s) => (
                <div key={s.id} className="bg-gray-800 p-4 rounded-lg shadow">
                  <h3 className="font-semibold">{s.title}</h3>
                  <ul className="mt-2 flex flex-col gap-1">
                    {s.urls.map((entry) => {
                      const url = typeof entry === 'string' ? entry : entry.url
                      const price = typeof entry === 'string' ? s.price : entry.price
                      return (
                        <li key={url} className="flex items-center space-x-2">
                          <a
                            href={url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-400 hover:underline"
                          >
                            {url}
                          </a>
                          <span className="text-gray-400">${price}</span>
                        </li>
                      )
                    })}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Best Price Section */}
        <div className="mb-6">
          <h2 className="text-xl mb-2">Best Price</h2>
          <BestPriceForm
            onFetch={async (start, end) => {
              setBestError(null)
              setBestLoading(true)
              try {
                const snap = await getBestPrice(Number(id), start, end)
                setBestPrice(snap)
              } catch (err: any) {
                setBestError(err.message || 'Error fetching best price')
              } finally {
                setBestLoading(false)
              }
            }}
          />
          {bestLoading && <div>Loading best price…</div>}
          {bestError && <div className="text-red-400">{bestError}</div>}
          {bestPrice && (
            <div className="bg-gray-800 p-4 rounded-lg shadow mt-4">
              <p>Title: {bestPrice.title}</p>
              <p>Price: ${bestPrice.price}</p>
              <p>Date: {new Date(bestPrice.captured_at).toLocaleString()}</p>
              <ul className="mt-2 flex flex-col gap-1">
                {bestPrice.urls.map((entry) => {
                  const url = typeof entry === 'string' ? entry : entry.url
                  const price = typeof entry === 'string' ? bestPrice.price : entry.price
                  return (
                    <li key={url} className="flex items-center space-x-2">
                      <a
                        href={url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-400 hover:underline"
                      >
                        {url}
                      </a>
                      <span className="text-gray-400">${price}</span>
                    </li>
                  )
                })}
              </ul>
            </div>
          )}
        </div>

        {/* History: chart + combined snapshot cards */}
        {!loadingSnapshots && !snapshotError && viewMode === 'history' && (
          <>
            <div className="mb-6">
              <h2 className="text-xl mb-2">Price History (last 30 days)</h2>
              <SnapshotChart data={historySnapshots} />
            </div>

            <div>
              <h2 className="text-xl mb-2">Snapshot History</h2>
              <SnapshotTable data={historySnapshots} />
            </div>
          </>
        )}
      </main>
    </>
  )
}
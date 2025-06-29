import { useRouter } from 'next/router'
import Head from 'next/head'
import useSWR from 'swr'
import { useState, useEffect } from 'react'
import SnapshotChart from '@/components/SnapshotChart'
import SnapshotTable from '@/components/SnapshotTable'

interface Snapshot {
  id: number
  title: string
  price: number
  urls: string[]
  captured_at: string
}

interface ProductDetail {
  id: number
  name: string
  snapshots: Snapshot[]
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
  const [latestSnapshot, setLatestSnapshot] = useState<Snapshot | null>(null)
  const [historySnapshots, setHistorySnapshots] = useState<Snapshot[]>([])

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
          setLatestSnapshot(data)
        } else {
          setHistorySnapshots(data)
        }
      })
      .catch((err: any) => setSnapshotError(err.message || 'Error loading snapshots'))
      .finally(() => setLoadingSnapshots(false))
  }, [id, viewMode])

  const { data, error } = useSWR<ProductDetail>(
    id ? `${API_BASE}/products/${id}` : null,
    fetcher
  )

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

        {/* Real-time: single latest snapshot */}
        {!loadingSnapshots && !snapshotError && viewMode === 'realtime' && latestSnapshot && (
          <div className="mb-6">
            <h2 className="text-xl">Latest Snapshot</h2>
            <p>Title: {latestSnapshot.title}</p>
            <p>Price: ${latestSnapshot.price}</p>
            <p className="flex flex-wrap gap-2">
              Links:
              {latestSnapshot.urls.map((url) => (
                <a
                  key={url}
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-400 hover:underline"
                >
                  {url}
                </a>
              ))}
            </p>
          </div>
        )}

        {/* History: chart + table of past snapshots */}
        {!loadingSnapshots && !snapshotError && viewMode === 'history' && (
          <>
            <div className="mb-6">
              <h2 className="text-xl mb-2">Price History (last 30 days)</h2>
              <SnapshotChart data={historySnapshots} />
            </div>
            <div>
              <h2 className="text-xl mb-2">All Snapshots</h2>
              <SnapshotTable data={historySnapshots} />
            </div>
          </>
        )}
      </main>
    </>
  )
}
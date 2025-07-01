import useSWR from 'swr'
import { useState } from 'react'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface ProductCreate {
  name: string
  prompt: string
}

export interface UrlPrice {
  url: string
  price: number | null
}

export interface SnapshotRead {
  id: number
  product_id: number
  title: string
  price: number | null
  /**
   * Snapshot URLs. Backend returns a list of string URLs,
   * but best-price endpoint wraps them as UrlPrice objects.
   */
  urls: Array<string | UrlPrice>
  captured_at: string
}

export interface ProductRead {
  id: number
  name: string
  prompt?: string
  created_at: string
  snapshots: SnapshotRead[]
}

export const fetcher = (url: string) =>
  fetch(url).then((res) => {
    if (!res.ok) throw new Error(`Fetch error (${res.status}): ${res.statusText}`)
    return res.json()
  })

export function useProducts() {
  return useSWR<ProductRead[]>(`${API_BASE}/products`, fetcher)
}

export function useProduct(id?: number | string) {
  return useSWR<ProductRead>(
    id ? `${API_BASE}/products/${id}` : null,
    fetcher
  )
}

export function useCreateProduct() {
  const [isLoading, setIsLoading] = useState(false)

  async function mutateAsync(data: ProductCreate): Promise<ProductRead> {
    setIsLoading(true)
    const res = await fetch(`${API_BASE}/products`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    if (!res.ok) {
      const message = await res.text()
      setIsLoading(false)
      throw new Error(message || `Error creating product (${res.status})`)
    }
    const json = (await res.json()) as ProductRead
    setIsLoading(false)
    return json
  }

  return { mutateAsync, isLoading }
}

/**
 * Fetch the lowest-price snapshot for a product within an optional date range.
 * Dates should be ISO strings (YYYY-MM-DD).
 */
interface RawSnapshot {
  id: number
  product_id: number
  title: string
  price: number | null
  urls: string[]
  captured_at: string
}

/**
 * Fetch the lowest-price snapshot for a product between start and end dates.
 */
export async function getBestPrice(
  productId: number,
  start?: string,
  end?: string
): Promise<SnapshotRead> {
  const params = new URLSearchParams()
  if (start) params.append('start', start)
  if (end) params.append('end', end)
  const res = await fetch(
    `${API_BASE}/products/${productId}/best${params.toString() ? '?' + params.toString() : ''}`
  )
  if (!res.ok) {
    throw new Error(`Error fetching best price: ${res.statusText}`)
  }
  const raw = (await res.json()) as RawSnapshot
  return {
    id: raw.id,
    product_id: raw.product_id,
    title: raw.title,
    price: raw.price,
    urls: raw.urls.map((url) => ({ url, price: raw.price ?? 0 })),
    captured_at: raw.captured_at,
  }
}
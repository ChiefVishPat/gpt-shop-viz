/**
 * API client and React hooks for gpt-shop-viz frontend.
 *
 * Defines TypeScript interfaces for Product and Snapshot schemas,
 * SWR hooks for fetching data, and helper functions for creating products
 * and fetching best price snapshots.
 */
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

/**
 * Generic fetcher function for SWR that throws on HTTP errors.
 *
 * @param url The resource URL to fetch.
 * @returns Parsed JSON response.
 * @throws Error if response status is not OK.
 */
export const fetcher = (url: string) =>
  fetch(url).then((res) => {
    if (!res.ok) throw new Error(`Fetch error (${res.status}): ${res.statusText}`)
    return res.json()
  })

/**
 * SWR hook to fetch all products along with their snapshots.
 *
 * @returns SWR response containing ProductRead[] or error/loading state.
 */
export function useProducts() {
  return useSWR<ProductRead[]>(`${API_BASE}/products`, fetcher)
}

/**
 * SWR hook to fetch a single product by its ID.
 *
 * @param id Product ID or undefined. Hook is disabled if id is not set.
 * @returns SWR response containing ProductRead or error/loading state.
 */
export function useProduct(id?: number | string) {
  return useSWR<ProductRead>(
    id ? `${API_BASE}/products/${id}` : null,
    fetcher
  )
}

/**
 * Hook to create a new product via the API.
 *
 * @returns An object with mutateAsync function and isLoading flag.
 */
export function useCreateProduct() {
  const [isLoading, setIsLoading] = useState(false)

  /**
   * Sends a POST request to create a product and returns the created ProductRead.
   *
   * @param data ProductCreate payload containing name and prompt.
   * @returns The created ProductRead object.
   */
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
import useSWR from 'swr'
import { useState } from 'react'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface ProductCreate {
  name: string
  prompt: string
}

export interface SnapshotRead {
  id: number
  product_id: number
  title: string
  price: number | null
  urls: string[]
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
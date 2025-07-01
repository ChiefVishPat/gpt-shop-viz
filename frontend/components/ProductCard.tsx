
/**
 * Displays a product card with name and creation date, linking to its detail page.
 *
 * @param product Object containing id, name, and created_at timestamp.
 */
import Link from 'next/link'
import React from 'react'

interface Product {
  id: number
  name: string
  created_at: string
}

export default function ProductCard({ product }: { product: Product }) {
  return (
    <div className="bg-gray-800 p-4 rounded-lg shadow hover:bg-gray-700 transition">
      <h3 className="text-lg font-semibold">{product.name}</h3>
      <p className="text-sm text-gray-400 mb-2">
        Created at: {new Date(product.created_at).toLocaleString()}
      </p>
      <Link href={`/products/${product.id}`} className="text-blue-400 hover:underline">
        View
      </Link>
    </div>
  )
}
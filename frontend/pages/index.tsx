/**
 * Home page showing list of products and a form to add new products.
 */
import Head from 'next/head'
import useSWR from 'swr'
import ProductCard from '@/components/ProductCard'
import NewProductForm from '@/components/NewProductForm'

interface Product {
  id: number
  name: string
  created_at: string
}

const fetcher = (url: string) => fetch(url).then((res) => res.json())

export default function Home() {
  const { data, error } = useSWR<Product[]>(
    `${process.env.NEXT_PUBLIC_API_URL}/products`,
    fetcher
  )

  if (error) return <div className="p-6">Error loading products.</div>
  if (!data) return <div className="p-6">Loading...</div>

  return (
    <>
      <Head>
        <title>Products</title>
      </Head>
      <main className="p-6">
        <div className="bg-gray-800 p-4 rounded-lg shadow">
          <NewProductForm />
        </div>
        <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 mt-6">
          {data.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      </main>
    </>
  )
}
import Link from 'next/link'
import React from 'react'

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen bg-gray-900 text-white">
      <aside className="w-64 bg-gray-800 p-4 flex flex-col">
        <h2 className="text-2xl font-bold mb-8">gpt-shop-viz</h2>
        <nav className="flex flex-col space-y-2">
          <Link href="/">
            <span className="hover:bg-gray-700 p-2 rounded cursor-pointer">Products</span>
          </Link>
        </nav>
      </aside>
      <div className="flex flex-col flex-1 overflow-auto">
        <header className="bg-gray-800 p-4 flex justify-between items-center">
          <div>Dashboard</div>
        </header>
        <section className="flex-1 overflow-auto p-6">{children}</section>
      </div>
    </div>
  )
}
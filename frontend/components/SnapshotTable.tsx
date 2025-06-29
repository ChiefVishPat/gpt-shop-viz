import React from 'react'

interface Snapshot {
  id: number
  title: string
  price: number
  urls: string[]
  captured_at: string
}

export default function SnapshotTable({ data }: { data: Snapshot[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full bg-gray-800">
        <thead>
          <tr>
            <th className="px-4 py-2 text-left text-sm text-gray-400">Date</th>
            <th className="px-4 py-2 text-left text-sm text-gray-400">Title</th>
            <th className="px-4 py-2 text-left text-sm text-gray-400">Price</th>
            <th className="px-4 py-2 text-left text-sm text-gray-400">Links</th>
          </tr>
        </thead>
        <tbody>
          {data.map((s) => (
            <tr key={s.id} className="border-t border-gray-700">
              <td className="px-4 py-2 text-sm">
                {new Date(s.captured_at).toLocaleString()}
              </td>
              <td className="px-4 py-2 text-sm">{s.title}</td>
              <td className="px-4 py-2 text-sm">${s.price}</td>
              <td className="px-4 py-2 text-sm flex flex-wrap gap-2">
                {s.urls.map((url) => (
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
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
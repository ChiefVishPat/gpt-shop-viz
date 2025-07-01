import React, { useState } from 'react'

interface BestPriceFormProps {
  onFetch: (start?: string, end?: string) => void
}

export default function BestPriceForm({ onFetch }: BestPriceFormProps) {
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')

  return (
    <div className="flex flex-col sm:flex-row gap-2 items-center">
      <input
        type="date"
        value={startDate}
        onChange={(e) => setStartDate(e.target.value)}
        className="bg-gray-800 text-white border border-gray-700 rounded px-4 py-2"
      />
      <input
        type="date"
        value={endDate}
        onChange={(e) => setEndDate(e.target.value)}
        className="bg-gray-800 text-white border border-gray-700 rounded px-4 py-2"
      />
      <button
        onClick={() => onFetch(startDate || undefined, endDate || undefined)}
        className="bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded px-4 py-2"
      >
        Fetch Best Price
      </button>
    </div>
  )
}
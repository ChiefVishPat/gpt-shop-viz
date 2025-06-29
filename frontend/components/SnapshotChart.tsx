import React from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'

interface Snapshot {
  id: number
  title: string
  price: number
  captured_at: string
}

export default function SnapshotChart({ data }: { data: Snapshot[] }) {
  const chartData = data
    .slice()
    .reverse()
    .map((s) => ({
      date: new Date(s.captured_at).toLocaleString(),
      price: s.price,
    }))
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={chartData}>
        <XAxis dataKey="date" tick={{ fill: '#ccc' }} />
        <YAxis tick={{ fill: '#ccc' }} />
        <Tooltip
          formatter={(value: any) => [`$${value}`, 'Price']}
          labelStyle={{ color: '#fff' }}
          contentStyle={{ backgroundColor: '#333', borderColor: '#444' }}
        />
        <Line
          type="monotone"
          dataKey="price"
          stroke="#8884d8"
          strokeWidth={2}
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
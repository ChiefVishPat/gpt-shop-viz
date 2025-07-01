import React from 'react'
import { SnapshotRead } from '@/utils/api'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'

export default function SnapshotChart({ data }: { data: SnapshotRead[] }) {
  // Prepare chart data in chronological order (oldest → newest)
  const chartData = data
    .slice()
    .map((s) => ({
      date: new Date(s.captured_at).toISOString().slice(0, 10),
      price: s.price ?? 0,
    }))

  const prices = chartData.map((d) => d.price)
  const dataMin = prices.length > 0 ? Math.min(...prices) : 0
  const dataMax = prices.length > 0 ? Math.max(...prices) : 0
  const padding = (dataMax - dataMin) * 0.1 || 5

  return (
    <div style={{ height: 300, width: '100%' }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={chartData}
          margin={{ top: 20, right: 20, left: 20, bottom: 20 }}
        >
          <XAxis
            dataKey="date"
            type="category"
            tick={{ fill: '#ccc' }}
            interval={0}
            angle={-45}
            textAnchor="end"
          />
          <YAxis
            type="number"
            dataKey="price"
            tick={{ fill: '#ccc' }}
            tickFormatter={(v) => `$${v}`}
            domain={[dataMin - padding, dataMax + padding]}
          />
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
            dot={{ r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
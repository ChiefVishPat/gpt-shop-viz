import React from 'react'
import { SnapshotRead } from '@/utils/api'
import SnapshotCard from './SnapshotCard'

export default function SnapshotTable({ data }: { data: SnapshotRead[] }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {data.map((s) => (
        <SnapshotCard key={s.id} snapshot={s} />
      ))}
    </div>
  )
}
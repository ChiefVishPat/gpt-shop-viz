
/**
 * Toggle buttons to switch between real-time and history views.
 *
 * @param viewMode Current view mode ('realtime' or 'history').
 * @param onChange Callback to set the view mode.
 */
import React from 'react'

interface RealtimeToggleProps {
  viewMode: 'realtime' | 'history'
  onChange: (mode: 'realtime' | 'history') => void
}

export default function RealtimeToggle({ viewMode, onChange }: RealtimeToggleProps) {
  return (
    <div className="flex space-x-2 mb-4">
      <button
        onClick={() => onChange('realtime')}
        className={`px-4 py-2 rounded ${
          viewMode === 'realtime' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-400'
        }`}
      >
        Real-time
      </button>
      <button
        onClick={() => onChange('history')}
        className={`px-4 py-2 rounded ${
          viewMode === 'history' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-400'
        }`}
      >
        History
      </button>
    </div>
  )
}
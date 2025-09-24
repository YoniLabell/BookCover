'use client'

import { useEffect, useMemo, useState } from 'react'
import { requestSpine } from '@/lib/api'

interface CoverDesignerProps {
  trimWidth: number
  trimHeight: number
  bleed: number
  paperType: string
  onSpineChange?: (value: number) => void
}

export function CoverDesigner({ trimWidth, trimHeight, bleed, paperType, onSpineChange }: CoverDesignerProps) {
  const [pages, setPages] = useState(200)
  const [spine, setSpine] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let mounted = true
    setLoading(true)
    requestSpine(pages, paperType)
      .then((value) => {
        if (!mounted) return
        setSpine(value)
        onSpineChange?.(value)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
    return () => {
      mounted = false
    }
  }, [pages, paperType, onSpineChange])

  const canvasSize = useMemo(() => {
    const width = trimWidth * 2 + spine + bleed * 2
    const height = trimHeight + bleed * 2
    return { width, height }
  }, [bleed, spine, trimHeight, trimWidth])

  return (
    <div className="rounded border border-slate-800 bg-slate-900/60 p-4">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div className="flex-1 space-y-3 text-sm">
          <h3 className="text-sm font-semibold text-white">Cover template</h3>
          <label className="block text-xs uppercase tracking-wide text-slate-400">
            Interior pages
            <input
              type="number"
              min={2}
              step={2}
              value={pages}
              onChange={(event) => setPages(parseInt(event.target.value, 10) || 2)}
              className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white"
            />
          </label>
          <p className="text-xs text-slate-400">Calculated spine: {spine.toFixed(2)} mm</p>
          {loading && <p className="text-xs text-slate-400">Calculating spine…</p>}
          {error && <p className="text-xs text-red-400">{error}</p>}
        </div>
        <div className="mt-6 md:mt-0 md:w-2/3">
          <svg viewBox={`0 0 ${canvasSize.width} ${canvasSize.height}`} className="h-48 w-full">
            <rect x={0} y={0} width={canvasSize.width} height={canvasSize.height} fill="#0f172a" stroke="#1e293b" />
            <rect
              x={bleed}
              y={bleed}
              width={trimWidth}
              height={trimHeight}
              fill="none"
              stroke="#38bdf8"
              strokeDasharray="6 4"
            />
            <rect
              x={bleed + trimWidth + spine}
              y={bleed}
              width={trimWidth}
              height={trimHeight}
              fill="none"
              stroke="#38bdf8"
              strokeDasharray="6 4"
            />
            <rect
              x={bleed + trimWidth}
              y={0}
              width={spine}
              height={canvasSize.height}
              fill="#38bdf821"
            />
          </svg>
        </div>
      </div>
    </div>
  )
}

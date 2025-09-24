'use client'

import { useEffect, useRef } from 'react'

interface PdfViewerProps {
  fileUrl: string | null
}

export function PdfViewer({ fileUrl }: PdfViewerProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null)

  useEffect(() => {
    let cancelled = false
    async function render() {
      if (!fileUrl || !canvasRef.current) return
      const [{ GlobalWorkerOptions, getDocument }, worker] = await Promise.all([
        import('pdfjs-dist/build/pdf'),
        import('pdfjs-dist/build/pdf.worker.min.js'),
      ])
      GlobalWorkerOptions.workerSrc = (worker as { default: string }).default
      const pdf = await getDocument(fileUrl).promise
      const page = await pdf.getPage(1)
      const viewport = page.getViewport({ scale: 0.8 })
      const canvas = canvasRef.current
      const context = canvas.getContext('2d')
      if (!context) return
      canvas.height = viewport.height
      canvas.width = viewport.width
      await page.render({ canvasContext: context, viewport }).promise
      if (!cancelled) {
        context.strokeStyle = 'rgba(56,189,248,0.6)'
        context.lineWidth = 2
        context.strokeRect(10, 10, canvas.width - 20, canvas.height - 20)
      }
    }
    void render()
    return () => {
      cancelled = true
    }
  }, [fileUrl])

  if (!fileUrl) {
    return <div className="rounded border border-slate-800 bg-slate-900/60 p-6 text-sm text-slate-400">No PDF selected.</div>
  }

  return (
    <div className="overflow-hidden rounded border border-slate-800 bg-black/40">
      <canvas ref={canvasRef} className="mx-auto block" />
    </div>
  )
}

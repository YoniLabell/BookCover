'use client'

import { useCallback, useRef, useState } from 'react'
import type { PresignResponse } from '@/lib/api'
import { presignUpload } from '@/lib/api'

interface UploadAreaProps {
  projectId: string
  kind: 'content' | 'cover'
  onUploaded: (key: string) => void
}

export function UploadArea({ projectId, kind, onUploaded }: UploadAreaProps) {
  const inputRef = useRef<HTMLInputElement | null>(null)
  const [progress, setProgress] = useState(0)
  const [status, setStatus] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)

  const handleUpload = useCallback(
    async (file: File) => {
      setUploading(true)
      setStatus(null)
      try {
        const presign = await presignUpload({
          project_id: projectId,
          kind,
          filename: file.name,
          content_type: file.type || 'application/pdf',
          content_length: file.size,
        })
        await uploadToS3(file, presign, setProgress)
        setStatus('Uploaded successfully')
        onUploaded(presign.key)
      } catch (err) {
        setStatus((err as Error).message)
      } finally {
        setUploading(false)
        setTimeout(() => setProgress(0), 500)
      }
    },
    [kind, onUploaded, projectId],
  )

  const onFileChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0]
      if (file) {
        void handleUpload(file)
      }
    },
    [handleUpload],
  )

  return (
    <div className="rounded border border-dashed border-slate-700 bg-slate-900/40 p-4">
      <div className="flex flex-col gap-2 text-sm">
        <p className="font-medium text-white">Upload {kind === 'content' ? 'content' : 'cover'} PDF</p>
        <p className="text-xs text-slate-400">Pre-signed S3 upload with antivirus scanning.</p>
      </div>
      <div className="mt-4 flex items-center gap-3">
        <button
          className="rounded bg-slate-800 px-3 py-2 text-sm font-semibold text-white hover:bg-slate-700"
          onClick={() => inputRef.current?.click()}
          disabled={uploading}
        >
          Choose file
        </button>
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf"
          className="hidden"
          onChange={onFileChange}
        />
        {uploading && (
          <div className="flex-1">
            <div className="h-2 rounded-full bg-slate-800">
              <div className="h-2 rounded-full bg-sky-500 transition-all" style={{ width: `${progress}%` }} />
            </div>
          </div>
        )}
        {status && <span className="text-xs text-slate-300">{status}</span>}
      </div>
    </div>
  )
}

async function uploadToS3(file: File, presign: PresignResponse, onProgress: (value: number) => void) {
  const formData = new FormData()
  Object.entries(presign.fields).forEach(([key, value]) => {
    formData.append(key, value)
  })
  formData.append('file', file)

  await new Promise<void>((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    xhr.open('POST', presign.url, true)
    xhr.upload.onprogress = (event) => {
      if (!event.lengthComputable) return
      onProgress(Math.round((event.loaded / event.total) * 100))
    }
    xhr.onerror = () => reject(new Error('Upload failed'))
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve()
      } else {
        reject(new Error('Upload failed'))
      }
    }
    xhr.send(formData)
  })
}

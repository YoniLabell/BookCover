'use client'

import { useEffect, useState } from 'react'
import {
  Project,
  ValidationResult,
  fetchProject,
  validateContent,
  validateCover,
} from '@/lib/api'
import { UploadArea } from '@/components/UploadArea'
import { PdfViewer } from '@/components/PdfViewer'
import { ValidationReport } from '@/components/ValidationReport'
import { CoverDesigner } from '@/components/CoverDesigner'

interface ProjectPageProps {
  params: { id: string }
}

export default function ProjectPage({ params }: ProjectPageProps) {
  const projectId = params.id
  const [project, setProject] = useState<Project | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [contentKey, setContentKey] = useState<string | null>(null)
  const [coverKey, setCoverKey] = useState<string | null>(null)
  const [contentPath, setContentPath] = useState('')
  const [coverPath, setCoverPath] = useState('')
  const [contentValidation, setContentValidation] = useState<ValidationResult | null>(null)
  const [coverValidation, setCoverValidation] = useState<ValidationResult | null>(null)
  const [spine, setSpine] = useState(0)

  useEffect(() => {
    setLoading(true)
    fetchProject(projectId)
      .then((data) => {
        setProject(data)
        setError(null)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [projectId])

  const runContentValidation = async () => {
    if (!project || !contentPath) return
    try {
      const result = await validateContent({
        pdf_path: contentPath,
        trim: [project.size.width_mm, project.size.height_mm],
        bleed_mm: project.bleed_mm,
      })
      setContentValidation(result)
    } catch (err) {
      setError((err as Error).message)
    }
  }

  const runCoverValidation = async () => {
    if (!project || !coverPath) return
    try {
      const result = await validateCover({
        pdf_path: coverPath,
        trim: [project.size.width_mm, project.size.height_mm],
        bleed_mm: project.bleed_mm,
        spine_mm: spine,
      })
      setCoverValidation(result)
    } catch (err) {
      setError((err as Error).message)
    }
  }

  if (loading) {
    return <p className="text-sm text-slate-400">Loading project…</p>
  }
  if (error) {
    return <p className="text-sm text-red-400">{error}</p>
  }
  if (!project) {
    return <p className="text-sm text-slate-400">Project not found.</p>
  }

  return (
    <div className="space-y-10">
      <section className="rounded border border-slate-800 bg-slate-900/60 p-6 shadow">
        <div className="flex flex-col gap-6 md:flex-row md:items-start md:justify-between">
          <div className="flex-1 space-y-4">
            <h2 className="text-xl font-semibold text-white">{project.name}</h2>
            <p className="text-sm text-slate-400">
              Trim {project.size.width_mm} × {project.size.height_mm} mm · Bleed {project.bleed_mm} mm · {project.paper_type}
            </p>
            <UploadArea projectId={projectId} kind="content" onUploaded={setContentKey} />
            <UploadArea projectId={projectId} kind="cover" onUploaded={setCoverKey} />
            <div className="space-y-2 text-sm">
              <label className="block text-xs uppercase tracking-wide text-slate-400">
                Content file path
                <input
                  value={contentPath}
                  onChange={(event) => setContentPath(event.target.value)}
                  placeholder="/data/bookready/<file>.pdf"
                  className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white"
                />
              </label>
              <button
                onClick={() => void runContentValidation()}
                className="rounded bg-sky-500 px-3 py-2 text-sm font-semibold text-white hover:bg-sky-400"
              >
                Validate content
              </button>
              {contentKey && <p className="text-xs text-slate-500">Stored object key: {contentKey}</p>}
            </div>
            <div className="space-y-2 text-sm">
              <label className="block text-xs uppercase tracking-wide text-slate-400">
                Cover file path
                <input
                  value={coverPath}
                  onChange={(event) => setCoverPath(event.target.value)}
                  placeholder="/data/bookready/<cover>.pdf"
                  className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white"
                />
              </label>
              <button
                onClick={() => void runCoverValidation()}
                className="rounded bg-sky-500 px-3 py-2 text-sm font-semibold text-white hover:bg-sky-400"
              >
                Validate cover
              </button>
              {coverKey && <p className="text-xs text-slate-500">Stored object key: {coverKey}</p>}
            </div>
          </div>
          <div className="space-y-4 md:w-1/3">
            <PdfViewer fileUrl={null} />
            <ValidationReport result={contentValidation} title="Content validation" />
            <ValidationReport result={coverValidation} title="Cover validation" />
          </div>
        </div>
      </section>
      <CoverDesigner
        trimWidth={project.size.width_mm}
        trimHeight={project.size.height_mm}
        bleed={project.bleed_mm}
        paperType={project.paper_type}
        onSpineChange={setSpine}
      />
    </div>
  )
}

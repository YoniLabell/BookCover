'use client'

import Link from 'next/link'
import { useEffect, useMemo, useState } from 'react'
import {
  Project,
  ProjectCreate,
  createProject,
  fetchProjects,
  getStoredToken,
  login,
} from '@/lib/api'

interface ProjectFormState extends ProjectCreate {
  pages: number
}

const DEFAULT_FORM: ProjectFormState = {
  name: 'Untitled Manuscript',
  size: { width_mm: 148, height_mm: 210 },
  bleed_mm: 3.2,
  paper_type: '80gsm',
  color_space: 'CMYK',
  pages: 200,
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [loggedIn, setLoggedIn] = useState<boolean>(!!getStoredToken())
  const [form, setForm] = useState<ProjectFormState>(DEFAULT_FORM)
  const [auth, setAuth] = useState({ username: 'admin', password: 'admin' })
  const [authError, setAuthError] = useState<string | null>(null)

  useEffect(() => {
    if (!loggedIn) return
    setLoading(true)
    fetchProjects()
      .then(setProjects)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [loggedIn])

  const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    try {
      await login(auth.username, auth.password)
      setLoggedIn(true)
      setAuthError(null)
    } catch (err) {
      setAuthError((err as Error).message)
    }
  }

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const payload: ProjectCreate = {
        name: form.name,
        size: form.size,
        bleed_mm: form.bleed_mm,
        paper_type: form.paper_type,
        color_space: form.color_space,
      }
      const project = await createProject(payload)
      setProjects((prev) => [...prev, project])
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setLoading(false)
    }
  }

  const projectList = useMemo(() => {
    if (projects.length === 0) {
      return <p className="text-sm text-slate-400">No projects yet. Create one to begin.</p>
    }
    return (
      <ul className="space-y-3">
        {projects.map((project) => (
          <li
            key={project.id}
            className="rounded border border-slate-800 bg-slate-900/60 p-4 shadow-sm shadow-slate-900/30"
          >
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-white">{project.name}</h3>
                <p className="text-xs text-slate-400">
                  {project.size.width_mm} × {project.size.height_mm} mm · Bleed {project.bleed_mm} mm ·{' '}
                  {project.paper_type}
                </p>
              </div>
              <Link
                href={`/project/${project.id}`}
                className="rounded bg-sky-500 px-3 py-1 text-sm font-medium text-white hover:bg-sky-400"
              >
                Open
              </Link>
            </div>
          </li>
        ))}
      </ul>
    )
  }, [projects])

  if (!loggedIn) {
    return (
      <div className="mx-auto max-w-md rounded border border-slate-800 bg-slate-900/60 p-6 shadow">
        <h2 className="text-lg font-semibold text-white">Sign in</h2>
        <p className="mb-4 text-sm text-slate-400">Use the default admin/admin credentials for local development.</p>
        <form className="space-y-4" onSubmit={handleLogin}>
          <div>
            <label className="text-xs uppercase tracking-wide text-slate-400">Username</label>
            <input
              value={auth.username}
              onChange={(event) => setAuth({ ...auth, username: event.target.value })}
              className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white"
              required
            />
          </div>
          <div>
            <label className="text-xs uppercase tracking-wide text-slate-400">Password</label>
            <input
              type="password"
              value={auth.password}
              onChange={(event) => setAuth({ ...auth, password: event.target.value })}
              className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white"
              required
            />
          </div>
          {authError && <p className="text-sm text-red-400">{authError}</p>}
          <button
            type="submit"
            className="w-full rounded bg-sky-500 py-2 text-sm font-semibold text-white hover:bg-sky-400"
          >
            Sign in
          </button>
        </form>
      </div>
    )
  }

  return (
    <div className="space-y-10">
      <section className="rounded border border-slate-800 bg-slate-900/60 p-6 shadow">
        <h2 className="text-lg font-semibold text-white">New project</h2>
        <p className="text-sm text-slate-400">Define trim size, bleed, and paper stock.</p>
        <form className="mt-4 grid gap-4 md:grid-cols-2" onSubmit={handleSubmit}>
          <div className="md:col-span-2">
            <label className="text-xs uppercase tracking-wide text-slate-400">Project name</label>
            <input
              className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white"
              value={form.name}
              onChange={(event) => setForm({ ...form, name: event.target.value })}
              required
            />
          </div>
          <div>
            <label className="text-xs uppercase tracking-wide text-slate-400">Trim width (mm)</label>
            <input
              type="number"
              className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white"
              value={form.size.width_mm}
              onChange={(event) =>
                setForm({ ...form, size: { ...form.size, width_mm: parseFloat(event.target.value) } })
              }
              required
            />
          </div>
          <div>
            <label className="text-xs uppercase tracking-wide text-slate-400">Trim height (mm)</label>
            <input
              type="number"
              className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white"
              value={form.size.height_mm}
              onChange={(event) =>
                setForm({ ...form, size: { ...form.size, height_mm: parseFloat(event.target.value) } })
              }
              required
            />
          </div>
          <div>
            <label className="text-xs uppercase tracking-wide text-slate-400">Bleed (mm)</label>
            <input
              type="number"
              step="0.1"
              className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white"
              value={form.bleed_mm}
              onChange={(event) => setForm({ ...form, bleed_mm: parseFloat(event.target.value) })}
            />
          </div>
          <div>
            <label className="text-xs uppercase tracking-wide text-slate-400">Paper stock</label>
            <input
              className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white"
              value={form.paper_type}
              onChange={(event) => setForm({ ...form, paper_type: event.target.value })}
            />
          </div>
          <div>
            <label className="text-xs uppercase tracking-wide text-slate-400">Colour space</label>
            <input
              className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white"
              value={form.color_space}
              onChange={(event) => setForm({ ...form, color_space: event.target.value })}
            />
          </div>
          <div className="md:col-span-2">
            <button
              type="submit"
              className="rounded bg-sky-500 px-4 py-2 text-sm font-semibold text-white hover:bg-sky-400"
              disabled={loading}
            >
              Create project
            </button>
            {error && <span className="ml-3 text-sm text-red-400">{error}</span>}
          </div>
        </form>
      </section>
      <section>
        <h2 className="text-lg font-semibold text-white">Projects</h2>
        {loading ? <p className="text-sm text-slate-400">Loading…</p> : projectList}
      </section>
    </div>
  )
}

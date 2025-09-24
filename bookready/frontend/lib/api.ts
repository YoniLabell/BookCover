'use client'

export type Token = string

export interface ProjectSize {
  width_mm: number
  height_mm: number
}

export interface Project {
  id: string
  name: string
  size: ProjectSize
  bleed_mm: number
  paper_type: string
  color_space: string
  created_at: string
  updated_at: string
  content_key?: string | null
  cover_key?: string | null
}

export interface ProjectCreate {
  name: string
  size: ProjectSize
  bleed_mm: number
  paper_type: string
  color_space: string
}

export interface ValidationCheck {
  id: string
  ok: boolean
  details: string
}

export interface ValidationResult {
  status: 'pass' | 'warn' | 'fail'
  checks: ValidationCheck[]
  metrics: Record<string, number>
}

const TOKEN_STORAGE_KEY = 'bookready-token'
const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8080'

function getToken(): Token | null {
  if (typeof window === 'undefined') {
    return null
  }
  return window.localStorage.getItem(TOKEN_STORAGE_KEY)
}

function setToken(token: Token) {
  if (typeof window === 'undefined') return
  window.localStorage.setItem(TOKEN_STORAGE_KEY, token)
}

async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> | undefined),
  }
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  })
  if (!res.ok) {
    const error = await res.json().catch(() => ({}))
    throw new Error(error.detail ?? 'Request failed')
  }
  if (res.status === 204) {
    return {} as T
  }
  return (await res.json()) as T
}

export async function login(username: string, password: string): Promise<void> {
  const form = new URLSearchParams()
  form.append('username', username)
  form.append('password', password)
  const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
    method: 'POST',
    body: form,
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  if (!res.ok) {
    throw new Error('Invalid credentials')
  }
  const data = (await res.json()) as { access_token: string }
  setToken(data.access_token)
}

export async function fetchProjects(): Promise<Project[]> {
  return apiFetch<Project[]>(`/api/v1/projects/`)
}

export async function createProject(project: ProjectCreate): Promise<Project> {
  return apiFetch<Project>(`/api/v1/projects/`, {
    method: 'POST',
    body: JSON.stringify(project),
  })
}

export async function fetchProject(id: string): Promise<Project> {
  return apiFetch<Project>(`/api/v1/projects/${id}`)
}

export function getStoredToken(): Token | null {
  return getToken()
}

export async function requestSpine(pages: number, paperType: string): Promise<number> {
  const data = await apiFetch<{ spine_mm: number }>(`/api/v1/spine/calc`, {
    method: 'POST',
    body: JSON.stringify({ pages, paper_type: paperType }),
  })
  return data.spine_mm
}

export interface PresignPayload {
  project_id: string
  kind: 'content' | 'cover'
  filename: string
  content_type: string
  content_length: number
}

export interface PresignResponse {
  url: string
  fields: Record<string, string>
  key: string
}

export async function presignUpload(payload: PresignPayload): Promise<PresignResponse> {
  return apiFetch(`/api/v1/uploads/presign`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function validateContent(payload: {
  pdf_path: string
  trim: [number, number]
  bleed_mm: number
}): Promise<ValidationResult> {
  return apiFetch(`/api/v1/validate/content`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function validateCover(payload: {
  pdf_path: string
  trim: [number, number]
  bleed_mm: number
  spine_mm: number
}): Promise<ValidationResult> {
  return apiFetch(`/api/v1/validate/cover`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

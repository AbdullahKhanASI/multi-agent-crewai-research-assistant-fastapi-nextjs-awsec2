export type Candidate = {
  url: string
  title: string
  publisher?: string
  date?: string
  score?: number
}

export type Evidence = {
  url: string
  title?: string
  quote: string
  selector?: string | null
  checksum?: string
  publisher?: string
}

export type Synthesis = {
  run_id: string
  sections: { heading: string; content: string | any }[]
  quality_metrics?: Record<string, any>
}

const BASE = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
const API = `${BASE}/api/v1`

async function post<T>(path: string, body: any): Promise<T> {
  const r = await fetch(`${API}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!r.ok) throw new Error(`${path} failed: ${r.status}`)
  return r.json()
}

export async function apiSearch(topic: string) {
  return post<{ optimized_queries: string[]; candidates: Candidate[] }>('/research/search', { topic })
}

export async function apiGather(sources: Candidate[], runId?: string) {
  return post<{ run_id: string; evidence: Evidence[]; evidence_count: number }>('/research/gather', {
    run_id: runId,
    sources,
  })
}

export async function apiSynthesize(runId: string, evidence: Evidence[]) {
  return post<Synthesis>('/research/synthesize', { run_id: runId, evidence })
}

export async function apiTitle(runId: string) {
  return post<{ run_id: string; title: string; abstract: string }>('/research/title', { run_id: runId })
}

export async function apiReview(runId: string) {
  return post<{ run_id: string; issues: { message: string; severity: string }[] }>('/research/review', {
    run_id: runId,
  })
}

export async function apiBundleZip(report: any): Promise<Blob> {
  const BASE = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
  const r = await fetch(`${BASE}/api/v1/runs/bundle`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(report),
  })
  if (!r.ok) throw new Error(`bundle failed: ${r.status}`)
  return r.blob()
}

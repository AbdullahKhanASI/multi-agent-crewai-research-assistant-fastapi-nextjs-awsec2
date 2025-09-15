"use client"

import { useState } from 'react'
import { apiSearch, apiGather, apiSynthesize, apiTitle, apiReview, apiBundleZip, type Candidate, type Evidence } from '@/lib/api'
import { useSSE } from '@/hooks/useSSE'
import SectionCard from '@/components/SectionCard'
import LogPanel from '@/components/LogPanel'

export default function Home() {
  const [topic, setTopic] = useState('Flow State for Productivity')
  const [loading, setLoading] = useState(false)
  const [log, setLog] = useState<string[]>([])
  const [candidates, setCandidates] = useState<Candidate[]>([])
  const [evidence, setEvidence] = useState<Evidence[]>([])
  const [synthesis, setSynthesis] = useState<any>(null)
  const [sseUrl, setSseUrl] = useState<string | undefined>(undefined)
  const { progress: sseProgress, result: sseResult } = useSSE(sseUrl)
  const [runId, setRunId] = useState<string | null>(null)
  const [queries, setQueries] = useState<string[]>([])
  const [titleData, setTitleData] = useState<{ title: string; abstract: string } | null>(null)
  const [reviewIssues, setReviewIssues] = useState<{ message: string; severity: string }[]>([])

  const append = (line: string) => setLog((l) => [...l, line])

  async function run() {
    setLoading(true)
    setLog([])
    setCandidates([])
    setEvidence([])
    setSynthesis(null)
    try {
      append('Searching...')
      const s = await apiSearch(topic)
      setCandidates(s.candidates)
      setQueries(s.optimized_queries || [])
      append(`Found ${s.candidates.length} candidates`)

      append('Gathering evidence...')
      const g = await apiGather(s.candidates)
      setRunId(g.run_id)
      setEvidence(g.evidence)
      append(`Extracted ${g.evidence_count} evidence items`)

      append('Synthesizing...')
      const syn = await apiSynthesize(g.run_id, g.evidence)
      setSynthesis(syn)
      append('Generating title...')
      const t = await apiTitle(g.run_id)
      setTitleData({ title: t.title, abstract: t.abstract })
      append(`Title: ${t.title}`)

      append('Reviewing...')
      const r = await apiReview(g.run_id)
      setReviewIssues(r.issues)
      append(`Review issues: ${r.issues.length}`)
    } catch (e: any) {
      append(`Error: ${e?.message || String(e)}`)
    } finally {
      setLoading(false)
    }
  }

  async function stream() {
    setSynthesis(null)
    setSseUrl(undefined)
    setLog([])
    try {
      // Ensure we have a run by doing search+gather first
      const s = await apiSearch(topic)
      setCandidates(s.candidates)
      const g = await apiGather(s.candidates)
      setRunId(g.run_id)
      setEvidence(g.evidence)
      const base = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
      setSseUrl(`${base}/api/v1/research/synthesize/stream?run_id=${g.run_id}`)
    } catch (e: any) {
      append(`Error: ${e?.message || String(e)}`)
    }
  }

  return (
    <main className="mx-auto max-w-4xl p-6 space-y-6">
      <header className="space-y-2">
        <h1 className="text-2xl font-semibold">Multi‑Agent Research</h1>
        <p className="text-sm text-gray-500">Backend: {process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}</p>
      </header>

      <section className="flex gap-2">
        <input
          className="flex-1 border rounded px-3 py-2"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Enter a research topic"
        />
        <button
          className="px-4 py-2 rounded bg-black text-white disabled:opacity-50"
          onClick={run}
          disabled={loading}
        >
          {loading ? 'Running…' : 'Run'}
        </button>
        <button className="px-4 py-2 rounded border" onClick={stream}>Stream Synthesis</button>
        {(synthesis || sseResult) && (
          <button
            className="px-4 py-2 rounded border"
            onClick={() => {
              const report = {
                topic,
                run_id: runId,
                optimized_queries: queries,
                candidates,
                evidence,
                synthesis: sseResult || synthesis,
                title: titleData || undefined,
                review: reviewIssues,
                generated_at: new Date().toISOString(),
              }
              const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
              const url = URL.createObjectURL(blob)
              const a = document.createElement('a')
              a.href = url
              a.download = `${(topic || 'research').toLowerCase().replace(/\s+/g, '_')}_report.json`
              document.body.appendChild(a)
              a.click()
              a.remove()
              URL.revokeObjectURL(url)
            }}
          >
            Download JSON
          </button>
        )}
        {(synthesis || sseResult) && (
          <button
            className="px-4 py-2 rounded border"
            onClick={async () => {
              const report = {
                topic,
                run_id: runId,
                optimized_queries: queries,
                candidates,
                evidence,
                synthesis: sseResult || synthesis,
                title: titleData || undefined,
                review: reviewIssues,
                generated_at: new Date().toISOString(),
              }
              const blob = await apiBundleZip(report)
              const url = URL.createObjectURL(blob)
              const a = document.createElement('a')
              a.href = url
              a.download = `${(topic || 'research').toLowerCase().replace(/\s+/g, '_')}_bundle.zip`
              document.body.appendChild(a)
              a.click()
              a.remove()
              URL.revokeObjectURL(url)
            }}
          >
            Download ZIP
          </button>
        )}
      </section>

      <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h2 className="font-medium mb-2">Candidates</h2>
          <ul className="space-y-2">
            {candidates.map((c) => (
              <li key={c.url} className="text-sm">
                <a className="text-blue-600 underline" href={c.url} target="_blank" rel="noreferrer">
                  {c.title || c.url}
                </a>
                <span className="text-gray-500"> {c.publisher ? `— ${c.publisher}` : ''}</span>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h2 className="font-medium mb-2">Evidence</h2>
          <ul className="space-y-3 max-h-[380px] overflow-auto pr-2">
            {evidence.map((e, i) => (
              <li key={e.checksum || i} className="text-sm">
                <div className="mb-1">{e.quote}</div>
                <a className="text-blue-600 underline" href={e.url} target="_blank" rel="noreferrer">
                  {e.title || e.url}
                </a>
              </li>
            ))}
          </ul>
        </div>
      </section>

      {(synthesis || sseResult) && (
        <section className="space-y-3">
          <h2 className="font-medium">Synthesis</h2>
          <div className="space-y-4">
            {(sseResult?.sections || synthesis?.sections || []).map((s: any, idx: number) => (
              <SectionCard key={idx} heading={s.heading} content={s.content} />
            ))}
          </div>
        </section>
      )}

      <LogPanel title="Log" lines={[...log, ...sseProgress]} />
    </main>
  )
}

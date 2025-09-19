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
    <main className="relative min-h-screen">
      <div className="pointer-events-none absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute inset-x-0 top-[-20%] h-[320px] bg-gradient-to-br from-indigo-500/40 via-purple-500/20 to-transparent blur-3xl" />
        <div className="absolute -right-32 bottom-[-10%] h-80 w-80 rounded-full bg-pink-500/20 blur-3xl" />
      </div>

      <div className="mx-auto flex w-full max-w-5xl flex-col gap-10 px-6 py-12">
        <header className="space-y-3 text-center md:text-left">
          <span className="inline-flex items-center justify-center rounded-full border border-white/20 bg-white/60 px-3 py-1 text-xs font-medium uppercase tracking-wide text-slate-700 shadow-sm backdrop-blur dark:border-white/10 dark:bg-white/10 dark:text-slate-200">
            Research cockpit
          </span>
          <h1 className="text-3xl font-semibold tracking-tight text-slate-900 dark:text-slate-100 md:text-4xl">
            Multi‑Agent Research Assistant
          </h1>
          <p className="mx-auto max-w-2xl text-sm text-slate-600 dark:text-slate-300 md:mx-0">
            Search, gather, synthesize, and review findings in one place. Powered by {process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}.
          </p>
        </header>

        <section className="rounded-3xl border border-white/40 bg-white/75 p-6 shadow-xl ring-1 ring-black/5 backdrop-blur-xl dark:border-white/10 dark:bg-slate-900/60 dark:ring-black/40">
          <div className="flex flex-col gap-4 md:flex-row md:items-center">
            <div className="flex-1 space-y-1">
              <label htmlFor="topic" className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500 dark:text-slate-300">
                Research topic
              </label>
              <input
                id="topic"
                className="w-full rounded-2xl border border-slate-200 bg-white/80 px-4 py-3 text-sm shadow-inner outline-none transition focus:border-indigo-400 focus:ring-4 focus:ring-indigo-200 dark:border-white/10 dark:bg-slate-900/60 dark:text-slate-100 dark:focus:border-indigo-400 dark:focus:ring-indigo-500/30"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="Enter a research topic"
              />
            </div>
            <div className="flex flex-wrap items-center gap-3 md:justify-end">
              <button
                className="inline-flex items-center justify-center rounded-2xl bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-500/30 transition hover:scale-[1.01] focus:outline-none focus-visible:ring-4 focus-visible:ring-indigo-300 disabled:cursor-not-allowed disabled:opacity-60"
                onClick={run}
                disabled={loading}
              >
                {loading ? 'Running…' : 'Run full workflow'}
              </button>
              <button
                className="rounded-2xl border border-indigo-300/60 bg-indigo-50/60 px-5 py-3 text-sm font-semibold text-indigo-700 transition hover:border-indigo-500 hover:text-indigo-800 focus:outline-none focus-visible:ring-4 focus-visible:ring-indigo-200 dark:border-indigo-400/40 dark:bg-indigo-500/10 dark:text-indigo-200"
                onClick={stream}
              >
                Stream Synthesis
              </button>
            </div>
          </div>

          {(synthesis || sseResult) && (
            <div className="mt-6 flex flex-wrap items-center gap-3 border-t border-white/40 pt-6 dark:border-white/10">
              <span className="text-xs font-semibold uppercase tracking-[0.3em] text-slate-500 dark:text-slate-300">
                exports
              </span>
              <div className="flex flex-wrap gap-3">
                <button
                  className="rounded-2xl border border-slate-200/80 bg-white/80 px-4 py-2 text-xs font-semibold uppercase tracking-wide text-slate-700 shadow-sm transition hover:border-slate-300 hover:bg-white focus:outline-none focus-visible:ring-4 focus-visible:ring-slate-200 dark:border-white/10 dark:bg-slate-900/60 dark:text-slate-200"
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
                <button
                  className="rounded-2xl border border-slate-200/80 bg-white/90 px-4 py-2 text-xs font-semibold uppercase tracking-wide text-slate-700 shadow-sm transition hover:border-slate-300 hover:bg-white focus:outline-none focus-visible:ring-4 focus-visible:ring-slate-200 dark:border-white/10 dark:bg-slate-900/60 dark:text-slate-200"
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
              </div>
            </div>
          )}
        </section>

        <section className="grid grid-cols-1 gap-6 md:grid-cols-2">
          <div className="rounded-3xl border border-white/30 bg-white/70 p-5 shadow-lg backdrop-blur-xl dark:border-white/10 dark:bg-slate-900/60">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-sm font-semibold uppercase tracking-[0.3em] text-slate-500 dark:text-slate-300">Candidates</h2>
              <span className="rounded-full bg-indigo-100 px-3 py-1 text-xs font-medium text-indigo-600 dark:bg-indigo-500/20 dark:text-indigo-200">
                {candidates.length} sources
              </span>
            </div>
            <ul className="space-y-3 text-sm text-slate-700 dark:text-slate-200">
              {candidates.map((c) => (
                <li key={c.url} className="group rounded-2xl border border-transparent bg-white/60 p-3 shadow-sm transition hover:border-indigo-200 hover:shadow-md dark:bg-slate-900/50 dark:hover:border-indigo-400/40">
                  <a className="text-sm font-semibold text-indigo-600 underline-offset-2 transition group-hover:underline dark:text-indigo-300" href={c.url} target="_blank" rel="noreferrer">
                    {c.title || c.url}
                  </a>
                  <div className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                    {c.publisher ? `${c.publisher}` : 'Unknown publisher'}
                    {c.date ? ` · ${c.date}` : ''}
                  </div>
                </li>
              ))}
              {!candidates.length && <li className="rounded-2xl border border-dashed border-slate-200 py-6 text-center text-xs text-slate-400 dark:border-white/10 dark:text-slate-500">Run a search to see recommended sources.</li>}
            </ul>
          </div>

          <div className="rounded-3xl border border-white/30 bg-white/70 p-5 shadow-lg backdrop-blur-xl dark:border-white/10 dark:bg-slate-900/60">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-sm font-semibold uppercase tracking-[0.3em] text-slate-500 dark:text-slate-300">Evidence</h2>
              <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-medium text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-200">
                {evidence.length} quotes
              </span>
            </div>
            <ul className="space-y-3 max-h-[380px] overflow-auto pr-2 text-sm text-slate-700 dark:text-slate-200">
              {evidence.map((e, i) => (
                <li key={e.checksum || i} className="rounded-2xl border border-transparent bg-white/60 p-3 shadow-sm transition hover:border-emerald-200 hover:shadow-md dark:bg-slate-900/50 dark:hover:border-emerald-400/40">
                  <div className="mb-2 text-sm leading-relaxed text-slate-700 dark:text-slate-100">{e.quote}</div>
                  <a className="text-xs font-semibold uppercase tracking-wide text-emerald-600 underline-offset-4 transition hover:underline dark:text-emerald-300" href={e.url} target="_blank" rel="noreferrer">
                    {e.title || e.url}
                  </a>
                </li>
              ))}
              {!evidence.length && <li className="rounded-2xl border border-dashed border-slate-200 py-6 text-center text-xs text-slate-400 dark:border-white/10 dark:text-slate-500">Evidence will appear here after gather.</li>}
            </ul>
          </div>
        </section>

        {(synthesis || sseResult) && (
          <section className="space-y-5">
            <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
              <h2 className="text-sm font-semibold uppercase tracking-[0.3em] text-slate-500 dark:text-slate-300">Synthesis</h2>
              {titleData && (
                <div className="rounded-2xl border border-white/40 bg-white/70 px-4 py-2 text-xs font-medium text-slate-600 shadow-sm backdrop-blur dark:border-white/10 dark:bg-slate-900/60 dark:text-slate-300">
                  {titleData.title}
                </div>
              )}
            </div>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              {(sseResult?.sections || synthesis?.sections || []).map((s: any, idx: number) => (
                <SectionCard key={idx} heading={s.heading} content={s.content} />
              ))}
            </div>
          </section>
        )}

        <LogPanel title="Run Activity" lines={[...log, ...sseProgress]} />
      </div>
    </main>
  )
}

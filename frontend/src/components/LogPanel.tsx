type Props = { title?: string; lines: string[] }

export default function LogPanel({ title = 'Log', lines }: Props) {
  return (
    <section className="rounded-3xl border border-white/30 bg-white/80 p-6 shadow-xl backdrop-blur-xl dark:border-white/10 dark:bg-slate-900/60">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-[0.3em] text-slate-500 dark:text-slate-300">{title}</h2>
        <span className="text-[10px] font-semibold uppercase tracking-[0.35em] text-slate-400 dark:text-slate-500">Real-time</span>
      </div>
      <div className="rounded-2xl border border-white/40 bg-white/70 p-4 shadow-inner transition dark:border-white/10 dark:bg-slate-900/50">
        <ul className="max-h-56 space-y-2 overflow-auto text-xs text-slate-600 dark:text-slate-300">
          {lines.map((l, idx) => (
            <li key={idx} className="flex items-start gap-3 rounded-2xl border border-transparent p-2 transition hover:border-indigo-200/60 dark:hover:border-indigo-400/30">
              <span className="mt-1 inline-flex h-2 w-2 flex-none rounded-full bg-emerald-400/80" />
              <span className="leading-relaxed">{l}</span>
            </li>
          ))}
          {!lines.length && (
            <li className="rounded-2xl border border-dashed border-slate-200 py-6 text-center text-[11px] uppercase tracking-[0.35em] text-slate-400 dark:border-white/10 dark:text-slate-500">
              Awaiting activity
            </li>
          )}
        </ul>
      </div>
    </section>
  )
}

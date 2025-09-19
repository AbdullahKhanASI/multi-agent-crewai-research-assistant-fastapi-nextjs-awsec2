type Props = { heading: string; content: any }

export default function SectionCard({ heading, content }: Props) {
  return (
    <div className="group relative overflow-hidden rounded-3xl border border-white/30 bg-white/80 p-6 shadow-xl transition hover:-translate-y-1 hover:shadow-2xl dark:border-white/10 dark:bg-slate-900/60">
      <div className="absolute inset-0 -z-10 bg-gradient-to-br from-white/80 via-white/40 to-transparent opacity-0 transition group-hover:opacity-100 dark:from-indigo-500/20 dark:via-purple-500/20" />
      <div className="relative space-y-4">
        <div className="text-lg font-semibold tracking-tight text-slate-900 dark:text-slate-100">{heading}</div>
        {typeof content === 'string' ? (
          <p className="whitespace-pre-wrap text-sm leading-relaxed text-slate-700 dark:text-slate-200">{content}</p>
        ) : Array.isArray(content) ? (
          <ul className="space-y-3 text-sm text-slate-700 dark:text-slate-200">
            {content.map((c: any, i: number) => {
              const isObject = typeof c === 'object' && c !== null
              const itemHeading = isObject && c.heading ? c.heading : undefined
              const rawContent = isObject && 'content' in c ? c.content : c
              const displayContent = typeof rawContent === 'string' ? rawContent : JSON.stringify(rawContent)

              return (
                <li key={i} className="flex gap-3">
                  <span className="mt-1 inline-flex h-2.5 w-2.5 flex-none rounded-full bg-indigo-400/70 group-hover:bg-indigo-500" />
                  <div className="space-y-1">
                    {itemHeading ? (
                      <div className="text-xs font-semibold uppercase tracking-[0.3em] text-slate-500 dark:text-slate-300">{itemHeading}</div>
                    ) : null}
                    <div className="text-sm leading-relaxed text-slate-700 dark:text-slate-100">{displayContent}</div>
                  </div>
                </li>
              )
            })}
          </ul>
        ) : (
          <pre className="overflow-auto rounded-2xl bg-slate-900/90 p-4 text-xs text-slate-100 shadow-inner">{JSON.stringify(content, null, 2)}</pre>
        )}
      </div>
    </div>
  )
}

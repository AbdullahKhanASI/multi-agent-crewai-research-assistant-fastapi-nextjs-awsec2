type Props = { title?: string; lines: string[] }

export default function LogPanel({ title = 'Log', lines }: Props) {
  return (
    <section>
      <div className="flex items-center justify-between mb-2">
        <h2 className="font-medium">{title}</h2>
      </div>
      <div className="rounded-lg border bg-gray-50 dark:bg-zinc-900 p-3">
        <ul className="text-xs space-y-1 text-gray-800 dark:text-gray-200 max-h-64 overflow-auto">
          {lines.map((l, idx) => (
            <li key={idx} className="leading-relaxed">
              <span className="inline-block w-2 h-2 rounded-full bg-emerald-500 mr-2 align-middle" />
              {l}
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}


type Props = { heading: string; content: any }

export default function SectionCard({ heading, content }: Props) {
  return (
    <div className="rounded-xl border p-4 bg-white/70 dark:bg-black/20">
      <div className="font-semibold mb-2 text-lg">{heading}</div>
      {typeof content === 'string' ? (
        <p className="whitespace-pre-wrap text-sm leading-relaxed">{content}</p>
      ) : Array.isArray(content) ? (
        <ul className="list-disc pl-5 space-y-2 text-sm">
          {content.map((c: any, i: number) => (
            <li key={i}>
              {c.heading ? <span className="font-medium">{c.heading}: </span> : null}
              {typeof c.content === 'string' ? c.content : JSON.stringify(c.content)}
            </li>
          ))}
        </ul>
      ) : (
        <pre className="text-xs whitespace-pre-wrap">{JSON.stringify(content, null, 2)}</pre>
      )}
    </div>
  )
}


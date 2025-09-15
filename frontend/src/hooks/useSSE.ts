import { useEffect, useRef, useState } from 'react'

export function useSSE(url?: string) {
  const [progress, setProgress] = useState<string[]>([])
  const [result, setResult] = useState<any | null>(null)
  const [open, setOpen] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const esRef = useRef<EventSource | null>(null)

  useEffect(() => {
    if (!url) return
    setProgress([])
    setResult(null)
    const es = new EventSource(url)
    esRef.current = es
    setOpen(true)

    const onAny = (e: MessageEvent) => {
      setProgress((prev) => [...prev, e.data])
    }
    const onProgress = (e: MessageEvent) => {
      setProgress((prev) => [...prev, e.data])
    }
    const onResult = (e: MessageEvent) => {
      try {
        setResult(JSON.parse(e.data))
      } catch {
        setResult(e.data)
      }
    }
    const onError = () => {
      setError('SSE connection error')
      setOpen(false)
      es.close()
    }

    es.addEventListener('message', onAny as any)
    es.addEventListener('progress', onProgress as any)
    es.addEventListener('result', onResult as any)
    es.onerror = onError

    return () => {
      es.close()
      setOpen(false)
    }
  }, [url])

  const reset = () => {
    setProgress([])
    setResult(null)
    setError(null)
  }

  return { progress, result, open, error, reset }
}

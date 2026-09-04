// lib/timedFetch.server.ts
// Drop-in replacement for `fetch()` in the server-only data fetchers
// (catalog.server.ts, blog.server.ts, sitemap.ts, etc). Sends
// `X-Client-Sent-At` so Django can report the inbound network hop, then
// reads Django's `X-Django-Received-At` / `X-Django-Sent-At` and
// `Server-Timing` response headers to log the full breakdown:
// Next.js -> Django, Django processing, DB, serialization, Django -> Next.js.

function parseServerTiming(header: string | null): Record<string, number> {
    const out: Record<string, number> = {}
    if (!header) return out
    for (const entry of header.split(',')) {
        const name = entry.match(/^\s*([a-zA-Z0-9_]+)/)?.[1]
        const dur = entry.match(/dur=([\d.]+)/)?.[1]
        if (name && dur) out[name] = parseFloat(dur)
    }
    return out
}

function fmt(ms: number | null | undefined): string {
    return ms === null || ms === undefined || Number.isNaN(ms) ? 'n/a' : `${ms.toFixed(1)}ms`
}

export async function timedFetch(url: string, init: RequestInit = {}): Promise<Response> {
    const clientSentAt = Date.now()
    const start = performance.now()

    const res = await fetch(url, {
        ...init,
        headers: { ...(init.headers as Record<string, string> | undefined), 'X-Client-Sent-At': String(clientSentAt) },
    })

    const clientReceivedAt = Date.now()
    const roundTripMs = performance.now() - start

    const djangoReceivedAt = Number(res.headers.get('x-django-received-at')) || null
    const djangoSentAt = Number(res.headers.get('x-django-sent-at')) || null
    const timing = parseServerTiming(res.headers.get('server-timing'))

    const nextToDjangoMs = djangoReceivedAt ? djangoReceivedAt - clientSentAt : null
    const djangoToNextMs = djangoSentAt ? clientReceivedAt - djangoSentAt : null

    console.log(
        `[timing] ${init.method ?? 'GET'} ${url} | ` +
        `next→django=${fmt(nextToDjangoMs)} ` +
        `processing=${fmt(timing.processing)} ` +
        `db=${fmt(timing.db)} (queries in Django log) ` +
        `serialization=${fmt(timing.serialization)} ` +
        `django→next=${fmt(djangoToNextMs)} ` +
        `total=${fmt(roundTripMs)}`,
    )

    return res
}

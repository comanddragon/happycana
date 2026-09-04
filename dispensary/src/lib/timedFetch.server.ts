// lib/timedFetch.server.ts
// Drop-in replacement for `fetch()` in the server-only data fetchers
// (catalog.server.ts, blog.server.ts, sitemap.ts, etc).

export async function timedFetch(url: string, init: RequestInit = {}): Promise<Response> {
    return fetch(url, init)
}

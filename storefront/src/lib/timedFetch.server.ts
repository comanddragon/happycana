// lib/timedFetch.server.ts
// Drop-in replacement for `fetch()` in the server-only data fetchers
// (catalog.server.ts, blog.server.ts, sitemap.ts, etc).

import { headers as requestHeaders } from 'next/headers'
import { DEFAULT_STOREFRONT_SLUG } from './storefront'

export async function timedFetch(url: string, init: RequestInit = {}): Promise<Response> {
    const headers = new Headers(init.headers)
    const incoming = await requestHeaders()
    const host = incoming.get('x-storefront-host')
        || incoming.get('x-forwarded-host')?.split(',', 1)[0]?.trim()
        || incoming.get('host')
    const explicitSlug = incoming.get('x-storefront') || DEFAULT_STOREFRONT_SLUG
    const hostname = host?.split(':', 1)[0].toLowerCase()
    const isLocal = hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '[::1]'
    if (isLocal && explicitSlug) headers.set('X-Storefront', explicitSlug)
    else if (host) headers.set('X-Storefront-Host', host)
    else if (DEFAULT_STOREFRONT_SLUG) headers.set('X-Storefront', DEFAULT_STOREFRONT_SLUG)
    return fetch(url, { ...init, headers })
}

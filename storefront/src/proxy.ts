import { NextRequest, NextResponse } from 'next/server'
import { DEFAULT_STOREFRONT_SLUG } from '@/lib/storefront'

function isLocalHostname(host: string): boolean {
    const hostname = host.split(':', 1)[0].toLowerCase()
    return hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '[::1]'
}

export function proxy(request: NextRequest) {
    const headers = new Headers(request.headers)
    const publicHost = request.headers.get('x-forwarded-host')?.split(',', 1)[0]?.trim()
        || request.headers.get('host')

    if (publicHost && isLocalHostname(publicHost) && DEFAULT_STOREFRONT_SLUG) {
        headers.set('x-storefront', DEFAULT_STOREFRONT_SLUG)
        headers.delete('x-storefront-host')
    } else if (publicHost) {
        headers.set('x-storefront-host', publicHost)
    }
    return NextResponse.next({ request: { headers } })
}

export const config = {
    matcher: ['/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp|ico)$).*)'],
}

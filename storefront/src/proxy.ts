import { NextRequest, NextResponse } from 'next/server'
import { DEFAULT_STOREFRONT_SLUG } from '@/lib/storefront'

const PRIVATE_IPV4_RANGES = [
    /^10\.\d{1,3}\.\d{1,3}\.\d{1,3}$/,
    /^192\.168\.\d{1,3}\.\d{1,3}$/,
    /^172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}$/,
]

function isLocalHostname(host: string): boolean {
    const hostname = host.split(':', 1)[0].toLowerCase()
    if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '[::1]') return true
    return PRIVATE_IPV4_RANGES.some((pattern) => pattern.test(hostname))
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
    matcher: ['/((?!_next/static|_next/image|.*\\.(?:svg|png|jpg|jpeg|gif|webp|ico)$).*)'],
}

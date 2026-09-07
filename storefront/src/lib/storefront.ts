import type { Storefront } from '@/types'

export const DEFAULT_STOREFRONT_NAME =
    process.env.NEXT_PUBLIC_STOREFRONT_NAME ||
    'Storefront'

export const DEFAULT_STOREFRONT_SLUG = process.env.NEXT_PUBLIC_STOREFRONT_SLUG || ''

const PRIVATE_IPV4_RANGES = [
    /^10\.\d{1,3}\.\d{1,3}\.\d{1,3}$/,
    /^192\.168\.\d{1,3}\.\d{1,3}$/,
    /^172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}$/,
]

/** True for hosts used to reach a local dev server, including from a LAN device. */
export function isLocalDevelopmentHost(host: string | null | undefined): boolean {
    if (!host) return false
    const value = host.split(',', 1)[0].trim().toLowerCase()
    let hostname = value
    try {
        hostname = new URL(`http://${value}`).hostname.replace(/^\[|\]$/g, '')
    } catch {
        hostname = value.split(':', 1)[0]
    }
    if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '::1') return true
    return PRIVATE_IPV4_RANGES.some(pattern => pattern.test(hostname))
}

export function siteUrl(): string {
    const value = process.env.NEXT_PUBLIC_FRONTEND_URL?.replace(/\/$/, '')
    if (value) return value
    if (process.env.NODE_ENV === 'production') {
        throw new Error('NEXT_PUBLIC_FRONTEND_URL is required in production')
    }
    return 'http://localhost:3000'
}

export function storefrontUrl(storefront?: Pick<Storefront, 'frontend_url'>): string {
    return storefront?.frontend_url?.replace(/\/$/, '') || siteUrl()
}

export function safeJsonLd(value: unknown): string {
    return JSON.stringify(value).replace(/</g, '\\u003c')
}

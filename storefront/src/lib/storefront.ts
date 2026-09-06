import type { Storefront } from '@/types'

export const DEFAULT_STOREFRONT_NAME =
    process.env.NEXT_PUBLIC_STOREFRONT_NAME ||
    'Storefront'

export const DEFAULT_STOREFRONT_SLUG = process.env.NEXT_PUBLIC_STOREFRONT_SLUG || ''

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

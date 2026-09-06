// lib/utils.ts
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs))
}

/**
 * Converts an absolute backend media URL to a proxied path so next/image
 * can serve it through localhost:3000/media/... instead of localhost:8000/media/...
 * In production, returns the URL unchanged.
 */
export function mediaUrl(url: string | null | undefined): string | null {
    if (!url) return null
    url = url.trim()
    if (!url) return null
    if (process.env.NODE_ENV === 'development') {
        try {
            const parsed = new URL(url)
            if (parsed.hostname === 'localhost' || parsed.hostname === '127.0.0.1') {
                return parsed.pathname + parsed.search
            }
        } catch {}
    }
    return url
}

export function formatPrice(value: string | number, currency = 'USD'): string {
    const n = typeof value === 'string' ? parseFloat(value) : value
    return new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(n)
}

export function formatDate(iso: string): string {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric', month: 'short', day: 'numeric',
    }).format(new Date(iso))
}

export function formatRelativeDate(iso: string): string {
    const diff = Date.now() - new Date(iso).getTime()
    const mins  = Math.floor(diff / 60_000)
    const hours = Math.floor(diff / 3_600_000)
    const days  = Math.floor(diff / 86_400_000)
    if (mins < 1)   return 'just now'
    if (mins < 60)  return `${mins}m ago`
    if (hours < 24) return `${hours}h ago`
    if (days < 7)   return `${days}d ago`
    return formatDate(iso)
}

export function slugify(s: string): string {
    return s.toLowerCase().replace(/\s+/g, '-').replace(/[^\w-]/g, '')
}

export const ORDER_STATUS_LABEL: Record<string, string> = {
    pending:    'Pending',
    confirmed:  'Confirmed',
    processing: 'Processing',
    shipped:    'Shipped',
    delivered:  'Delivered',
    cancelled:  'Cancelled',
    refunded:   'Refunded',
}

export const ORDER_STATUS_COLOR: Record<string, string> = {
    pending:    'bg-amber-50 text-amber-700 ring-amber-200',
    confirmed:  'bg-blue-50 text-blue-700 ring-blue-200',
    processing: 'bg-violet-50 text-violet-700 ring-violet-200',
    shipped:    'bg-sky-50 text-sky-700 ring-sky-200',
    delivered:  'bg-brand-50 text-brand-700 ring-brand-200',
    cancelled:  'bg-red-50 text-red-700 ring-red-200',
    refunded:   'bg-surface-100 text-surface-600 ring-surface-200',
}

export const PAYMENT_STATUS_COLOR: Record<string, string> = {
    pending:            'bg-amber-50 text-amber-700',
    paid:               'bg-brand-50 text-brand-700',
    failed:             'bg-red-50 text-red-700',
    refunded:           'bg-surface-100 text-surface-600',
    partially_refunded: 'bg-orange-50 text-orange-700',
}

export const CANNABIS_TYPE_LABEL: Record<string, string> = {
    sativa:         'Sativa',
    indica:         'Indica',
    hybrid:         'Hybrid',
    hybrid_sativa:  'Hybrid (Sativa Leaning)',
    hybrid_indica:  'Hybrid (Indica Leaning)',
    na:             'N/A',
}

export const COMPLIANCE_CATEGORY_LABEL: Record<string, string> = {
    flower:        'Flower',
    vaporizers:    'Vaporizers',
    edibles:       'Edibles',
    concentrates:  'Concentrates',
    pre_rolls:     'Pre-Rolls',
    tinctures:     'Tinctures',
    topicals:      'Topicals',
    beverages:     'Beverages',
    accessories:   'Accessories',
    merchandise:   'Merchandise',
    cbd_products:  'CBD Products',
    gift_cards:    'Gift Cards',
}

export const POTENCY_LABEL: Record<string, string> = {
    mild:   'Mild',
    medium: 'Medium',
    strong: 'Strong',
}

// Simple preset ranges for the THC filter — a dual min/max slider isn't
// worth the extra dependency for a filter most shoppers use as "at least X%".
export const THC_PRESETS: { label: string; min_thc?: number; max_thc?: number }[] = [
    { label: 'Any potency' },
    { label: '15%+',        min_thc: 15 },
    { label: '20%+',        min_thc: 20 },
    { label: '25%+',        min_thc: 25 },
    { label: '30%+',        min_thc: 30 },
]

/** e.g. formatWeight('3.5', 'grams') -> '3.5g'; formatWeight('100', 'milligrams') -> '100mg' */
export function formatWeight(value: string | null | undefined, unit: string | null | undefined): string | null {
    if (!value) return null
    const suffix = unit === 'milligrams' ? 'mg' : unit === 'grams' ? 'g' : unit === 'each' ? '' : ''
    return `${value}${suffix}`
}

/** e.g. formatThc('23.500') -> '23.5% THC' */
export function formatThc(value: string | null | undefined): string | null {
    if (!value) return null
    const n = parseFloat(value)
    if (Number.isNaN(n)) return null
    return `${n}% THC`
}

export function getVariantLabel(variant: {
    attributes: { name: string; value: string }[]
    weight_value?: string | null
    weight_unit?: string
    sku?: string
}): string {
    if (variant.attributes.length > 0) {
        return variant.attributes.map(a => a.value).join(' / ')
    }
    // Most seeded products have exactly one variant with no EAV attributes —
    // fall back to real weight data, then the SKU, rather than a blank label.
    return formatWeight(variant.weight_value, variant.weight_unit) || variant.sku || 'Default'
}

export function truncate(str: string, n: number): string {
    return str.length > n ? str.slice(0, n - 1) + '…' : str
}

/** Convert scraped product-description HTML into readable, safe plain text. */
export function stripHtml(value: string | null | undefined): string {
    if (!value) return ''
    return value
        .replace(/<br\s*\/?>/gi, '\n')
        .replace(/<\/p>|<\/li>/gi, '\n')
        .replace(/<[^>]*>/g, '')
        .replace(/&nbsp;/gi, ' ')
        .replace(/&amp;/gi, '&')
        .replace(/&lt;/gi, '<')
        .replace(/&gt;/gi, '>')
        .replace(/&quot;/gi, '"')
        .replace(/&#39;/gi, "'")
        .replace(/[ \t]+\n/g, '\n')
        .replace(/\n{3,}/g, '\n\n')
        .trim()
}

/** e.g. titleCase('beta_caryophyllene') -> 'Beta Caryophyllene' */
export function titleCase(str: string): string {
    return str.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

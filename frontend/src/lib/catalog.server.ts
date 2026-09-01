// lib/catalog.server.ts
// Server-only data fetchers for the catalog. These call the backend
// directly via `process.env.API_URL` (not the axios `api` client in
// lib/api.ts, which is wired for the browser — auth cookies, 401 refresh,
// etc.). Used from Server Components and route handlers only.

import type {
    Product, Effect, Category, Brand, PaginatedResponse, ProductFilterParams, LabResult,
} from '@/types'

const EMPTY_PRODUCTS: PaginatedResponse<Product> = {
    count: 0, next: null, previous: null, results: [],
}

function buildQuery(params?: ProductFilterParams): string {
    if (!params) return ''
    const qs = new URLSearchParams()
    for (const [key, value] of Object.entries(params)) {
        if (value === undefined || value === null || value === '') continue
        qs.set(key, String(value))
    }
    const s = qs.toString()
    return s ? `?${s}` : ''
}

/**
 * `revalidate`: seconds to cache for (default 1h — fine for the handful of
 * fixed queries the homepage reuses across every visitor). Pass a shorter
 * window, or `false` for `no-store`, for pages like the filtered product
 * grid where the query string is effectively unbounded and caching every
 * combination isn't worth it.
 */
export async function getProducts(
    params?: ProductFilterParams,
    { revalidate = 3600 }: { revalidate?: number | false } = {},
): Promise<PaginatedResponse<Product>> {
    try {
        const res = await fetch(`${process.env.API_URL}/catalog/products/${buildQuery(params)}`, {
            ...(revalidate === false ? { cache: 'no-store' } : { next: { revalidate } }),
        })
        if (!res.ok) return EMPTY_PRODUCTS
        const data = await res.json()
        return Array.isArray(data?.results) ? data : EMPTY_PRODUCTS
    } catch {
        return EMPTY_PRODUCTS
    }
}

export async function getEffects(): Promise<Effect[]> {
    try {
        const res = await fetch(`${process.env.API_URL}/catalog/effects/`, {
            next: { revalidate: 3600 },
        })
        if (!res.ok) return []
        const data = await res.json()
        return Array.isArray(data) ? data : (data?.results ?? [])
    } catch {
        return []
    }
}

export async function getCategories(): Promise<Category[]> {
    try {
        const res = await fetch(`${process.env.API_URL}/catalog/categories/`, {
            next: { revalidate: 3600 },
        })
        if (!res.ok) return []
        const data = await res.json()
        return Array.isArray(data) ? data : (data?.results ?? [])
    } catch {
        return []
    }
}

export async function getBrands(): Promise<Brand[]> {
    try {
        const res = await fetch(`${process.env.API_URL}/catalog/brands/?page_size=200`, {
            next: { revalidate: 3600 },
        })
        if (!res.ok) return []
        const data = await res.json()
        return Array.isArray(data) ? data : (data?.results ?? [])
    } catch {
        return []
    }
}

const EMPTY_LAB_RESULTS: PaginatedResponse<LabResult> = {
    count: 0, next: null, previous: null, results: [],
}

/** Every variant with a real, on-file COA — backs the /learn/lab-results index page. */
export async function getLabResults(page?: number): Promise<PaginatedResponse<LabResult>> {
    try {
        const qs = page ? `?page=${page}` : ''
        const res = await fetch(`${process.env.API_URL}/catalog/labs/${qs}`, {
            next: { revalidate: 3600 },
        })
        if (!res.ok) return EMPTY_LAB_RESULTS
        const data = await res.json()
        return Array.isArray(data?.results) ? data : EMPTY_LAB_RESULTS
    } catch {
        return EMPTY_LAB_RESULTS
    }
}

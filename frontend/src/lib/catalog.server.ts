// lib/catalog.server.ts
// Server-only data fetchers for the catalog. These call the backend
// directly via `process.env.API_URL` (not the axios `api` client in
// lib/api.ts, which is wired for the browser — auth cookies, 401 refresh,
// etc.). Used from Server Components and route handlers only.

import { cache } from 'react'
import { timedFetch } from './timedFetch.server'
import type {
    Product, Effect, Category, Collection, Brand, PaginatedResponse, ProductFilterParams, LabResult,
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
        const res = await timedFetch(`${process.env.API_URL}/catalog/products/${buildQuery(params)}`, {
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
        const res = await timedFetch(`${process.env.API_URL}/catalog/effects/`, {
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
        const res = await timedFetch(`${process.env.API_URL}/catalog/categories/?page_size=100`, {
            next: { revalidate: 3600 },
        })
        if (!res.ok) return []
        const data = await res.json()
        return Array.isArray(data) ? data : (data?.results ?? [])
    } catch {
        return []
    }
}

export async function getFreshCategories(): Promise<Category[]> {
    try {
        const res = await timedFetch(`${process.env.API_URL}/catalog/categories/?page_size=100`, { cache: 'no-store' })
        if (!res.ok) return []
        const data = await res.json()
        return Array.isArray(data) ? data : (data?.results ?? [])
    } catch {
        return []
    }
}

export function flattenCategories(categories: Category[]): Category[] {
    return categories.flatMap(category => [
        category,
        ...flattenCategories(category.children ?? []),
    ])
}

export async function getCategory(slug: string): Promise<Category | null> {
    try {
        const res = await timedFetch(`${process.env.API_URL}/catalog/categories/${encodeURIComponent(slug)}/`, {
            next: { revalidate: 3600 },
        })
        if (!res.ok) return null
        return await res.json()
    } catch {
        return null
    }
}

export async function getCollections(): Promise<Collection[]> {
    try {
        const res = await timedFetch(`${process.env.API_URL}/catalog/collections/`, {
            next: { revalidate: 3600 },
        })
        if (!res.ok) return []
        const data = await res.json()
        return Array.isArray(data) ? data : (data?.results ?? [])
    } catch {
        return []
    }
}

// Wrapped in React's `cache()` so the two `getCollection(slug)` call sites in
// app/shop/collections/[slug]/page.tsx (generateMetadata + the page
// component) explicitly share one fetch per request, instead of relying on
// Next.js's fetch-level memoization silently doing it for them.
export const getCollection = cache(async (slug: string): Promise<Collection | null> => {
    try {
        const res = await timedFetch(`${process.env.API_URL}/catalog/collections/${encodeURIComponent(slug)}/`, {
            next: { revalidate: 3600 },
        })
        if (!res.ok) return null
        return await res.json()
    } catch {
        return null
    }
})

export async function getCollectionProducts(
    slug: string,
    params?: Omit<ProductFilterParams, 'category'>,
    { revalidate = 3600 }: { revalidate?: number | false } = {},
): Promise<PaginatedResponse<Product>> {
    try {
        const res = await timedFetch(
            `${process.env.API_URL}/catalog/collections/${encodeURIComponent(slug)}/products/${buildQuery(params)}`,
            revalidate === false ? { cache: 'no-store' } : { next: { revalidate } },
        )
        if (!res.ok) return EMPTY_PRODUCTS
        const data = await res.json()
        return Array.isArray(data?.results) ? data : EMPTY_PRODUCTS
    } catch {
        return EMPTY_PRODUCTS
    }
}

export async function getBrands(): Promise<Brand[]> {
    try {
        const res = await timedFetch(`${process.env.API_URL}/catalog/brands/?page_size=200`, {
            next: { revalidate: 3600 },
        })
        if (!res.ok) return []
        const data = await res.json()
        return Array.isArray(data) ? data : (data?.results ?? [])
    } catch {
        return []
    }
}

export async function getBrand(slug: string): Promise<Brand | null> {
    try {
        const res = await timedFetch(`${process.env.API_URL}/catalog/brands/${encodeURIComponent(slug)}/`, {
            next: { revalidate: 3600 },
        })
        if (!res.ok) return null
        return await res.json()
    } catch {
        return null
    }
}

const EMPTY_LAB_RESULTS: PaginatedResponse<LabResult> = {
    count: 0, next: null, previous: null, results: [],
}

/** Every variant with a real, on-file COA — backs the /lab-results index page. */
export async function getLabResults(page?: number): Promise<PaginatedResponse<LabResult>> {
    try {
        const qs = page ? `?page=${page}` : ''
        const res = await timedFetch(`${process.env.API_URL}/catalog/labs/${qs}`, {
            next: { revalidate: 3600 },
        })
        if (!res.ok) return EMPTY_LAB_RESULTS
        const data = await res.json()
        return Array.isArray(data?.results) ? data : EMPTY_LAB_RESULTS
    } catch {
        return EMPTY_LAB_RESULTS
    }
}

// lib/blog.server.ts
// Server-only data fetchers for the blog. Calls the backend directly via
// `process.env.API_URL`, same pattern as lib/catalog.server.ts. Used from
// Server Components and route handlers only.

import { timedFetch } from './timedFetch.server'
import type { BlogPostSummary, BlogPostDetail, PaginatedResponse } from '@/types'

const EMPTY_POSTS: PaginatedResponse<BlogPostSummary> = {
    count: 0, next: null, previous: null, results: [],
}

export async function getBlogPosts(
    { page = 1, page_size, revalidate = 3600 }: { page?: number; page_size?: number; revalidate?: number | false } = {},
): Promise<PaginatedResponse<BlogPostSummary>> {
    try {
        const params = new URLSearchParams({ page: String(page) })
        if (page_size) params.set('page_size', String(page_size))
        const res = await timedFetch(`${process.env.API_URL}/blog/posts/?${params.toString()}`, {
            ...(revalidate === false ? { cache: 'no-store' } : { next: { revalidate } }),
        })
        if (!res.ok) return EMPTY_POSTS
        const data = await res.json()
        return Array.isArray(data?.results) ? data : EMPTY_POSTS
    } catch {
        return EMPTY_POSTS
    }
}

// Walks every page of the blog (the list endpoint caps at page_size=100 —
// see core/pagination.py's max_page_size — so a catalog with more posts
// than that needs more than one request). Used by the sitemap, which
// needs every published post, not just the first page. Hard-capped at 50
// pages (5,000 posts) as a sanity ceiling against an accidental infinite
// loop if the backend ever returns malformed pagination.
export async function getAllBlogPosts(
    { revalidate = 3600 }: { revalidate?: number | false } = {},
): Promise<BlogPostSummary[]> {
    const posts: BlogPostSummary[] = []
    let page = 1
    for (; page <= 50; page++) {
        const { results, next } = await getBlogPosts({ page, page_size: 100, revalidate })
        posts.push(...results)
        if (!next || results.length === 0) break
    }
    return posts
}

export async function getBlogPost(slug: string): Promise<BlogPostDetail | null> {
    try {
        const res = await timedFetch(`${process.env.API_URL}/blog/posts/${slug}/`, {
            next: { revalidate: 3600 },
        })
        if (!res.ok) return null
        return await res.json()
    } catch {
        return null
    }
}

export function formatPostDate(iso: string | null): string {
    if (!iso) return ''
    return new Date(iso).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
}

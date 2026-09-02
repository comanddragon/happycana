// lib/blog.server.ts
// Server-only data fetchers for the blog. Calls the backend directly via
// `process.env.API_URL`, same pattern as lib/catalog.server.ts. Used from
// Server Components and route handlers only.

import type { BlogPostSummary, BlogPostDetail, PaginatedResponse } from '@/types'

const EMPTY_POSTS: PaginatedResponse<BlogPostSummary> = {
    count: 0, next: null, previous: null, results: [],
}

export async function getBlogPosts(
    { page = 1, revalidate = 3600 }: { page?: number; revalidate?: number | false } = {},
): Promise<PaginatedResponse<BlogPostSummary>> {
    try {
        const res = await fetch(`${process.env.API_URL}/blog/posts/?page=${page}`, {
            ...(revalidate === false ? { cache: 'no-store' } : { next: { revalidate } }),
        })
        if (!res.ok) return EMPTY_POSTS
        const data = await res.json()
        return Array.isArray(data?.results) ? data : EMPTY_POSTS
    } catch {
        return EMPTY_POSTS
    }
}

export async function getBlogPost(slug: string): Promise<BlogPostDetail | null> {
    try {
        const res = await fetch(`${process.env.API_URL}/blog/posts/${slug}/`, {
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

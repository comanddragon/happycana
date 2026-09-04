// app/sitemap.ts
import type { MetadataRoute } from 'next'
import type { Product } from '@/types'
import { getAllBlogPosts } from "@/lib/blog.server";
import { getCategories, getCollections } from '@/lib/catalog.server'

async function getAllBrandsForSitemap() {
    const brands = []
    let page = 1
    while (true) {
        const response = await fetch(`${process.env.API_URL}/catalog/brands/?page=${page}&page_size=100`, {
            next: { revalidate: 3600 },
        })
        if (!response.ok) throw new Error(`Failed to fetch brands: ${response.status}`)
        const data = await response.json()
        brands.push(...(Array.isArray(data) ? data : data.results ?? []))
        if (Array.isArray(data) || !data.next) break
        page += 1
    }
    return brands
}

export const dynamic = 'force-dynamic'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
    const siteUrl = process.env.NEXT_PUBLIC_FRONTEND_URL || 'http://localhost:3000'
    const staticEntries = [
        { url: siteUrl, priority: 1 },
        { url: `${siteUrl}/shop`, priority: 0.9 },
        { url: `${siteUrl}/shop/products`, priority: 0.9 },
        { url: `${siteUrl}/shop/new-arrivals`, priority: 0.8 },
        { url: `${siteUrl}/shop/best-sellers`, priority: 0.8 },
        { url: `${siteUrl}/blog`, priority: 0.7 },
        { url: `${siteUrl}/lab-results`, priority: 0.6 },
        { url: `${siteUrl}/help/faq`, priority: 0.5 },
    ]

    // Answer/informational content — the highest-priority gap called out in
    // the SEO/AEO audit — needs to be discoverable by crawlers even though
    // it isn't linked from the dynamic product catalog below.
    //
    // getAllBlogPosts() walks every page (the list endpoint caps a single
    // page at 100 — see core/pagination.py) rather than just the first
    // page/20 posts, since the blog can run into the hundreds of posts and
    // the previous single-page fetch here silently left most of them out
    // of the sitemap entirely.
    const posts = await getAllBlogPosts()
    const blogEntries = posts.map(p => ({
        url: `${siteUrl}/blog/${p.slug}`,
        lastModified: p.published_at ?? undefined,
        changeFrequency: 'monthly',
        priority: 0.6,
    }))

    try {
        const [categories, collections, brands] = await Promise.all([getCategories(), getCollections(), getAllBrandsForSitemap()])
        const productRows: Product[] = []
        let page = 1
        while (true) {
            const res = await fetch(`${process.env.API_URL}/catalog/products/?page=${page}&page_size=100`, {
                next: { revalidate: 3600 },
            })
            if (!res.ok) throw new Error(`Failed to fetch products: ${res.status}`)
            const data = await res.json()
            productRows.push(...data.results)
            if (!data.next) break
            page += 1
        }

        const products: MetadataRoute.Sitemap = productRows.map((p: Product) => ({
            url: `${siteUrl}/shop/products/${p.slug}`,
            lastModified: p.updated_at,
            changeFrequency: 'weekly' as const,
            priority: 0.8,
        }))

        const categoryEntries: MetadataRoute.Sitemap = categories.filter(c => c.is_key).map(c => ({
            url: `${siteUrl}/shop/categories/${c.slug}`,
            changeFrequency: 'weekly' as const,
            priority: 0.8,
        }))
        const collectionEntries: MetadataRoute.Sitemap = collections.filter(c => c.product_count > 0).map(c => ({
            url: `${siteUrl}/shop/collections/${c.slug}`,
            changeFrequency: 'weekly' as const,
            priority: 0.7,
        }))
        const brandEntries: MetadataRoute.Sitemap = brands.map(b => ({
            url: `${siteUrl}/shop/brands/${b.slug}`,
            changeFrequency: 'weekly' as const,
            priority: 0.7,
        }))

        return [...staticEntries, ...categoryEntries, ...collectionEntries, ...brandEntries, ...blogEntries, ...products]
    } catch (e) {
        return [...staticEntries, ...blogEntries]
    }
}

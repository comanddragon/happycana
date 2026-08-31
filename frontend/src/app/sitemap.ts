// app/sitemap.ts
import {Product} from "@/types";

export const dynamic = 'force-dynamic'

export default async function sitemap() {
    const staticEntries = [
        { url: `${process.env.NEXT_PUBLIC_FRONTEND_URL}`, priority: 1 },
        { url: `${process.env.NEXT_PUBLIC_FRONTEND_URL}/shop`, priority: 0.9 },
    ]

    try {
        const res = await fetch(`${process.env.API_URL}/catalog/products/?page_size=1000`, {
            next: { revalidate: 3600 },
        })
        if (!res.ok) throw new Error(`Failed to fetch products: ${res.status}`)
        const data = await res.json()

        const products = data.results.map((p: Product) => ({
            url: `${process.env.NEXT_PUBLIC_FRONTEND_URL}/shop/products/${p.slug}`,
            lastModified: p.updated_at,
            changeFrequency: 'weekly',
            priority: 0.8,
        }))

        return [...staticEntries, ...products]
    } catch (e) {
        return staticEntries
    }
}
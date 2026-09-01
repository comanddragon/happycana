// app/sitemap.ts
import {Product} from "@/types";
import {GUIDES} from "@/lib/guides";

export const dynamic = 'force-dynamic'

export default async function sitemap() {
    const staticEntries = [
        { url: `${process.env.NEXT_PUBLIC_FRONTEND_URL}`, priority: 1 },
        { url: `${process.env.NEXT_PUBLIC_FRONTEND_URL}/shop`, priority: 0.9 },
        { url: `${process.env.NEXT_PUBLIC_FRONTEND_URL}/shop/products`, priority: 0.9 },
        { url: `${process.env.NEXT_PUBLIC_FRONTEND_URL}/learn`, priority: 0.7 },
        { url: `${process.env.NEXT_PUBLIC_FRONTEND_URL}/learn/lab-results`, priority: 0.6 },
        { url: `${process.env.NEXT_PUBLIC_FRONTEND_URL}/help/faq`, priority: 0.5 },
    ]

    // Answer/informational content — the highest-priority gap called out in
    // the SEO/AEO audit — needs to be discoverable by crawlers even though
    // it isn't linked from the dynamic product catalog below.
    const guideEntries = GUIDES.map(g => ({
        url: `${process.env.NEXT_PUBLIC_FRONTEND_URL}/learn/${g.slug}`,
        changeFrequency: 'monthly',
        priority: 0.6,
    }))

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

        return [...staticEntries, ...guideEntries, ...products]
    } catch (e) {
        return [...staticEntries, ...guideEntries]
    }
}
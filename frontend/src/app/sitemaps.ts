// app/sitemap.ts
import {Product} from "@/types";

export default async function sitemap() {
    const res = await fetch(`${process.env.API_URL}/catalog/products/?page_size=1000`)
    const data = await res.json()

    const products = data.results.map((p: Product) => ({
        url: `https://yourstore.com/shop/products/${p.slug}`,
        lastModified: p.updated_at,
        changeFrequency: 'weekly',
        priority: 0.8,
    }))

    return [
        { url: 'https://yourstore.com', priority: 1 },
        { url: 'https://yourstore.com/shop', priority: 0.9 },
        ...products,
    ]
}
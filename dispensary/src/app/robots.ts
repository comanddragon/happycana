// app/robots.ts
import type { MetadataRoute } from 'next'

export default function robots(): MetadataRoute.Robots {
    return {
        rules: {
            userAgent: '*',
            allow: '/',
            disallow: ['/account/', '/shop/checkout', '/login', '/register', '/api/'],
        },
        sitemap: `${process.env.NEXT_PUBLIC_FRONTEND_URL}/sitemap.xml`,
        host: process.env.NEXT_PUBLIC_FRONTEND_URL,
    }
}

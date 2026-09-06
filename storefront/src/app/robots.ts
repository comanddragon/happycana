// app/robots.ts
import type { MetadataRoute } from 'next'
import { siteUrl } from '@/lib/storefront'

export default function robots(): MetadataRoute.Robots {
    const canonicalOrigin = siteUrl()
    return {
        rules: {
            userAgent: '*',
            allow: '/',
            disallow: ['/account/', '/shop/checkout', '/login', '/register', '/api/'],
        },
        sitemap: `${canonicalOrigin}/sitemap.xml`,
        host: canonicalOrigin,
    }
}

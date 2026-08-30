// app/(shop)/shop/products/[slug]/page.tsx
import type { Metadata } from 'next'
import { notFound } from 'next/navigation'
import { ProductDetails } from '@/components/shop/ProductDetails' // client component

// ── Types ──────────────────────────────────────────────────────────────────

interface PageProps {
    params: Promise<{ slug: string }>
}

// ── Data fetching ──────────────────────────────────────────────────────────

async function getProduct(slug: string) {
    const res = await fetch(`${process.env.API_URL}/catalog/products/${slug}/`, {
        next: { revalidate: 60 },
    })
    if (res.status === 404) notFound()
    if (!res.ok) throw new Error(`Failed to fetch product: ${res.status}`)
    return res.json()
}

// ── Metadata ───────────────────────────────────────────────────────────────

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
    const { slug } = await params
    const product  = await getProduct(slug)

    return {
        title:       product.meta_title || product.name,
        description: product.meta_description || product.description?.slice(0, 160),
        openGraph: {
            title:       product.name,
            description: product.description?.slice(0, 160),
            images: product.primary_image
                ? [{ url: product.primary_image.image_url, alt: product.primary_image.alt_text }]
                : [],
        },
    }
}

// ── Page ───────────────────────────────────────────────────────────────────

export default async function ProductPage({ params }: PageProps) {
    const { slug } = await params
    const product  = await getProduct(slug)

    const jsonLd = {
        '@context': 'https://schema.org',
        '@type':    'Product',
        name:        product.name,
        description: product.description,
        image:       product.primary_image?.image_url,
        ...(product.brand && { brand: { '@type': 'Brand', name: product.brand.name } }),
        offers: {
            '@type':        'Offer',
            price:           product.base_price,
            priceCurrency:  'USD',
            availability:   'https://schema.org/InStock',
        },
    }

    return (
        <>
            <script
                type="application/ld+json"
                dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
            />
            {/* All interactive UI lives in the client component */}
            <ProductDetails product={product} />
        </>
    )
}
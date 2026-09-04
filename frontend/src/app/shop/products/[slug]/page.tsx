// app/(shop)/shop/products/[slug]/page.tsx
import type { Metadata } from 'next'
import { notFound } from 'next/navigation'
import { ProductDetails } from '@/components/shop/ProductDetails' // client component
import type { Product, ProductVariant } from '@/types'
import { stripHtml } from '@/lib/utils'
import { timedFetch } from '@/lib/timedFetch.server'

// ── Types ──────────────────────────────────────────────────────────────────

interface PageProps {
    params: Promise<{ slug: string }>
}

// ── Data fetching ──────────────────────────────────────────────────────────

async function getProduct(slug: string): Promise<Product> {
    const res = await timedFetch(`${process.env.API_URL}/catalog/products/${slug}/`, {
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
    const canonicalPath = `/shop/products/${product.slug}`
    const description = product.meta_description || stripHtml(product.description).slice(0, 160)
    const ogImageUrl = product.primary_image?.image_url ?? undefined

    return {
        title:       product.meta_title || product.name,
        description,
        alternates: {
            canonical: canonicalPath,
        },
        openGraph: {
            type:        'website',
            title:       product.name,
            description,
            url:         canonicalPath,
            images: ogImageUrl
                ? [{ url: ogImageUrl, alt: product.primary_image?.alt_text || product.name }]
                : undefined,
        },
        twitter: {
            card:        ogImageUrl ? 'summary_large_image' : 'summary',
            title:       product.meta_title || product.name,
            description,
            images: ogImageUrl ? [ogImageUrl] : undefined,
        },
    }
}

// ── Schema helpers ────────────────────────────────────────────────────────

function buildOffers(product: Product, siteUrl: string) {
    const variants: ProductVariant[] = product.variants ?? []
    const prices = variants
        .map(v => parseFloat(v.price))
        .filter(p => !Number.isNaN(p))
    const anyInStock = variants.length > 0
        ? variants.some(v => v.in_stock)
        : true // no variants modeled yet — don't assert OutOfStock without data
    const availability = anyInStock
        ? 'https://schema.org/InStock'
        : 'https://schema.org/OutOfStock'

    if (prices.length > 1) {
        const low  = Math.min(...prices)
        const high = Math.max(...prices)
        return {
            '@type':      'AggregateOffer',
            priceCurrency: 'USD',
            lowPrice:      low,
            highPrice:     high,
            offerCount:    variants.length,
            availability,
            url:           `${siteUrl}/shop/products/${product.slug}`,
        }
    }

    const price = prices[0] ?? parseFloat(product.base_price)
    return {
        '@type':        'Offer',
        price,
        priceCurrency: 'USD',
        availability,
        url:            `${siteUrl}/shop/products/${product.slug}`,
        ...(variants[0]?.sku && { sku: variants[0].sku }),
    }
}

// ── Page ───────────────────────────────────────────────────────────────────

export default async function ProductPage({ params }: PageProps) {
    const { slug } = await params
    const product  = await getProduct(slug)
    const siteUrl  = process.env.NEXT_PUBLIC_FRONTEND_URL ?? ''
    const productUrl = `${siteUrl}/shop/products/${product.slug}`
    const category = product.category?.[0] ?? null

    const jsonLd = {
        '@context': 'https://schema.org',
        '@type':    'Product',
        name:        product.name,
        description: stripHtml(product.description),
        image:       product.primary_image?.image_url,
        url:         productUrl,
        ...(product.variants?.[0]?.sku && { sku: product.variants[0].sku }),
        ...(product.brand && { brand: { '@type': 'Brand', name: product.brand.name } }),
        offers: buildOffers(product, siteUrl),
    }

    const breadcrumbLd = {
        '@context': 'https://schema.org',
        '@type':    'BreadcrumbList',
        itemListElement: [
            { '@type': 'ListItem', position: 1, name: 'Shop',    item: `${siteUrl}/shop` },
            ...(category
                ? [{
                    '@type': 'ListItem',
                    position: 2,
                    name: category.name,
                    item: category.is_key
                        ? `${siteUrl}/shop/categories/${category.slug}`
                        : `${siteUrl}/shop/collections/${category.slug}`,
                }]
                : []),
            {
                '@type':  'ListItem',
                position: category ? 3 : 2,
                name:     product.name,
                item:     productUrl,
            },
        ],
    }

    return (
        <>
            <script
                type="application/ld+json"
                dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
            />
            <script
                type="application/ld+json"
                dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbLd) }}
            />
            {/* All interactive UI lives in the client component */}
            <ProductDetails product={product} />
        </>
    )
}

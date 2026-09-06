// app/(shop)/shop/products/[slug]/page.tsx
import type { Metadata } from 'next'
import { cache } from 'react'
import { notFound } from 'next/navigation'
import { ProductDetails } from '@/components/shop/ProductDetails' // client component
import type { Listing, Product, ProductVariant } from '@/types'
import { stripHtml } from '@/lib/utils'
import { timedFetch } from '@/lib/timedFetch.server'
import { getStorefront } from '@/lib/storefront.server'
import { safeJsonLd, siteUrl } from '@/lib/storefront'

// ── Types ──────────────────────────────────────────────────────────────────

interface PageProps {
    params: Promise<{ slug: string }>
}

// ── Data fetching ──────────────────────────────────────────────────────────

// Wrapped in React's `cache()` so `generateMetadata` and the page component
// below share one fetch per request explicitly — rather than relying on
// Next.js's fetch-level request memoization (which only dedupes when both
// call sites happen to pass identical `timedFetch` options and silently
// stops deduping if either one ever drifts).
const getListing = cache(async (slug: string): Promise<Listing> => {
    const res = await timedFetch(`${process.env.API_URL}/catalog/listings/${slug}/`, {
        next: { revalidate: 60 },
    })
    if (res.status === 404) notFound()
    if (!res.ok) throw new Error(`Failed to fetch listing: ${res.status}`)
    return res.json()
})

function listingProduct(listing: Listing): Product {
    return {
        ...listing.product,
        slug: listing.slug,
        name: listing.display_name,
        base_price: listing.effective_price,
        compare_at_price: listing.compare_at_price_override ?? listing.product.compare_at_price,
        meta_title: listing.meta_title || listing.product.meta_title,
        meta_description: listing.meta_description || listing.product.meta_description,
        category: listing.categories.length > 0 ? listing.categories : listing.product.category,
        is_featured: listing.is_featured,
    }
}

// ── Metadata ───────────────────────────────────────────────────────────────

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
    const { slug } = await params
    const product  = listingProduct(await getListing(slug))
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

function buildOffers(product: Product, canonicalOrigin: string, currency: string) {
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
            priceCurrency: currency,
            lowPrice:      low,
            highPrice:     high,
            offerCount:    variants.length,
            availability,
            url:           `${canonicalOrigin}/shop/products/${product.slug}`,
        }
    }

    const price = prices[0] ?? parseFloat(product.base_price)
    return {
        '@type':        'Offer',
        price,
        priceCurrency: currency,
        availability,
        url:            `${canonicalOrigin}/shop/products/${product.slug}`,
        ...(variants[0]?.sku && { sku: variants[0].sku }),
    }
}

// ── Page ───────────────────────────────────────────────────────────────────

export default async function ProductPage({ params }: PageProps) {
    const { slug } = await params
    const product  = listingProduct(await getListing(slug))
    const storefront = await getStorefront()
    const canonicalOrigin = siteUrl()
    const productUrl = `${canonicalOrigin}/shop/products/${product.slug}`
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
        offers: buildOffers(product, canonicalOrigin, storefront.currency),
    }

    const breadcrumbLd = {
        '@context': 'https://schema.org',
        '@type':    'BreadcrumbList',
        itemListElement: [
            { '@type': 'ListItem', position: 1, name: 'Shop',    item: `${canonicalOrigin}/shop` },
            ...(category
                ? [{
                    '@type': 'ListItem',
                    position: 2,
                    name: category.name,
                    item: category.is_key
                        ? `${canonicalOrigin}/shop/categories/${category.slug}`
                        : `${canonicalOrigin}/shop/collections/${category.slug}`,
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
                dangerouslySetInnerHTML={{ __html: safeJsonLd(jsonLd) }}
            />
            <script
                type="application/ld+json"
                dangerouslySetInnerHTML={{ __html: safeJsonLd(breadcrumbLd) }}
            />
            {/* All interactive UI lives in the client component */}
            <ProductDetails product={product} />
        </>
    )
}

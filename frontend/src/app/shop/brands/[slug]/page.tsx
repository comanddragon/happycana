import type { Metadata } from 'next'
import Image from 'next/image'
import { notFound } from 'next/navigation'
import { QueryClient, dehydrate, HydrationBoundary } from '@tanstack/react-query'
import { ProductsGrid } from '@/components/shop/ProductsGrid'
import { getBrand, getBrands, getCategories, getEffects, getProducts } from '@/lib/catalog.server'
import { qk } from '@/lib/queryKeys'
import { mediaUrl } from '@/lib/utils'
import type { ProductFilterParams } from '@/types'

interface Props {
    params: Promise<{ slug: string }>
    searchParams: Promise<{ page?: string; ordering?: string; search?: string }>
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
    const brand = await getBrand((await params).slug)
    if (!brand) return {}
    const description = brand.meta_description || brand.description || `Shop ${brand.name} products at HappyCana.`
    return {
        title: brand.meta_title || `${brand.name} Products`, description,
        alternates: { canonical: `/shop/brands/${brand.slug}` },
        openGraph: {
            title: brand.meta_title || `${brand.name} Products`, description, type: 'website',
            ...(brand.logo_url && { images: [{ url: brand.logo_url, alt: brand.name }] }),
        },
    }
}

export default async function BrandPage({ params, searchParams }: Props) {
    const brand = await getBrand((await params).slug)
    if (!brand) notFound()
    const query = await searchParams
    const page = Math.max(1, Number(query.page ?? 1) || 1)
    const ordering = query.ordering ?? '-created_at'
    const search = query.search ?? ''
    const filters: ProductFilterParams = { brand: brand.slug, ordering, page, ...(search && { search }) }
    const queryClient = new QueryClient()
    await Promise.all([
        queryClient.prefetchQuery({ queryKey: qk.products(filters), queryFn: () => getProducts(filters, { revalidate: false }) }),
        queryClient.prefetchQuery({ queryKey: qk.categories(), queryFn: getCategories }),
        queryClient.prefetchQuery({ queryKey: qk.brands(), queryFn: getBrands }),
        queryClient.prefetchQuery({ queryKey: qk.effects(), queryFn: getEffects }),
    ])
    const siteUrl = process.env.NEXT_PUBLIC_FRONTEND_URL ?? ''
    const schema = {
        '@context': 'https://schema.org', '@type': 'Brand', name: brand.name,
        url: `${siteUrl}/shop/brands/${brand.slug}`, ...(brand.logo_url && { logo: brand.logo_url }),
        ...(brand.description && { description: brand.description }),
    }
    return (
        <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
            <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }} />
            <header className="mb-8 flex max-w-2xl items-center gap-5">
                {brand.logo_url && <Image src={mediaUrl(brand.logo_url)!} alt={`${brand.name} logo`} width={96} height={64} className="h-16 w-24 rounded-lg bg-white object-contain p-2" />}
                <div><p className="mb-2 font-hc-mono text-xs uppercase tracking-[0.12em] text-hc-canopy-3">Brand</p><h1 className="font-hc-display text-3xl font-medium text-hc-ink">{brand.name}</h1></div>
            </header>
            {brand.description && <p className="mb-8 max-w-2xl text-hc-ink-soft">{brand.description}</p>}
            <HydrationBoundary state={dehydrate(queryClient)}>
                <ProductsGrid initialBrand={brand.slug} initialOrdering={ordering} initialSearch={search} initialPage={page} basePath={`/shop/brands/${brand.slug}`} />
            </HydrationBoundary>
        </div>
    )
}

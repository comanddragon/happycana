import type { Metadata } from 'next'
import { notFound } from 'next/navigation'
import { QueryClient, dehydrate, HydrationBoundary } from '@tanstack/react-query'
import { ProductsGrid } from '@/components/shop/ProductsGrid'
import { getBrands, getCategories, getCollection, getCollectionProducts, getEffects } from '@/lib/catalog.server'
import { qk } from '@/lib/queryKeys'
import type { ProductFilterParams } from '@/types'

interface PageProps {
    params: Promise<{ slug: string }>
    searchParams: Promise<{ page?: string; ordering?: string; search?: string }>
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
    const { slug } = await params
    const collection = await getCollection(slug)
    if (!collection) return {}
    const description = collection.meta_description || collection.description || `Shop the ${collection.name} collection.`
    return {
        title: collection.meta_title || collection.name,
        description,
        alternates: { canonical: `/shop/collections/${collection.slug}` },
    }
}

export default async function CollectionPage({ params, searchParams }: PageProps) {
    const { slug } = await params
    const query = await searchParams
    const collection = await getCollection(slug)
    if (!collection) notFound()

    const page = Math.max(1, Number(query.page ?? '1') || 1)
    const ordering = query.ordering ?? '-created_at'
    const search = query.search ?? ''
    const filters: ProductFilterParams = {
        category: collection.slug,
        ordering,
        page,
        ...(search && { search }),
    }
    const siteUrl = process.env.NEXT_PUBLIC_FRONTEND_URL ?? ''
    const schema = {
        '@context': 'https://schema.org', '@type': 'CollectionPage', name: collection.name,
        description: collection.meta_description || collection.description,
        url: `${siteUrl}/shop/collections/${collection.slug}`,
        isPartOf: { '@type': 'WebSite', name: 'HappyCana', url: siteUrl },
    }
    const queryClient = new QueryClient()
    await Promise.all([
        queryClient.prefetchQuery({
            queryKey: qk.products(filters),
            queryFn: () => getCollectionProducts(collection.slug, filters, { revalidate: false }),
        }),
        queryClient.prefetchQuery({ queryKey: qk.categories(), queryFn: getCategories }),
        queryClient.prefetchQuery({ queryKey: qk.brands(), queryFn: getBrands }),
        queryClient.prefetchQuery({ queryKey: qk.effects(), queryFn: getEffects }),
    ])

    return (
        <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
            <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }} />
            <div className="mb-8 max-w-2xl">
                <p className="mb-2 font-hc-mono text-xs uppercase tracking-[0.12em] text-hc-canopy-3">Collection</p>
                <h1 className="font-hc-display text-3xl font-medium text-hc-ink">{collection.name}</h1>
                {collection.description && (
                    <p className="mt-3 text-sm leading-relaxed text-hc-ink-soft">{collection.description}</p>
                )}
            </div>
            <HydrationBoundary state={dehydrate(queryClient)}>
                <ProductsGrid
                    initialCategory={collection.slug}
                    initialOrdering={ordering}
                    initialSearch={search}
                    initialPage={page}
                    basePath={`/shop/collections/${collection.slug}`}
                    showCategoryFilter={false}
                />
            </HydrationBoundary>
        </div>
    )
}

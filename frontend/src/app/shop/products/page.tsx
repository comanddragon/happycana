import { Suspense } from 'react'
import type { Metadata } from 'next'
import { QueryClient, dehydrate, HydrationBoundary } from '@tanstack/react-query'
import { ProductsGrid } from '@/components/shop/ProductsGrid'
import { getProducts, getCategories, getBrands, getEffects } from '@/lib/catalog.server'
import { qk } from '@/lib/queryKeys'
import type { ProductFilterParams } from '@/types'

interface SearchParams {
    category?: string
    ordering?: string
    search?: string
    page?: string
    brand?: string
    cannabis_type?: string
    effect?: string
    min_thc?: string
    in_stock?: string
}

interface PageProps {
    searchParams: Promise<SearchParams>
}

// Mirrors ProductsGrid's own filter derivation exactly (see the useProducts()
// call there). The query key prefetched here has to structurally match the
// one useProducts() builds client-side, or hydration misses silently and
// the client just refetches from scratch.
function buildFilters(params: SearchParams): ProductFilterParams {
    const category     = params.category ?? ''
    const ordering     = params.ordering ?? '-created_at'
    const search       = params.search ?? ''
    const brand        = params.brand ?? ''
    const cannabisType = params.cannabis_type ?? ''
    const effect       = params.effect ?? ''
    const minThc       = params.min_thc ?? ''
    const inStock      = params.in_stock === 'true'
    const page         = Number(params.page ?? '1')

    return {
        ...(category && { category }),
        ...(brand && { brand }),
        ...(cannabisType && { cannabis_type: cannabisType }),
        ...(effect && { effect }),
        ...(minThc && { min_thc: Number(minThc) }),
        ...(inStock && { in_stock: true }),
        ordering,
        ...(search && { search }),
        page,
    }
}

export async function generateMetadata({ searchParams }: PageProps): Promise<Metadata> {
    const params   = await searchParams
    const category = params.category ?? ''

    return {
        title:       category ? `${category} Products` : 'All Products',
        description: `Browse ${category || 'all'} products. Filter by price, category, and availability.`,
    }
}

export default async function ProductsPage({ searchParams }: PageProps) {
    const params  = await searchParams
    const filters = buildFilters(params)

    // A throwaway QueryClient just for this request's prefetch — not the
    // app's shared client, which only exists in the browser (see
    // components/providers/providers.tsx).
    const queryClient = new QueryClient()

    await Promise.all([
        // Filter combinations are effectively unbounded, so cache the
        // fetch briefly rather than for the full hour the homepage uses
        // for its handful of fixed queries.
        queryClient.prefetchQuery({
            queryKey: qk.products(filters),
            queryFn:  () => getProducts(filters, { revalidate: 60 }),
        }),
        queryClient.prefetchQuery({ queryKey: qk.categories(), queryFn: getCategories }),
        queryClient.prefetchQuery({ queryKey: qk.brands(),     queryFn: getBrands }),
        queryClient.prefetchQuery({ queryKey: qk.effects(),    queryFn: getEffects }),
    ])

    return (
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-10">
            <div className="mb-8">
                <h1 className="font-hc-display text-3xl font-medium text-hc-ink">
                    {params.category ? `${params.category} Products` : 'All Products'}
                </h1>
            </div>
            <HydrationBoundary state={dehydrate(queryClient)}>
                <Suspense fallback={<div className="h-96 animate-pulse rounded-2xl bg-hc-paper-2" />}>
                    <ProductsGrid
                        initialCategory={params.category ?? ''}
                        initialOrdering={params.ordering ?? '-created_at'}
                        initialSearch={params.search ?? ''}
                        initialPage={Number(params.page ?? '1')}
                    />
                </Suspense>
            </HydrationBoundary>
        </div>
    )
}

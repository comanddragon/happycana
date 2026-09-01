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

// Title-case a slug/category param for display: "flower" -> "Flower",
// "pre-rolls" -> "Pre Rolls". Best-effort formatting for a raw URL param,
// not a lookup against the real Category name.
function formatCategoryLabel(value: string): string {
    return value
        .replace(/[-_]+/g, ' ')
        .split(' ')
        .filter(Boolean)
        .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
        .join(' ')
}

export async function generateMetadata({ searchParams }: PageProps): Promise<Metadata> {
    const params   = await searchParams
    const category = params.category ?? ''
    const label    = category ? formatCategoryLabel(category) : ''

    // Faceted/sorted/paginated variants of this URL are all the same
    // underlying listing for search-engine purposes — point every variant's
    // canonical at the unfiltered base URL (or the category-only URL, so a
    // real category landing page isn't diluted by ordering/page params).
    const canonicalPath = category
        ? `/shop/products?category=${encodeURIComponent(category)}`
        : '/shop/products'

    return {
        title:       label ? `${label} Products` : 'All Products',
        description: `Browse ${label || 'all'} products. Filter by price, category, and availability.`,
        alternates: {
            canonical: canonicalPath,
        },
    }
}

export default async function ProductsPage({ searchParams }: PageProps) {
    const params  = await searchParams
    const filters = buildFilters(params)

    const queryClient = new QueryClient()

    await Promise.all([
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
                    {params.category ? `${formatCategoryLabel(params.category)} Products` : 'All Products'}
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
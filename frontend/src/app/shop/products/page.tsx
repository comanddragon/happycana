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

// The category segment of the URL is a slug (e.g. "flower"), not a display
// name, so this looks the real name up against the category list. Falls
// back to a humanized version of the slug (hyphens -> spaces, title case)
// if the slug doesn't match anything, so metadata never renders a raw,
// lowercase slug like "flower Products".
function humanize(slug: string): string {
    return slug
        .split('-')
        .filter(Boolean)
        .map(w => w[0].toUpperCase() + w.slice(1))
        .join(' ')
}

export async function generateMetadata({ searchParams }: PageProps): Promise<Metadata> {
    const params       = await searchParams
    const categorySlug = params.category ?? ''

    let categoryName = ''
    if (categorySlug) {
        const categories = await getCategories()
        categoryName = categories.find(c => c.slug === categorySlug)?.name ?? humanize(categorySlug)
    }

    // Faceted navigation (sort/search/page/brand/effect/etc.) produces many
    // crawlable URL variants of substantially the same content. Canonicalize
    // everything back to the base listing — bare /shop/products, or
    // /shop/products?category=X when a category is set — so ranking signals
    // consolidate onto one URL per category instead of splitting across
    // every filter/sort combination.
    const canonical = categorySlug
        ? `/shop/products?category=${encodeURIComponent(categorySlug)}`
        : '/shop/products'

    return {
        title:       categoryName ? `${categoryName} Products` : 'All Products',
        description: `Browse ${categoryName || 'all'} products. Filter by price, category, and availability.`,
        alternates: { canonical },
    }
}

export default async function ProductsPage({ searchParams }: PageProps) {
    const params  = await searchParams
    const filters = buildFilters(params)

    const queryClient = new QueryClient()

    const [, categories] = await Promise.all([
        queryClient.prefetchQuery({
            queryKey: qk.products(filters),
            queryFn:  () => getProducts(filters, { revalidate: 60 }),
        }),
        queryClient.fetchQuery({ queryKey: qk.categories(), queryFn: getCategories }),
        queryClient.prefetchQuery({ queryKey: qk.brands(),  queryFn: getBrands }),
        queryClient.prefetchQuery({ queryKey: qk.effects(), queryFn: getEffects }),
    ])

    const categoryName = params.category
        ? categories.find(c => c.slug === params.category)?.name ?? humanize(params.category)
        : ''

    return (
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-10">
            <div className="mb-8">
                <h1 className="font-hc-display text-3xl font-medium text-hc-ink">
                    {categoryName ? `${categoryName} Products` : 'All Products'}
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
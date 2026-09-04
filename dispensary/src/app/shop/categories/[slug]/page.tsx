import type { Metadata } from 'next'
import { notFound } from 'next/navigation'
import { QueryClient, dehydrate, HydrationBoundary } from '@tanstack/react-query'
import { ProductsGrid } from '@/components/shop/ProductsGrid'
import { getBrands, getCategories, getCategory, getEffects, getProducts } from '@/lib/catalog.server'
import { qk } from '@/lib/queryKeys'
import type { ProductFilterParams } from '@/types'

interface Props {
    params: Promise<{ slug: string }>
    searchParams: Promise<{ page?: string; ordering?: string; search?: string }>
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
    const category = await getCategory((await params).slug)
    if (!category || !category.is_key) return {}
    const description = category.meta_description || category.description ||
        `Shop ${category.name.toLowerCase()} products from trusted brands at HappyCana.`
    return {
        title: category.meta_title || `${category.name} Products`,
        description,
        alternates: { canonical: `/shop/categories/${category.slug}` },
        openGraph: { title: category.meta_title || `${category.name} Products`, description, type: 'website' },
    }
}

export default async function CategoryPage({ params, searchParams }: Props) {
    const category = await getCategory((await params).slug)
    if (!category || !category.is_key) notFound()
    const query = await searchParams
    const page = Math.max(1, Number(query.page ?? 1) || 1)
    const ordering = query.ordering ?? '-created_at'
    const search = query.search ?? ''
    const filters: ProductFilterParams = { category: category.slug, ordering, page, ...(search && { search }) }
    const queryClient = new QueryClient()
    await Promise.all([
        queryClient.prefetchQuery({ queryKey: qk.products(filters), queryFn: () => getProducts(filters, { revalidate: false }) }),
        queryClient.prefetchQuery({ queryKey: qk.categories(), queryFn: getCategories }),
        queryClient.prefetchQuery({ queryKey: qk.brands(), queryFn: getBrands }),
        queryClient.prefetchQuery({ queryKey: qk.effects(), queryFn: getEffects }),
    ])
    const siteUrl = process.env.NEXT_PUBLIC_FRONTEND_URL ?? ''
    const schema = {
        '@context': 'https://schema.org', '@type': 'CollectionPage', name: `${category.name} Products`,
        description: category.meta_description || category.description,
        url: `${siteUrl}/shop/categories/${category.slug}`,
        isPartOf: { '@type': 'WebSite', name: 'HappyCana', url: siteUrl },
    }
    return (
        <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
            <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }} />
            <header className="mb-8 max-w-2xl">
                <p className="mb-2 font-hc-mono text-xs uppercase tracking-[0.12em] text-hc-canopy-3">Category</p>
                <h1 className="font-hc-display text-3xl font-medium text-hc-ink">{category.name}</h1>
                {category.description && <p className="mt-3 text-hc-ink-soft">{category.description}</p>}
            </header>
            <HydrationBoundary state={dehydrate(queryClient)}>
                <ProductsGrid initialCategory={category.slug} initialOrdering={ordering} initialSearch={search} initialPage={page} basePath={`/shop/categories/${category.slug}`} showCategoryFilter={false} />
            </HydrationBoundary>
        </div>
    )
}

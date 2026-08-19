import { Suspense } from 'react'
import type { Metadata } from 'next'
import { ProductsGrid } from '@/components/shop/ProductsGrid'

interface PageProps {
    searchParams: Promise<{
        category?: string
        ordering?: string
        search?: string
        page?: string
    }>
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
    const params = await searchParams

    return (
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-10">
            <div className="mb-8">
                <h1 className="section-heading">
                    {params.category ? `${params.category} Products` : 'All Products'}
                </h1>
            </div>
            <Suspense fallback={<div className="h-96 animate-pulse rounded-2xl bg-surface-100" />}>
                <ProductsGrid
                    initialCategory={params.category ?? ''}
                    initialOrdering={params.ordering ?? '-created_at'}
                    initialSearch={params.search ?? ''}
                    initialPage={Number(params.page ?? '1')}
                />
            </Suspense>
        </div>
    )
}
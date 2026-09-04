// app/(shop)/shop/best-sellers/page.tsx
import { Suspense } from 'react'
import type { Metadata } from 'next'
import { QueryClient, dehydrate, HydrationBoundary } from '@tanstack/react-query'
import { ProductsGrid } from '@/components/shop/ProductsGrid'
import { Faq } from '@/components/support/Faq'
import { CtaBand } from '@/components/home/CtaBand'
import { getProducts, getCategories, getBrands, getEffects } from '@/lib/catalog.server'
import { qk } from '@/lib/queryKeys'

interface SearchParams {
    category?: string
    page?: string
}

interface PageProps {
    searchParams: Promise<SearchParams>
}

const ORDERING = '-units_sold_hint'

export const metadata: Metadata = {
    title: 'Best Sellers',
    description: 'The most popular flower, edibles, vapes, and concentrates on the menu \u2014 ranked by what customers actually reorder.',
    alternates: { canonical: '/shop/best-sellers' },
    openGraph: {
        title: 'Best Sellers | HappyCana',
        description: 'The most popular products on the menu, most-loved first.',
    },
}

export default async function BestSellersPage({ searchParams }: PageProps) {
    const params   = await searchParams
    const category = params.category ?? ''
    const page     = Number(params.page ?? '1')

    const queryClient = new QueryClient()

    await Promise.all([
        queryClient.prefetchQuery({
            queryKey: qk.products({ ...(category && { category }), ordering: ORDERING, page }),
            queryFn:  () => getProducts({ ...(category && { category }), ordering: ORDERING, page }, { revalidate: false }),
        }),
        queryClient.prefetchQuery({ queryKey: qk.categories(), queryFn: getCategories }),
        queryClient.prefetchQuery({ queryKey: qk.brands(),     queryFn: getBrands }),
        queryClient.prefetchQuery({ queryKey: qk.effects(),    queryFn: getEffects }),
    ])

    return (
        <div className="bg-hc-paper">
            <section className="relative overflow-hidden bg-[radial-gradient(120%_90%_at_50%_0%,var(--color-hc-canopy-3),var(--color-hc-canopy)_55%,var(--color-hc-canopy-2))] px-7 py-16 text-hc-paper sm:py-20">
                <div
                    aria-hidden
                    className="pointer-events-none absolute left-1/2 top-[-30%] h-[600px] w-[600px] -translate-x-1/2 rounded-full blur-[10px]"
                    style={{ background: 'radial-gradient(circle, rgba(200,121,46,.3), transparent 62%)' }}
                />
                <div className="relative mx-auto max-w-[1180px]">
                    <div className="mb-4 inline-flex items-center gap-2 font-hc-mono text-xs uppercase tracking-[0.12em] text-hc-amber-light before:h-px before:w-3.5 before:bg-current before:opacity-50">
                        Crowd favorites
                    </div>
                    <h1 className="font-hc-display text-[34px] font-normal leading-[1.08] tracking-tight sm:text-5xl">
                        Best Sellers
                    </h1>
                    <p className="mt-4 max-w-lg text-[16px] leading-relaxed text-hc-sage">
                        The products customers reorder most, ranked by real sales — not sponsored placement.
                        A safe starting point if you&rsquo;re not sure where to begin.
                    </p>
                </div>
            </section>

            <div className="mx-auto max-w-7xl px-4 py-14 sm:px-6 lg:px-8">
                <HydrationBoundary state={dehydrate(queryClient)}>
                    <Suspense fallback={<div className="h-96 animate-pulse rounded-2xl bg-hc-paper-2" />}>
                        <ProductsGrid
                            initialCategory={category}
                            initialOrdering={ORDERING}
                            initialPage={page}
                            basePath="/shop/best-sellers"
                        />
                    </Suspense>
                </HydrationBoundary>
            </div>

            <div className="mx-auto max-w-3xl px-4 pb-20 sm:px-6">
                <Faq
                    title="Best sellers FAQ"
                    items={[
                        {
                            q: 'How is the best sellers list ranked?',
                            a: 'By units actually sold, not by margin or promotion \u2014 it\u2019s a straightforward reflection of what customers buy and reorder most.',
                        },
                        {
                            q: 'Which cannabinoid products are best for beginners?',
                            a: 'A well-tested, moderate-potency flower or a small pre-roll is a reasonable starting point \u2014 see the beginner\u2019s dosing guide in Learn for how to pace your first sessions.',
                        },
                        {
                            q: 'Does the list update over time?',
                            a: 'Yes \u2014 it reflects recent sales, so it shifts as new products gain traction rather than staying fixed to the same handful indefinitely.',
                        },
                    ]}
                />
            </div>

            <CtaBand
                heading="Not sure where to start?"
                subheading="These are the products customers come back for."
                href="/shop/products?ordering=-units_sold_hint"
                label="Browse all products"
            />
        </div>
    )
}

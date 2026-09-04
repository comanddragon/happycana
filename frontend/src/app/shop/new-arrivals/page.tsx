// app/(shop)/shop/new-arrivals/page.tsx
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

const ORDERING = '-created_at'

export const metadata: Metadata = {
    title: 'New Arrivals',
    description: 'The newest flower, edibles, vapes, and concentrates to land on the menu \u2014 every batch lab-tested before it\u2019s listed.',
    alternates: { canonical: '/shop/new-arrivals' },
    openGraph: {
        title: 'New Arrivals | HappyCana',
        description: 'The newest products on the menu, freshest batches first.',
    },
}

export default async function NewArrivalsPage({ searchParams }: PageProps) {
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
                        Fresh batch
                    </div>
                    <h1 className="font-hc-display text-[34px] font-normal leading-[1.08] tracking-tight sm:text-5xl">
                        New Arrivals
                    </h1>
                    <p className="mt-4 max-w-lg text-[16px] leading-relaxed text-hc-sage">
                        The newest lots to hit the menu, newest first. Every batch is third-party tested before
                        it&rsquo;s listed \u2014 nothing goes up without a lab result behind it.
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
                            basePath="/shop/new-arrivals"
                        />
                    </Suspense>
                </HydrationBoundary>
            </div>

            <div className="mx-auto max-w-3xl px-4 pb-20 sm:px-6">
                <Faq
                    title="New arrivals FAQ"
                    items={[
                        {
                            q: 'How often does the new arrivals list update?',
                            a: 'As soon as a new batch clears lab testing and goes live \u2014 there\u2019s no fixed schedule, so it\u2019s worth checking back regularly if you like to try the freshest drops first.',
                        },
                        {
                            q: 'Are new arrivals lab-tested before they\u2019re listed?',
                            a: 'Yes. Every batch is independently tested before it appears here, the same as the rest of the catalog \u2014 being new doesn\u2019t skip that step.',
                        },
                        {
                            q: 'Can I filter new arrivals by category?',
                            a: 'Yes \u2014 use the category filter above to narrow the list down to flower, edibles, vapes, or concentrates.',
                        },
                    ]}
                />
            </div>

            <CtaBand
                heading="Don\u2019t want to miss the next drop?"
                subheading="New batches ship for same-day pickup or next-day delivery."
                href="/shop/products?ordering=-created_at"
                label="Browse all products"
            />
        </div>
    )
}

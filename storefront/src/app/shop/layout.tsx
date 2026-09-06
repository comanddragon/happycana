// app/(shop)/layout.tsx
import React from "react";
import type { Metadata } from 'next'
import { QueryClient, dehydrate, HydrationBoundary } from '@tanstack/react-query'
import { getCategories, getBrands, getEffects } from '@/lib/catalog.server'
import { qk } from '@/lib/queryKeys'
import { DEFAULT_STOREFRONT_NAME } from '@/lib/storefront'
import { getStorefront } from '@/lib/storefront.server'

export async function generateMetadata(): Promise<Metadata> {
    const storefront = await getStorefront()
    const peptides = storefront.kind === 'peptides'
    return {
        title: {
            default: peptides ? `${storefront.name} — Research Catalog` : `${DEFAULT_STOREFRONT_NAME} — Shop the Menu`,
            template: `%s | ${storefront.name || DEFAULT_STOREFRONT_NAME}`,
        },
        description: peptides
            ? 'Browse source-traceable research compounds by concentration and format.'
            : 'Shop Flower, edibles, and concentrates from small-batch growers, third-party tested and delivered same-day.',
    }
}

export default async function ShopLayout({ children }: { children: React.ReactNode }) {
    // Categories/brands/effects don't vary by page or filters, so they're
    // prefetched once here instead of on every products-page navigation.
    // Next's fetch data cache (revalidate: 3600 in catalog.server.ts) keeps
    // this cheap regardless.
    const queryClient = new QueryClient()

    await Promise.all([
        queryClient.prefetchQuery({ queryKey: qk.categories(), queryFn: getCategories }),
        queryClient.prefetchQuery({ queryKey: qk.brands(),     queryFn: getBrands }),
        queryClient.prefetchQuery({ queryKey: qk.effects(),    queryFn: getEffects }),
    ])

    return (
        <div className="font-hc-body bg-hc-paper min-h-screen flex flex-col">
            <HydrationBoundary state={dehydrate(queryClient)}>
                <main className="flex-1">{children}</main>
            </HydrationBoundary>
        </div>
    )
}

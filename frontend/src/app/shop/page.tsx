// app/(shop)/shop/page.tsx  — NO 'use client'
import Link from 'next/link'
import { ArrowRight, Truck, RotateCcw, ShieldCheck, FlaskConical } from 'lucide-react'
import { ProductCard } from '@/components/shop/ProductCard'
import { CategoryGrid } from '@/components/shop/CategoryGrid'
import { BrandStrip } from '@/components/shop/BrandStrip'
import { Reveal } from '@/components/home/Reveal'
import { CtaBand } from '@/components/home/CtaBand'
import { Category, Product, Effect } from "@/types"
import type { Metadata } from "next"

async function getCategories(): Promise<Category[]> {
    try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/catalog/categories/`, {
            next: { revalidate: 3600 }
        })
        if (!res.ok) return []
        const data = await res.json()
        return Array.isArray(data) ? data : (data?.results ?? [])
    } catch {
        return []
    }
}

async function getProducts(query: string): Promise<{ results: Product[] }> {
    try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/catalog/products/?${query}`, {
            next: { revalidate: 3600 }
        })
        if (!res.ok) return { results: [] }
        const data = await res.json()
        return Array.isArray(data?.results) ? data : { results: [] }
    } catch {
        return { results: [] }
    }
}

const getNewArrivals  = () => getProducts('ordering=-created_at&page_size=4')
const getBestSellers  = () => getProducts('ordering=-units_sold_hint&page_size=4')

async function getEffects(): Promise<Effect[]> {
    try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/catalog/effects/`, {
            next: { revalidate: 3600 }
        })
        if (!res.ok) return []
        const data = await res.json()
        return Array.isArray(data) ? data : (data?.results ?? [])
    } catch {
        return []
    }
}

export const metadata: Metadata = {
    title: 'Shop the Menu | HappyCana',
    description: 'Flower, edibles, vapes, and concentrates from small-batch growers, third-party tested and ready for same-day pickup or delivery.',
    openGraph: {
        title: 'Shop the Menu | HappyCana',
        description: 'Flower, edibles, vapes, and concentrates — every lot lab-tested twice.',
    }
}

export default async function ShopPage() {
    const [categories, newArrivals, bestSellers, effects] = await Promise.all([
        getCategories(),
        getNewArrivals(),
        getBestSellers(),
        getEffects(),
    ])

    return (
        <div className="bg-hc-paper">

            {/* Header band */}
            <section className="relative overflow-hidden bg-[radial-gradient(120%_90%_at_50%_0%,var(--color-hc-canopy-3),var(--color-hc-canopy)_55%,var(--color-hc-canopy-2))] px-7 py-16 text-hc-paper sm:py-20">
                <div
                    aria-hidden
                    className="pointer-events-none absolute left-1/2 top-[-30%] h-[600px] w-[600px] -translate-x-1/2 rounded-full blur-[10px]"
                    style={{ background: 'radial-gradient(circle, rgba(200,121,46,.3), transparent 62%)' }}
                />
                <div className="relative mx-auto max-w-[1180px]">
                    <div className="mb-4 inline-flex items-center gap-2 font-hc-mono text-xs uppercase tracking-[0.12em] text-hc-amber-light before:h-px before:w-3.5 before:bg-current before:opacity-50">
                        Today&rsquo;s menu
                    </div>
                    <h1 className="font-hc-display text-[34px] font-normal leading-[1.08] tracking-tight sm:text-5xl">
                        Shop by category
                    </h1>
                    <p className="mt-4 max-w-lg text-[16px] leading-relaxed text-hc-sage">
                        Explore our full range of flower, edibles, vapes, and concentrates — every batch third-party tested before it reaches you.
                    </p>
                </div>
            </section>

            <div className="mx-auto max-w-[1180px] px-7 py-16 space-y-16">

                {/* Category grid */}
                <Reveal>
                    <CategoryGrid />
                </Reveal>

                {/* All categories list with subcategories */}
                {categories.length > 0 && (
                    <Reveal>
                        <div className="mb-7 inline-flex items-center gap-2 font-hc-mono text-xs uppercase tracking-[0.12em] text-hc-sage-dim before:h-px before:w-3.5 before:bg-current before:opacity-50">
                            Browse
                        </div>
                        <h2 className="font-hc-display text-2xl font-medium text-hc-ink mb-6">All Departments</h2>
                        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                            {categories.map((cat: Category) => (
                                <div key={cat.id} className="rounded-2xl border border-hc-ink/[0.08] bg-white p-5 transition-colors hover:border-hc-amber">
                                    <Link
                                        href={`/shop/products?category=${cat.slug}`}
                                        className="group flex items-center justify-between font-hc-display text-lg font-medium text-hc-ink transition-colors hover:text-hc-amber-dim"
                                    >
                                        {cat.name}
                                        <ArrowRight className="h-4 w-4 text-hc-ink-soft transition-colors group-hover:text-hc-amber-dim" />
                                    </Link>
                                    {cat.children && cat.children.length > 0 && (
                                        <div className="mt-3 flex flex-wrap gap-2">
                                            {cat.children.map(child => (
                                                <Link
                                                    key={child.id}
                                                    href={`/shop/products?category=${child.slug}`}
                                                    className="rounded-full bg-hc-paper-2 px-2.5 py-1 font-hc-mono text-[11px] text-hc-ink-soft transition-colors hover:bg-hc-amber-light/20 hover:text-hc-amber-dim"
                                                >
                                                    {child.name}
                                                </Link>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </Reveal>
                )}

                {/* Shop by effect */}
                {effects.length > 0 && (
                    <Reveal>
                        <div className="mb-7 inline-flex items-center gap-2 font-hc-mono text-xs uppercase tracking-[0.12em] text-hc-sage-dim before:h-px before:w-3.5 before:bg-current before:opacity-50">
                            Mood &amp; effect
                        </div>
                        <h2 className="font-hc-display text-2xl font-medium text-hc-ink mb-6">Shop by Effect</h2>
                        <div className="flex flex-wrap gap-2.5">
                            {effects.map((effect: Effect) => (
                                <Link
                                    key={effect.id}
                                    href={`/shop/products?effect=${effect.slug}`}
                                    className="rounded-full border border-hc-ink/[0.08] bg-white px-4.5 py-2.5 font-hc-mono text-xs uppercase tracking-wide text-hc-ink-soft transition-colors hover:border-hc-amber hover:bg-hc-amber-light/15 hover:text-hc-amber-dim"
                                >
                                    {effect.name}
                                </Link>
                            ))}
                        </div>
                    </Reveal>
                )}

                {/* Shop by brand */}
                <Reveal>
                    <div className="mb-7 inline-flex items-center gap-2 font-hc-mono text-xs uppercase tracking-[0.12em] text-hc-sage-dim before:h-px before:w-3.5 before:bg-current before:opacity-50">
                        Brands
                    </div>
                    <h2 className="font-hc-display text-2xl font-medium text-hc-ink mb-6">Shop by Brand</h2>
                    <BrandStrip />
                </Reveal>

                {/* Bestsellers */}
                {bestSellers.results.length > 0 && (
                    <Reveal>
                        <div className="flex items-end justify-between mb-7">
                            <div>
                                <div className="mb-2 inline-flex items-center gap-2 font-hc-mono text-xs uppercase tracking-[0.12em] text-hc-sage-dim before:h-px before:w-3.5 before:bg-current before:opacity-50">
                                    Crowd favorites
                                </div>
                                <h2 className="font-hc-display text-2xl font-medium text-hc-ink">Best Sellers</h2>
                            </div>
                            <Link
                                href="/shop/products?ordering=-units_sold_hint"
                                className="inline-flex items-center gap-1.5 font-hc-mono text-xs uppercase tracking-wide text-hc-amber-dim hover:text-hc-amber transition-colors"
                            >
                                See all <ArrowRight className="h-3.5 w-3.5" />
                            </Link>
                        </div>
                        <div className="grid grid-cols-2 gap-x-5 gap-y-8 sm:grid-cols-4">
                            {bestSellers.results.map((product: Product) => (
                                <ProductCard key={product.id} product={product} />
                            ))}
                        </div>
                    </Reveal>
                )}

                {/* New arrivals */}
                {newArrivals.results.length > 0 && (
                    <Reveal>
                        <div className="flex items-end justify-between mb-7">
                            <div>
                                <div className="mb-2 inline-flex items-center gap-2 font-hc-mono text-xs uppercase tracking-[0.12em] text-hc-sage-dim before:h-px before:w-3.5 before:bg-current before:opacity-50">
                                    Fresh batch
                                </div>
                                <h2 className="font-hc-display text-2xl font-medium text-hc-ink">New Arrivals</h2>
                            </div>
                            <Link
                                href="/shop/products?ordering=-created_at"
                                className="inline-flex items-center gap-1.5 font-hc-mono text-xs uppercase tracking-wide text-hc-amber-dim hover:text-hc-amber transition-colors"
                            >
                                See all <ArrowRight className="h-3.5 w-3.5" />
                            </Link>
                        </div>
                        <div className="grid grid-cols-2 gap-x-5 gap-y-8 sm:grid-cols-4">
                            {newArrivals.results.map((product: Product) => (
                                <ProductCard key={product.id} product={product} />
                            ))}
                        </div>
                    </Reveal>
                )}

            </div>

            {/* Trust band */}
            <div className="border-y border-hc-ink/[0.06] bg-hc-paper-2">
                <div className="mx-auto max-w-[1180px] px-7 py-12 grid grid-cols-2 gap-6 sm:grid-cols-4">
                    {[
                        { icon: FlaskConical, title: '12-panel lab tested', text: 'Every batch, twice' },
                        { icon: Truck,        title: 'Same-day pickup',     text: 'Ready in ~20 min' },
                        { icon: RotateCcw,    title: '30-day returns',      text: 'No questions asked' },
                        { icon: ShieldCheck,  title: 'Licensed retailer',   text: 'State-compliant, always' },
                    ].map(({ icon: Icon, title, text }) => (
                        <div key={title} className="flex flex-col items-center gap-2 text-center">
                            <div className="flex h-11 w-11 items-center justify-center rounded-full bg-hc-canopy">
                                <Icon className="h-4.5 w-4.5 text-hc-amber-light" />
                            </div>
                            <p className="font-hc-display text-sm font-medium text-hc-ink">{title}</p>
                            <p className="font-hc-mono text-[11px] tracking-wide text-hc-ink-soft">{text}</p>
                        </div>
                    ))}
                </div>
            </div>

            <CtaBand
                heading="Can’t decide? We’ll walk you through it."
                subheading="Same-day pickup, next-day delivery, every lot tested twice."
                href="/shop/products"
                label="Browse all products"
            />
        </div>
    )
}
// app/(shop)/shop/page.tsx  — NO 'use client'
import { Suspense } from 'react'
import Link from 'next/link'
import { ArrowRight, Truck, RotateCcw, ShieldCheck, FlaskConical } from 'lucide-react'
import { ProductCard } from '@/components/shop/ProductCard'
import { CategoryGrid, CategoryGridSkeleton } from '@/components/shop/CategoryGrid'
import { BrandStrip, BrandStripSkeleton } from '@/components/shop/BrandStrip'
import { Reveal } from '@/components/home/Reveal'
import { CtaBand } from '@/components/home/CtaBand'
import { getProducts, getEffects, getCategories, getBrands } from '@/lib/catalog.server'
import { Product, Effect } from "@/types"
import type { Metadata } from "next"

const getNewArrivals = () => getProducts({ ordering: '-created_at', page_size: 4 })
const getBestSellers = () => getProducts({ ordering: '-units_sold_hint', page_size: 4 })

export const metadata: Metadata = {
    title: 'Shop the Menu | HappyCana',
    description: 'Flower, edibles, vapes, and concentrates from small-batch growers, third-party tested and ready for same-day pickup or delivery.',
    openGraph: {
        title: 'Shop the Menu | HappyCana',
        description: 'Flower, edibles, vapes, and concentrates — every lot lab-tested twice.',
    }
}

function SectionHeading({ eyebrow, title }: { eyebrow: string; title: string }) {
    return (
        <>
            <div className="mb-7 inline-flex items-center gap-2 font-hc-mono text-xs uppercase tracking-[0.12em] text-hc-canopy-3 before:h-px before:w-3.5 before:bg-current before:opacity-50">
                {eyebrow}
            </div>
            <h2 className="font-hc-display text-2xl font-medium text-hc-ink mb-6">{title}</h2>
        </>
    )
}

function ProductGridSkeleton() {
    return (
        <div className="grid grid-cols-2 gap-x-5 gap-y-8 sm:grid-cols-4">
            {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="aspect-[3/4] animate-pulse rounded-2xl bg-hc-paper-2" />
            ))}
        </div>
    )
}

async function EffectsSection() {
    const effects = await getEffects()
    if (effects.length === 0) return null

    return (
        <Reveal>
            <div className="mb-7 inline-flex items-center gap-2 font-hc-mono text-xs uppercase tracking-[0.12em] text-hc-canopy-3 before:h-px before:w-3.5 before:bg-current before:opacity-50">
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
    )
}

async function CategoryGridSection() {
    const categories = await getCategories()
    if (categories.length === 0) return null

    return (
        <Reveal>
            <SectionHeading eyebrow="Categories" title="Select a Category" />
            <CategoryGrid categories={categories} />
        </Reveal>
    )
}

async function BrandStripSection() {
    const brands = await getBrands()
    if (brands.length === 0) return null

    return (
        <Reveal>
            <SectionHeading eyebrow="Brands" title="Shop by Brand" />
            <BrandStrip brands={brands} />
        </Reveal>
    )
}

async function BestSellersSection() {
    const bestSellers = await getBestSellers()
    if (bestSellers.results.length === 0) return null

    return (
        <Reveal>
            <div className="flex items-end justify-between mb-7">
                <div>
                    <div className="mb-2 inline-flex items-center gap-2 font-hc-mono text-xs uppercase tracking-[0.12em] text-hc-canopy-3 before:h-px before:w-3.5 before:bg-current before:opacity-50">
                        Crowd favorites
                    </div>
                    <h2 className="font-hc-display text-2xl font-medium text-hc-ink">Best Sellers</h2>
                </div>
                <Link
                    href="/shop/best-sellers"
                    className="inline-flex items-center gap-1.5 font-hc-mono text-xs uppercase tracking-wide text-hc-amber-dim hover:text-hc-amber transition-colors"
                >
                    See all <ArrowRight className="h-3.5 w-3.5" />
                </Link>
            </div>
            <div className="grid grid-cols-2 gap-x-5 gap-y-8 sm:grid-cols-4">
                {bestSellers.results.map((product: Product, i: number) => (
                    <ProductCard key={product.id} product={product} priority={i < 4} />
                ))}
            </div>
        </Reveal>
    )
}

async function NewArrivalsSection() {
    const newArrivals = await getNewArrivals()
    if (newArrivals.results.length === 0) return null

    return (
        <Reveal>
            <div className="flex items-end justify-between mb-7">
                <div>
                    <div className="mb-2 inline-flex items-center gap-2 font-hc-mono text-xs uppercase tracking-[0.12em] text-hc-canopy-3 before:h-px before:w-3.5 before:bg-current before:opacity-50">
                        Fresh batch
                    </div>
                    <h2 className="font-hc-display text-2xl font-medium text-hc-ink">New Arrivals</h2>
                </div>
                <Link
                    href="/shop/new-arrivals"
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
    )
}

export default function ShopPage() {
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
                <Suspense fallback={
                    <>
                        <SectionHeading eyebrow="Categories" title="Select a Category" />
                        <CategoryGridSkeleton />
                    </>
                }>
                    <CategoryGridSection />
                </Suspense>

                {/* Shop by effect */}
                <Suspense fallback={null}>
                    <EffectsSection />
                </Suspense>

                {/* Shop by brand */}
                <Suspense fallback={
                    <>
                        <SectionHeading eyebrow="Brands" title="Shop by Brand" />
                        <BrandStripSkeleton />
                    </>
                }>
                    <BrandStripSection />
                </Suspense>

                {/* Bestsellers */}
                <Suspense fallback={<ProductGridSkeleton />}>
                    <BestSellersSection />
                </Suspense>

                {/* New arrivals */}
                <Suspense fallback={<ProductGridSkeleton />}>
                    <NewArrivalsSection />
                </Suspense>

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

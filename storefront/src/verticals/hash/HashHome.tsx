import Link from 'next/link'
import { ArrowRight, Layers3, ShieldCheck, Sparkles } from 'lucide-react'

import { ProductCard } from '@/components/shop/ProductCard'
import { getCategories, getProducts } from '@/lib/catalog.server'
import type { Storefront } from '@/types'

const STANDARDS = [
    { icon: Layers3, title: 'Method first', copy: 'Browse dry sift, static sift, frozen sift, eggs, and traditional plates by process.' },
    { icon: ShieldCheck, title: 'Source retained', copy: 'Every catalog record keeps its original producer and source reference.' },
    { icon: Sparkles, title: 'Drop clarity', copy: 'Weights, availability, and variant pricing are visible before checkout.' },
]

export async function HashHome({ storefront }: { storefront: Storefront }) {
    const [{ results }, categories] = await Promise.all([
        getProducts({ ordering: '-created_at', page_size: 8 }, { revalidate: false }),
        getCategories(),
    ])
    const hashCategories = categories.filter(category => category.is_key).slice(0, 6)

    return (
        <main className="bg-hc-paper text-hc-ink">
            <section className="relative isolate overflow-hidden bg-hc-canopy px-6 py-24 text-hc-paper sm:py-32">
                <div aria-hidden className="absolute inset-0 -z-10 opacity-25 [background-image:radial-gradient(circle_at_20%_20%,var(--color-hc-amber)_0,transparent_32%),radial-gradient(circle_at_80%_70%,var(--color-hc-canopy-3)_0,transparent_38%)]" />
                <div aria-hidden className="absolute inset-0 -z-10 opacity-[.08] [background-image:repeating-linear-gradient(115deg,transparent_0,transparent_22px,#fff_23px,#fff_24px)]" />
                <div className="mx-auto max-w-[1180px]">
                    <p className="font-hc-mono text-xs uppercase tracking-[.22em] text-hc-amber-light">Solventless · sifted · selected</p>
                    <h1 className="mt-6 max-w-4xl font-hc-display text-5xl leading-[.95] tracking-[-.04em] sm:text-7xl">
                        Resin craft,<br /><em className="text-hc-amber-light">sorted by method.</em>
                    </h1>
                    <p className="mt-7 max-w-xl text-base leading-7 text-hc-sage sm:text-lg">
                        {storefront.name} is a focused hash catalog built around process, provenance, weight, and current availability.
                    </p>
                    <div className="mt-9 flex flex-wrap gap-3">
                        <Link href="/shop/products" className="inline-flex items-center gap-2 rounded-full bg-hc-amber px-6 py-3.5 text-sm font-semibold text-hc-canopy-2 transition hover:-translate-y-0.5">
                            Enter the hash room <ArrowRight className="h-4 w-4" />
                        </Link>
                        <Link href="/shop" className="rounded-full border border-hc-paper/20 px-6 py-3.5 text-sm font-semibold transition hover:bg-hc-paper/5">Browse methods</Link>
                    </div>
                </div>
            </section>

            <section className="px-6 py-14">
                <div className="mx-auto grid max-w-[1180px] gap-px overflow-hidden rounded-2xl border border-hc-ink/10 bg-hc-ink/10 md:grid-cols-3">
                    {STANDARDS.map(({ icon: Icon, title, copy }) => (
                        <article key={title} className="bg-white p-8">
                            <Icon className="h-6 w-6 text-hc-amber-dim" />
                            <h2 className="mt-5 font-hc-display text-2xl">{title}</h2>
                            <p className="mt-2 text-sm leading-6 text-hc-ink-soft">{copy}</p>
                        </article>
                    ))}
                </div>
            </section>

            {hashCategories.length > 0 && (
                <section className="px-6 pb-10">
                    <div className="mx-auto max-w-[1180px]">
                        <p className="font-hc-mono text-xs uppercase tracking-[.18em] text-hc-amber-dim">Shop the process</p>
                        <div className="mt-5 grid grid-cols-2 gap-3 md:grid-cols-3">
                            {hashCategories.map(category => (
                                <Link key={category.id} href={`/shop/categories/${category.slug}`} className="group border border-hc-ink/10 bg-hc-paper-2 p-5 transition hover:border-hc-amber">
                                    <span className="font-hc-display text-xl group-hover:text-hc-amber-dim">{category.name}</span>
                                    <span className="mt-4 flex items-center gap-1 font-hc-mono text-[10px] uppercase tracking-wider text-hc-ink-soft">View selection <ArrowRight className="h-3 w-3" /></span>
                                </Link>
                            ))}
                        </div>
                    </div>
                </section>
            )}

            <section className="px-6 pb-24 pt-10">
                <div className="mx-auto max-w-[1180px]">
                    <div className="mb-9 flex items-end justify-between gap-4">
                        <div><p className="font-hc-mono text-xs uppercase tracking-[.18em] text-hc-amber-dim">Freshly indexed</p><h2 className="mt-2 font-hc-display text-4xl">Latest hash</h2></div>
                        <Link href="/shop/products" className="flex items-center gap-2 text-sm font-semibold text-hc-amber-dim">View all <ArrowRight className="h-4 w-4" /></Link>
                    </div>
                    <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4 lg:gap-6">
                        {results.map((product, index) => <ProductCard key={product.id} product={product} priority={index < 4} />)}
                    </div>
                </div>
            </section>
        </main>
    )
}

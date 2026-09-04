import Link from 'next/link'
import { ArrowRight } from 'lucide-react'
import { flattenCategories, getFreshCategories } from '@/lib/catalog.server'
import { Reveal } from '@/components/home/Reveal'

export async function HomeCategories() {
    const categories = flattenCategories(await getFreshCategories())
        .filter(category => category.is_key)
        .slice(0, 10)
    if (!categories.length) return null

    const schema = {
        '@context': 'https://schema.org',
        '@type': 'ItemList',
        name: 'Shop cannabis by category',
        itemListElement: categories.map((category, index) => ({
            '@type': 'ListItem',
            position: index + 1,
            name: category.name,
            url: `${process.env.NEXT_PUBLIC_FRONTEND_URL ?? ''}/shop/categories/${category.slug}`,
        })),
    }

    return (
        <section className="bg-hc-paper px-5 py-20 sm:px-7 sm:py-24" aria-labelledby="home-categories-title">
            <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }} />
            <div className="mx-auto max-w-[1180px]">
                <Reveal className="mb-10 flex flex-wrap items-end justify-between gap-5">
                    <div>
                        <p className="font-hc-mono text-xs uppercase tracking-[0.12em] text-hc-sage-dim">Shop the menu</p>
                        <h2 id="home-categories-title" className="mt-2 font-hc-display text-3xl font-normal text-hc-ink sm:text-4xl">Find your format</h2>
                    </div>
                    <Link href="/shop" className="inline-flex items-center gap-1.5 font-hc-mono text-xs uppercase tracking-wide text-hc-amber-dim hover:text-hc-amber">
                        Browse the shop <ArrowRight className="h-3.5 w-3.5" />
                    </Link>
                </Reveal>
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-5">
                    {categories.map(category => (
                        <Link key={category.id} href={`/shop/categories/${category.slug}`} className="group rounded-2xl border border-hc-ink/10 bg-white p-5 transition hover:-translate-y-1 hover:border-hc-amber/60 hover:shadow-lg">
                            <h3 className="font-hc-display text-xl text-hc-ink">{category.name}</h3>
                            <p className="mt-2 text-sm leading-6 text-hc-ink-soft">{category.description}</p>
                            <span className="mt-4 inline-flex items-center gap-1 font-hc-mono text-[10px] uppercase tracking-wide text-hc-amber-dim">Shop category <ArrowRight className="h-3 w-3 transition-transform group-hover:translate-x-1" /></span>
                        </Link>
                    ))}
                </div>
            </div>
        </section>
    )
}

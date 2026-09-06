import Link from 'next/link'
import { ArrowRight, Beaker, FileCheck2, Microscope, Snowflake } from 'lucide-react'
import { ProductCard } from '@/components/shop/ProductCard'
import { getProducts } from '@/lib/catalog.server'
import type { Storefront } from '@/types'

const TRUST = [
    { icon: FileCheck2, title: 'Source traceability', copy: 'Catalog records keep a direct link to their source documentation.' },
    { icon: Beaker, title: 'Research format', copy: 'Concentration and material format are visible before you open a listing.' },
    { icon: Snowflake, title: 'Handling clarity', copy: 'Storage guidance travels with every research compound profile.' },
]

export async function PeptideHome({ storefront }: { storefront: Storefront }) {
    const { results } = await getProducts(
        { ordering: '-created_at', page_size: 8 },
        { revalidate: false },
    )

    return (
        <main className="bg-[#f4f7f6] text-[#10231e]">
            <section className="relative overflow-hidden border-b border-[#19382f]/10 bg-[#071b17] px-6 pb-20 pt-20 text-white sm:pb-28 sm:pt-28">
                <div aria-hidden className="absolute inset-0 opacity-40 [background-image:linear-gradient(rgba(143,211,188,.08)_1px,transparent_1px),linear-gradient(90deg,rgba(143,211,188,.08)_1px,transparent_1px)] [background-size:46px_46px]" />
                <div aria-hidden className="absolute -right-40 -top-40 h-[620px] w-[620px] rounded-full border border-[#83e4c0]/15 shadow-[inset_0_0_100px_rgba(76,220,165,.08)]" />
                <div className="relative mx-auto grid max-w-[1180px] gap-14 lg:grid-cols-[1.15fr_.85fr] lg:items-center">
                    <div>
                        <p className="mb-6 font-hc-mono text-xs uppercase tracking-[.2em] text-[#83e4c0]">Research materials · catalog verified</p>
                        <h1 className="max-w-3xl font-hc-display text-5xl font-medium leading-[.98] tracking-[-.04em] sm:text-7xl">
                            Precision compounds.<br /><em className="text-[#9ee8ce]">Clear provenance.</em>
                        </h1>
                        <p className="mt-7 max-w-xl text-base leading-7 text-[#b9cec7] sm:text-lg">
                            {storefront.name} organizes research peptides by format, concentration, and source documentation—without therapeutic claims or guesswork.
                        </p>
                        <div className="mt-9 flex flex-wrap gap-3">
                            <Link href="/shop/products" className="inline-flex items-center gap-2 rounded-full bg-[#9ee8ce] px-6 py-3.5 text-sm font-semibold text-[#071b17] transition hover:-translate-y-0.5">
                                Browse compounds <ArrowRight className="h-4 w-4" />
                            </Link>
                            <a href="#standards" className="rounded-full border border-white/20 px-6 py-3.5 text-sm font-semibold text-white transition hover:bg-white/5">Our catalog standard</a>
                        </div>
                    </div>
                    <div className="relative mx-auto flex aspect-square w-full max-w-[430px] items-center justify-center">
                        <div className="absolute inset-[8%] rounded-full border border-[#83e4c0]/20" />
                        <div className="absolute inset-[22%] rounded-full border border-dashed border-[#83e4c0]/30" />
                        <div className="absolute h-[52%] w-[38%] rotate-6 rounded-[36px] border border-white/15 bg-gradient-to-b from-white/15 to-white/[.03] p-5 shadow-2xl backdrop-blur">
                            <div className="h-3 w-16 rounded-full bg-[#9ee8ce]/80" />
                            <Microscope className="mx-auto mt-14 h-20 w-20 text-[#9ee8ce]" strokeWidth={1} />
                            <div className="mt-12 border-t border-white/15 pt-3 font-hc-mono text-[10px] uppercase tracking-widest text-[#b9cec7]">Research use only</div>
                        </div>
                    </div>
                </div>
            </section>

            <section id="standards" className="px-6 py-16">
                <div className="mx-auto grid max-w-[1180px] gap-px overflow-hidden rounded-3xl border border-[#19382f]/10 bg-[#19382f]/10 md:grid-cols-3">
                    {TRUST.map(({ icon: Icon, title, copy }) => (
                        <article key={title} className="bg-white p-7 sm:p-9">
                            <Icon className="h-6 w-6 text-[#197052]" />
                            <h2 className="mt-5 font-hc-display text-2xl">{title}</h2>
                            <p className="mt-2 text-sm leading-6 text-[#526a62]">{copy}</p>
                        </article>
                    ))}
                </div>
            </section>

            <section className="px-6 pb-24 pt-8">
                <div className="mx-auto max-w-[1180px]">
                    <div className="mb-10 flex flex-wrap items-end justify-between gap-5">
                        <div>
                            <p className="font-hc-mono text-xs uppercase tracking-[.18em] text-[#197052]">Fresh to the catalog</p>
                            <h2 className="mt-2 font-hc-display text-4xl tracking-tight">Research collection</h2>
                        </div>
                        <Link href="/shop/products" className="inline-flex items-center gap-2 text-sm font-semibold text-[#197052]">View all compounds <ArrowRight className="h-4 w-4" /></Link>
                    </div>
                    {results.length ? (
                        <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4 lg:gap-6">
                            {results.map((product, index) => <ProductCard key={product.id} product={product} priority={index < 4} />)}
                        </div>
                    ) : (
                        <div className="rounded-3xl border border-dashed border-[#19382f]/20 bg-white px-6 py-20 text-center">
                            <Beaker className="mx-auto h-8 w-8 text-[#197052]" />
                            <p className="mt-4 font-hc-display text-2xl">Catalog import ready</p>
                            <p className="mt-2 text-sm text-[#526a62]">Run the peptide catalog importer to publish source-traceable products here.</p>
                        </div>
                    )}
                </div>
            </section>

            <section className="border-y border-[#19382f]/10 bg-[#dff3eb] px-6 py-8 text-center text-sm text-[#34564b]">
                Products are supplied for laboratory research and educational use only. Not for human consumption.
            </section>
        </main>
    )
}

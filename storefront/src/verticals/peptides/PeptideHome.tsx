import Image from 'next/image'
import Link from 'next/link'
import { ArrowRight, FileCheck2, FlaskConical, ScanLine } from 'lucide-react'
import { ProductCard } from '@/components/shop/ProductCard'
import { getCategories, getProducts } from '@/lib/catalog.server'
import type { Storefront } from '@/types'

export async function PeptideHome({ storefront }: { storefront: Storefront }) {
    const [{ results }, categories] = await Promise.all([
        getProducts({ ordering: '-created_at', page_size: 8 }, { revalidate: false }),
        getCategories(),
    ])
    const featured = categories.filter(category => category.is_key).slice(0, 4)
    return (
        <main className="bg-[#f2f6f4] text-hc-ink">
            <section className="relative -mt-[88px] min-h-[780px] overflow-hidden border-b border-emerald-950/10 pt-36">
                <div className="absolute inset-0 opacity-50 [background-image:linear-gradient(rgba(9,45,37,.06)_1px,transparent_1px),linear-gradient(90deg,rgba(9,45,37,.06)_1px,transparent_1px)] [background-size:40px_40px]"/>
                <div className="relative mx-auto grid min-h-[644px] max-w-[1220px] px-6 lg:grid-cols-[.82fr_1.18fr]">
                    <div className="flex flex-col justify-between border-x border-emerald-950/10 bg-[#f2f6f4]/85 p-7 backdrop-blur-sm sm:p-12">
                        <p className="font-hc-mono text-[10px] uppercase tracking-[.25em] text-hc-amber-dim">Axiom / reference series 2026</p>
                        <div>
                            <p className="mb-5 font-hc-mono text-xs text-hc-amber-dim">CATALOGUE 01—{String(results.length).padStart(2,'0')}</p>
                            <h1 className="font-hc-display text-5xl font-semibold leading-[.92] tracking-[-.065em] sm:text-7xl">Research,<br/>without the<br/><span className="text-hc-amber-dim">guesswork.</span></h1>
                            <p className="mt-7 max-w-md text-[15px] leading-7 text-hc-ink-soft">{storefront.name} presents compounds by format, concentration, source, and documentation—designed for fast, exact comparison.</p>
                            <Link href="/shop/products" className="mt-8 inline-flex items-center gap-3 border-b border-hc-ink pb-1 text-sm font-semibold">Open compound index <ArrowRight className="h-4 w-4"/></Link>
                        </div>
                        <div className="grid grid-cols-3 border-t border-emerald-950/15 pt-5 font-hc-mono text-[9px] uppercase tracking-wider text-hc-ink-soft"><span>Traceable</span><span>Cold-chain</span><span>Research only</span></div>
                    </div>
                    <div className="relative min-h-[520px] overflow-hidden bg-[#dbeee7]">
                        <Image src="/editorial/peptide-hero.webp" alt="Research peptide vial in a precision laboratory setting" fill priority sizes="(max-width:1024px) 100vw, 60vw" className="axiom-hero-image object-cover"/>
                        <div className="absolute inset-0 bg-gradient-to-t from-[#06221b]/70 via-transparent to-transparent"/>
                        <div className="absolute bottom-7 left-7 right-7 flex justify-between border-t border-white/40 pt-4 font-hc-mono text-[10px] uppercase tracking-[.18em] text-white"><span>Documented material</span><span>Fig. 01</span></div>
                    </div>
                </div>
            </section>

            {featured.length > 0 && <section className="mx-auto max-w-[1220px] px-6 py-20"><div className="mb-8 flex items-end justify-between"><div><p className="font-hc-mono text-[10px] uppercase tracking-[.22em] text-hc-amber-dim">Compound families</p><h2 className="mt-2 font-hc-display text-4xl font-semibold tracking-[-.045em]">Browse the index</h2></div><Link href="/shop" className="text-sm font-semibold">All families →</Link></div><div className="grid gap-px overflow-hidden border border-emerald-950/10 bg-emerald-950/10 sm:grid-cols-2 lg:grid-cols-4">{featured.map((category,index)=><Link key={category.id} href={`/shop/categories/${category.slug}`} className="group relative aspect-[4/5] overflow-hidden bg-white"><Image src={category.image_url} alt="" fill sizes="(max-width:640px) 100vw, 25vw" className="object-cover transition duration-700 group-hover:scale-105"/><div className="absolute inset-0 bg-gradient-to-t from-[#041d17]/90 via-transparent to-transparent"/><span className="absolute left-5 top-5 font-hc-mono text-[10px] text-white/70">0{index+1}</span><h3 className="absolute bottom-5 left-5 right-5 font-hc-display text-2xl font-semibold text-white">{category.name}</h3></Link>)}</div></section>}

            <section className="bg-[#07231c] px-6 py-20 text-white"><div className="mx-auto max-w-[1220px]"><div className="mb-10 grid gap-6 md:grid-cols-2"><div><p className="font-hc-mono text-[10px] uppercase tracking-[.22em] text-hc-amber-light">New reference entries</p><h2 className="mt-3 font-hc-display text-5xl font-semibold tracking-[-.05em]">The latest compounds.</h2></div><div className="grid grid-cols-3 gap-4 self-end font-hc-mono text-[9px] uppercase tracking-wider text-hc-sage"><span className="flex gap-2"><FileCheck2 className="h-4 w-4"/> Source kept</span><span className="flex gap-2"><FlaskConical className="h-4 w-4"/> Format shown</span><span className="flex gap-2"><ScanLine className="h-4 w-4"/> Exact index</span></div></div><div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4">{results.map((product,index)=><ProductCard key={product.id} product={product} priority={index<4}/>)}</div></div></section>
            <p className="border-t border-emerald-950/10 px-6 py-7 text-center font-hc-mono text-[10px] uppercase tracking-wider text-hc-ink-soft">For laboratory research and educational use only · Not for human consumption</p>
        </main>
    )
}

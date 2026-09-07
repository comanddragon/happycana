import Image from 'next/image'
import Link from 'next/link'
import { ArrowRight } from 'lucide-react'
import { ProductCard } from '@/components/shop/ProductCard'
import { getCategories, getProducts } from '@/lib/catalog.server'
import type { Storefront } from '@/types'

export async function HashHome({ storefront }: { storefront: Storefront }) {
    const [{ results }, categories] = await Promise.all([
        getProducts({ ordering: '-created_at', page_size: 8 }, { revalidate: false }),
        getCategories(),
    ])
    const methods = categories.filter(category => category.is_key).slice(0, 6)
    return (
        <main className="bg-[#100c09] text-[#f5ead5]">
            <section className="relative -mt-[88px] min-h-[860px] overflow-hidden px-6 pb-16 pt-40">
                <Image src="/editorial/hash-hero.webp" alt="Macro view of golden solventless hash resin" fill priority sizes="100vw" className="axiom-hero-image object-cover object-[65%_center] opacity-85"/>
                <div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(12,8,5,.98)_0%,rgba(12,8,5,.78)_38%,rgba(12,8,5,.08)_78%),linear-gradient(0deg,#100c09_0%,transparent_45%)]"/>
                <div className="relative mx-auto flex min-h-[690px] max-w-[1220px] items-center">
                    <div className="max-w-[650px]">
                        <div className="mb-8 flex items-center gap-5 font-hc-mono text-[10px] uppercase tracking-[.28em] text-[#d5a34b]"><span className="h-px w-14 bg-current"/> Axiom private archive</div>
                        <h1 className="font-hc-display text-[7rem] uppercase leading-[.74] tracking-[.015em] sm:text-[10rem] lg:text-[13rem]">Pure<br/><span className="text-[#e0a438]">resin.</span></h1>
                        <p className="mt-7 max-w-md border-l border-[#d5a34b] pl-5 text-base leading-7 text-[#c9bda8]">{storefront.name} is a collector’s room for solventless craft, indexed by method, maker, texture, and provenance.</p>
                        <div className="mt-9 flex gap-3"><Link href="/shop/products" className="inline-flex items-center gap-2 bg-[#dfa840] px-6 py-3.5 text-sm font-bold text-[#160e07] transition hover:-translate-y-1">Enter the archive <ArrowRight className="h-4 w-4"/></Link><Link href="/shop" className="border border-white/25 bg-black/20 px-6 py-3.5 text-sm font-semibold backdrop-blur-xl">Browse methods</Link></div>
                    </div>
                </div>
                <div className="absolute bottom-7 right-7 hidden border border-white/15 bg-black/30 p-4 font-hc-mono text-[9px] uppercase leading-5 tracking-[.2em] text-white/60 backdrop-blur-xl sm:block">Dry sift / Static / Frozen<br/>Archive release 001</div>
            </section>

            {methods.length > 0 && <section className="relative z-10 mx-auto -mt-16 max-w-[1220px] px-6 pb-24"><div className="mb-7 flex items-end justify-between"><div><p className="font-hc-mono text-[10px] uppercase tracking-[.24em] text-[#d5a34b]">Select by process</p><h2 className="mt-2 font-hc-display text-6xl uppercase leading-none">The methods</h2></div><Link href="/shop" className="text-sm text-[#d5a34b]">Full index →</Link></div><div className="grid grid-cols-2 gap-3 md:grid-cols-3">{methods.map((category,index)=><Link key={category.id} href={`/shop/categories/${category.slug}`} className={`group relative overflow-hidden border border-white/10 bg-[#1b130d] ${index===0?'aspect-[1.55] md:col-span-2':'aspect-[1.15]'}`}><Image src={category.image_url} alt="" fill sizes="(max-width:768px) 50vw, 33vw" className="object-cover opacity-70 saturate-[.8] transition duration-700 group-hover:scale-105 group-hover:opacity-90"/><div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/15 to-transparent"/><span className="absolute left-4 top-4 font-hc-mono text-[9px] text-white/55">PLATE 0{index+1}</span><h3 className="absolute bottom-4 left-4 font-hc-display text-4xl uppercase tracking-wide text-[#fff3db]">{category.name}</h3></Link>)}</div></section>}

            <section className="border-t border-white/10 bg-[#17100b] px-6 py-24"><div className="mx-auto max-w-[1220px]"><div className="mb-10 flex items-end justify-between"><div><p className="font-hc-mono text-[10px] uppercase tracking-[.22em] text-[#d5a34b]">Recently catalogued</p><h2 className="mt-2 font-hc-display text-7xl uppercase leading-none">Fresh plates</h2></div><Link href="/shop/products" className="hidden items-center gap-2 text-sm text-[#d5a34b] sm:flex">View the room <ArrowRight className="h-4 w-4"/></Link></div><div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4">{results.map((product,index)=><ProductCard key={product.id} product={product} priority={index<4}/>)}</div></div></section>
        </main>
    )
}

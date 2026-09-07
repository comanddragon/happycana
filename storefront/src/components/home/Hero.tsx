import Image from 'next/image'
import Link from 'next/link'
import { ArrowRight, ShieldCheck } from 'lucide-react'

export function Hero() {
    return (
        <section id="top" className="relative -mt-[88px] min-h-[820px] overflow-hidden bg-[#152219] px-6 pb-20 pt-40 text-[#fff8eb] sm:pt-48">
            <Image src="/editorial/dispensary-hero.webp" alt="Curated botanical cannabis flowers and natural objects" fill priority sizes="100vw" className="axiom-hero-image object-cover object-center opacity-80" />
            <div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(12,25,17,.96)_0%,rgba(12,25,17,.74)_43%,rgba(12,25,17,.12)_78%),linear-gradient(0deg,rgba(12,25,17,.8),transparent_45%)]" />
            <div className="relative mx-auto flex min-h-[630px] max-w-[1220px] items-end">
                <div className="max-w-[690px] pb-8">
                    <p className="mb-6 flex items-center gap-3 font-hc-mono text-[11px] uppercase tracking-[.24em] text-hc-amber-light before:h-px before:w-10 before:bg-current">The Axiom field guide · edition 01</p>
                    <h1 className="font-hc-display text-[4rem] font-medium leading-[.82] tracking-[-.045em] sm:text-[6rem] lg:text-[8rem]">Find your<br/><em className="font-normal text-hc-amber-light">natural state.</em></h1>
                    <p className="mt-8 max-w-lg text-base leading-7 text-[#d7dfd3] sm:text-lg">An image-led dispensary for carefully sourced flower, edibles, and concentrates—organized by how you want the day to feel.</p>
                    <div className="mt-9 flex flex-wrap gap-3">
                        <Link href="/shop/products" className="inline-flex items-center gap-2 rounded-full bg-hc-amber-light px-6 py-3.5 text-sm font-semibold text-hc-canopy transition hover:-translate-y-1">Explore the collection <ArrowRight className="h-4 w-4"/></Link>
                        <Link href="/shop" className="rounded-full border border-white/30 bg-white/[.06] px-6 py-3.5 text-sm font-semibold backdrop-blur-md transition hover:bg-white/[.12]">Shop by mood</Link>
                    </div>
                </div>
            </div>
            <div className="absolute bottom-6 right-6 hidden items-center gap-2 rounded-full border border-white/15 bg-black/20 px-4 py-2 font-hc-mono text-[10px] uppercase tracking-wider text-white/75 backdrop-blur-lg sm:flex"><ShieldCheck className="h-3.5 w-3.5 text-hc-amber-light"/> Independently lab tested</div>
        </section>
    )
}

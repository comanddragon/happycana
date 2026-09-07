'use client'

import Link from 'next/link'
import { ChevronDown } from 'lucide-react'
import { useEffects } from '@/hooks/useApi'

export function NavEffectsMenu() {
    const { data: effects, isLoading } = useEffects()

    return (
        <div className="group relative">
            <button className="flex items-center gap-1 text-sm font-medium text-hc-sage transition-colors hover:text-hc-paper">
                Shop by effect
                <ChevronDown className="h-4 w-4 transition-transform duration-200 group-hover:rotate-180 group-focus-within:rotate-180" />
            </button>
            <div className="pointer-events-none invisible absolute left-0 top-full z-50 min-w-[210px] translate-y-1 pt-2 opacity-0 transition-[opacity,transform] duration-150 ease-out group-hover:pointer-events-auto group-hover:visible group-hover:translate-y-0 group-hover:opacity-100 group-focus-within:pointer-events-auto group-focus-within:visible group-focus-within:translate-y-0 group-focus-within:opacity-100">
                <div className="rounded-xl border border-white/10 bg-hc-canopy-2 p-2 shadow-[0_16px_40px_rgba(0,0,0,.32)]">
                    {effects?.length ? effects.map(effect => (
                        <Link key={effect.id} href={`/shop/products?effect=${effect.slug}`} className="flex min-h-9 items-center rounded-lg px-4 py-2 text-sm font-medium text-hc-sage transition-colors hover:bg-white/[.07] hover:text-hc-paper focus-visible:bg-white/[.07] focus-visible:text-hc-paper focus-visible:outline-none">
                            {effect.name}
                        </Link>
                    )) : (
                        <span className="block px-4 py-2 text-sm text-hc-sage/60">{isLoading ? 'Loading…' : 'No effects available'}</span>
                    )}
                </div>
            </div>
        </div>
    )
}

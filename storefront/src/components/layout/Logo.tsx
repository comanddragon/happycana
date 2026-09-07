'use client'

import Link from 'next/link'
import { useStorefront } from '@/storefront/StorefrontProvider'

export function Logo({
                         variant: _variant = 'dark-bg',
                         height = 28,
                         href = '/',
                         priority: _priority = false,
                     }: {
    variant?: 'dark-bg' | 'light-bg'
    height?: number
    href?: string
    priority?: boolean
}) {
    const { storefront } = useStorefront()
    return (
        <Link href={href} className="group flex shrink-0 items-center gap-2.5 text-hc-paper" aria-label={`${storefront.name} home`}>
            <svg aria-hidden viewBox="0 0 42 42" style={{height, width: height}} className="shrink-0 text-hc-amber-light transition-transform duration-500 group-hover:rotate-6">
                <path d="M21 3 38 36H4L21 3Z" fill="none" stroke="currentColor" strokeWidth="2.2" />
                {storefront.kind === 'peptides' ? <><circle cx="21" cy="14" r="2.2" fill="currentColor"/><circle cx="14" cy="28" r="2.2" fill="currentColor"/><circle cx="28" cy="28" r="2.2" fill="currentColor"/><path d="m20 16-5 10m12 0-5-10m-5 12h9" stroke="currentColor"/></> : storefront.kind === 'hash' ? <><path d="M12 29c5-5 13-5 18 0M14 25c4-4 10-4 14 0M17 21c2-2 6-2 8 0" fill="none" stroke="currentColor" strokeWidth="1.6"/></> : <><path d="M21 30c-1-9 1-15 7-20-1 8-3 15-7 20Zm0 0c0-7-3-12-8-15 0 7 3 12 8 15Z" fill="currentColor" opacity=".82"/></>}
            </svg>
            <span className="leading-none"><span className="block font-hc-commerce text-xl font-semibold tracking-[-.01em]">{storefront.name}</span><span className="mt-1 hidden font-hc-mono text-[8px] uppercase tracking-[.22em] text-hc-sage sm:block">{storefront.kind === 'peptides' ? 'Research catalog' : storefront.kind === 'hash' ? 'Solventless archive' : 'Botanical dispensary'}</span></span>
        </Link>
    )
}

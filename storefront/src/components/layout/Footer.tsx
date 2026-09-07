'use client'

import Link from 'next/link'
import { Logo } from './Logo'
import { useStorefront } from '@/storefront/StorefrontProvider'
import { brandingString } from '@/storefront/config'

const CANNABIS_COLUMNS: Record<string, { label: string; href: string }[]> = {
    Shop: [
        { label: 'Flower', href: '/shop/products?category=flower' },
        { label: 'Edibles', href: '/shop/products?category=edibles' },
        { label: 'New arrivals', href: '/shop/new-arrivals' },
        { label: 'Best sellers', href: '/shop/best-sellers' },
    ],
    Learn: [
        { label: 'Blog', href: '/blog' },
        { label: 'Lab results', href: '/lab-results' },
    ],
    Account: [
        { label: 'Profile', href: '/account/profile' },
        { label: 'Orders', href: '/account/orders' },
        { label: 'Addresses', href: '/account/addresses' },
    ],
    Support: [
        { label: 'Contact', href: '/help/faq' },
        { label: 'FAQ', href: '/help/faq' },
        { label: 'Track an order', href: 'https://shipradarx.com/' },
    ],
}

const PEPTIDE_COLUMNS: Record<string, { label: string; href: string }[]> = {
    Catalog: [
        { label: 'All compounds', href: '/shop/products' },
        { label: 'New arrivals', href: '/shop/new-arrivals' },
        { label: 'Research blends', href: '/shop/products?category=peptide-peptide-blends' },
    ],
    Resources: [
        { label: 'Documentation', href: '/lab-results' },
        { label: 'Research notes', href: '/blog' },
    ],
    Account: CANNABIS_COLUMNS.Account,
    Support: CANNABIS_COLUMNS.Support,
}

const HASH_COLUMNS: Record<string, { label: string; href: string }[]> = {
    Catalog: [
        { label: 'All hash', href: '/shop/products' },
        { label: 'Dry sift', href: '/shop/products?category=hash-dry-sift-hash' },
        { label: 'Static sift', href: '/shop/products?category=hash-static-sift-hash' },
        { label: 'New drops', href: '/shop/new-arrivals' },
    ],
    Provenance: [
        { label: 'Lab archive', href: '/lab-results' },
        { label: 'Hash journal', href: '/blog' },
    ],
    Account: CANNABIS_COLUMNS.Account,
    Support: CANNABIS_COLUMNS.Support,
}

export function Footer() {
    const { storefront, features } = useStorefront()
    const description = brandingString(storefront, 'description') || `Quality products and dependable service from ${storefront.name}.`
    const license = brandingString(storefront, 'license_number')
    const columns = storefront.kind === 'hash'
        ? HASH_COLUMNS
        : features.peptideCatalog ? PEPTIDE_COLUMNS : CANNABIS_COLUMNS
    return (
        <footer className="bg-hc-canopy-2 px-7 pb-8 pt-16 text-hc-sage">
            <div className="mx-auto max-w-[1180px]">
                <div className="grid grid-cols-2 gap-8 border-b border-hc-paper/10 pb-11 md:grid-cols-[1.2fr_1fr_1fr_1fr_1fr]">
                    {/* Brand */}
                    <div>
                        <Logo height={22} href="/shop" />
                        <p className="mt-4 max-w-[260px] text-[13.5px] leading-relaxed text-hc-sage">
                            {description}
                        </p>
                    </div>

                    {Object.entries(columns).map(([title, links]) => (
                        <div key={title}>
                            <h3 className="mb-4 font-hc-mono text-[11.5px] uppercase tracking-[0.08em] text-hc-paper">{title}</h3>
                            <ul className="space-y-0">
                                {links.map(({ label, href }) => (
                                    <li key={label}>
                                        <Link
                                            href={href}
                                            className="block py-1.5 text-sm text-hc-sage transition-colors hover:text-hc-paper focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-hc-amber-light/50 rounded-sm"
                                        >
                                            {label}
                                        </Link>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ))}
                </div>

                <div className="mt-8 flex flex-wrap items-start justify-between gap-6">
                    {features.ageGate && <p className="max-w-[640px] text-xs leading-relaxed text-hc-sage">
                        You must be 21 years of age or older to purchase. Keep out of reach of children and pets. For use only
                        by adults 21+, in states where cannabis is legal. This product has not been evaluated by the FDA and is
                        not intended to diagnose, treat, cure, or prevent any disease. Please consume responsibly and do not
                        operate a vehicle or machinery after use.
                    </p>}
                    {features.peptideCatalog && <p className="max-w-[640px] text-xs leading-relaxed text-hc-sage">
                        For laboratory research and educational use only. Not for human consumption. No product information
                        on this site is intended to diagnose, treat, cure, or prevent disease.
                    </p>}
                    <div className="flex flex-col items-start gap-2 sm:items-end">
                        <p className="font-hc-mono text-[11.5px] text-hc-sage">
                            {license ? `${license} · ` : ''}© {new Date().getFullYear()} {storefront.name.toUpperCase()}
                        </p>
                        <div className="flex items-center gap-4 text-xs text-hc-sage">
                            <Link href="/privacy" className="hover:text-hc-paper transition-colors">Privacy Policy</Link>
                            <Link href="/terms" className="hover:text-hc-paper transition-colors">Terms of Service</Link>
                        </div>
                    </div>
                </div>
            </div>
        </footer>
    )
}

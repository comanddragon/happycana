export interface NavLink {
    href?: string
    label: string
    dynamic?: boolean
    effects?: boolean
}

export const NAV_LINKS: NavLink[] = [
    { href: '/shop', label: 'Shop' },
    { href: '/shop/products', label: 'Products' },
    { label: 'Categories', dynamic: true },
    { label: 'Shop by effect', effects: true },
    { href: '/blog', label: 'Blog' },
]

export const PEPTIDE_NAV_LINKS: NavLink[] = [
    { href: '/shop', label: 'Catalog' },
    { href: '/shop/products', label: 'All compounds' },
    { label: 'Research areas', dynamic: true },
    { href: '/blog', label: 'Research notes' },
]

export const HASH_NAV_LINKS: NavLink[] = [
    { href: '/shop', label: 'Hash room' },
    { href: '/shop/products', label: 'All hash' },
    { label: 'Hash styles', dynamic: true },
    { href: '/lab-results', label: 'Lab archive' },
]

export const AMBER_DOT = {
    background: 'radial-gradient(circle at 32% 28%, var(--color-hc-amber-light), var(--color-hc-amber) 60%, var(--color-hc-amber-dim))',
}

export const AMBER_BUTTON =
    'inline-flex items-center justify-center gap-2 rounded-full px-4 text-sm font-semibold text-hc-canopy-2 shadow-[0_6px_18px_rgba(200,121,46,.35)] transition-transform hover:-translate-y-0.5 hover:shadow-[0_10px_24px_rgba(200,121,46,.45)]'

export const AMBER_BUTTON_STYLE = {
    background: 'linear-gradient(180deg, var(--color-hc-amber-light), var(--color-hc-amber))',
}

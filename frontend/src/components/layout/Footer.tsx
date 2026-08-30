import Link from 'next/link'
import { Logo } from './Logo'

const COLUMNS: Record<string, { label: string; href: string }[]> = {
  Shop: [
    { label: 'Flower', href: '/shop/products?category=flower' },
    { label: 'Edibles', href: '/shop/products?category=edibles' },
    { label: 'Vapes', href: '/shop/products?category=vaporizers' },
    { label: 'New arrivals', href: '/shop/products?ordering=-created_at' },
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

export function Footer() {
  return (
    <footer className="bg-hc-canopy-2 px-7 pb-8 pt-16 text-hc-sage">
      <div className="mx-auto max-w-[1180px]">
        <div className="grid grid-cols-2 gap-8 border-b border-hc-paper/10 pb-11 md:grid-cols-[1.4fr_1fr_1fr_1fr]">
          {/* Brand */}
          <div>
            <Logo height={22} href="/shop" />
            <p className="mt-4 max-w-[260px] text-[13.5px] leading-relaxed text-hc-sage-dim">
              A licensed cannabis retailer offering same-day pickup and delivery, with every batch independently lab-tested.
            </p>
          </div>

          {Object.entries(COLUMNS).map(([title, links]) => (
            <div key={title}>
              <h4 className="mb-4 font-hc-mono text-[11.5px] uppercase tracking-[0.08em] text-hc-paper">{title}</h4>
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
          <p className="max-w-[640px] text-xs leading-relaxed text-hc-sage-dim">
            You must be 21 years of age or older to purchase. Keep out of reach of children and pets. For use only
            by adults 21+, in states where cannabis is legal. This product has not been evaluated by the FDA and is
            not intended to diagnose, treat, cure, or prevent any disease. Please consume responsibly and do not
            operate a vehicle or machinery after use.
          </p>
          <div className="flex flex-col items-start gap-2 sm:items-end">
            <p className="whitespace-nowrap font-hc-mono text-[11.5px] text-hc-sage-dim">
              STATE LICENSE #AD-2291-HC · © {new Date().getFullYear()} HAPPYCANA
            </p>
            <div className="flex items-center gap-4 text-xs text-hc-sage-dim">
              <Link href="/privacy" className="hover:text-hc-paper transition-colors">Privacy Policy</Link>
              <Link href="/terms" className="hover:text-hc-paper transition-colors">Terms of Service</Link>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}
// app/(shop)/shop/checkout/layout.tsx
import type { Metadata } from 'next'

// Checkout is a cart-state-dependent, no-unique-content page — nested here
// so it overrides just `robots` on top of the parent shop layout's
// title/description, rather than replacing that metadata outright.
export const metadata: Metadata = {
    robots: { index: false, follow: false },
}

export default function CheckoutLayout({ children }: { children: React.ReactNode }) {
    return children
}

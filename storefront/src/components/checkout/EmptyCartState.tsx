import Link from 'next/link'
import { ShoppingBag, ArrowRight } from 'lucide-react'
import { AMBER_GRADIENT } from '@/lib/checkout/constants'

export function EmptyCartState() {
    return (
        <div className="mx-auto flex min-h-[60vh] max-w-md flex-col items-center justify-center px-4 py-20 text-center">
            <div className="mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-hc-paper-2">
                <ShoppingBag className="h-7 w-7 text-hc-ink-soft/50" />
            </div>
            <h1 className="font-hc-display text-2xl font-medium text-hc-ink">Your cart is empty</h1>
            <p className="mt-2 text-sm text-hc-ink-soft">Add something from the menu before checking out.</p>
            <Link
                href="/shop/products"
                className="mt-6 inline-flex items-center gap-2 rounded-full px-6 py-3 text-sm font-semibold text-hc-canopy-2 shadow-[0_6px_18px_rgba(200,121,46,.35)] transition-transform hover:-translate-y-0.5"
                style={AMBER_GRADIENT}
            >
                Browse the menu <ArrowRight className="h-4 w-4" />
            </Link>
        </div>
    )
}

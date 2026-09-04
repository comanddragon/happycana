// components/blog/ProductPicks.tsx
// Drops a small strip of real products into a blog post \u2014 e.g. "the picks
// from this guide" \u2014 reusing the same ProductCard as the shop so price and
// stock stay live instead of being hand-typed into article copy.
import { ProductCard } from '@/components/shop/ProductCard'
import { getProducts } from '@/lib/catalog.server'
import type { ProductFilterParams } from '@/types'

interface Props {
    heading?: string
    /** Passed straight through to getProducts; defaults to bestsellers. */
    filters?: ProductFilterParams
    count?: number
}

export async function ProductPicks({ heading = 'From the shop', filters, count = 3 }: Props) {
    const { results } = await getProducts(
        { ordering: '-units_sold_hint', page_size: count, ...filters },
        { revalidate: 3600 },
    )

    if (results.length === 0) return null

    return (
        <div>
            <p className="mb-4 font-hc-mono text-[11px] uppercase tracking-[0.1em] text-hc-sage-dim">{heading}</p>
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
                {results.map(product => (
                    <ProductCard key={product.id} product={product} />
                ))}
            </div>
        </div>
    )
}

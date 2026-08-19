'use client'

import { useProducts } from '@/hooks/useApi'
import { ProductCard } from './ProductCard'

export function FeaturedProducts() {
  // `is_featured` isn't set on any product in the current catalog (it's
  // driven by curated collections at the source, not a per-product flag —
  // see MISSING_FIELDS.md), so ordering by it would return nothing.
  // `units_sold_hint` is real popularity data from the source and makes a
  // more honest "featured" default until products are curated manually.
  const { data, isLoading } = useProducts({ page_size: 8, ordering: '-units_sold_hint' })

  if (isLoading) {
    return (
      <div className="grid grid-cols-2 gap-x-5 gap-y-7 sm:grid-cols-3 lg:grid-cols-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="space-y-3 animate-pulse pt-2">
            <div className="aspect-square rounded-2xl bg-hc-paper-2" />
            <div className="h-4 rounded bg-hc-paper-2 w-3/4" />
            <div className="h-4 rounded bg-hc-paper-2 w-1/2" />
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-2 gap-x-5 gap-y-7 sm:grid-cols-3 lg:grid-cols-4">
      {data?.results.map((product, i) => (
        <ProductCard key={product.id} product={product} priority={i < 4} />
      ))}
    </div>
  )
}

'use client'

import Link from 'next/link'
import { useCategories } from '@/hooks/useApi'

export function CategoryGrid() {
  const { data: categories, isLoading } = useCategories()

  if (isLoading) {
    return (
      <div className="grid grid-cols-2 gap-3.5 sm:grid-cols-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="aspect-[4/3] animate-pulse rounded-2xl bg-hc-paper-2" />
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-2 gap-3.5 sm:grid-cols-4">
      {categories?.slice(0, 8).map(cat => (
        <Link
          key={cat.id}
          href={`/shop/products?category=${cat.slug}`}
          className="group relative flex aspect-[4/3] flex-col items-center justify-center rounded-2xl border border-hc-ink/[0.08] bg-white px-4 py-5 text-center transition-all duration-200 hover:-translate-y-1 hover:border-hc-amber hover:shadow-[0_16px_30px_-14px_rgba(23,20,15,0.25)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-hc-amber focus-visible:ring-offset-2"
        >
          <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-full bg-hc-canopy transition-transform duration-300 group-hover:scale-110">
            <span
              className="h-2.5 w-2.5 rounded-full"
              style={{ background: 'radial-gradient(circle at 32% 28%, var(--color-hc-amber-light), var(--color-hc-amber) 60%, var(--color-hc-amber-dim))' }}
            />
          </div>
          <p className="font-hc-display text-base font-medium text-hc-ink">{cat.name}</p>
          {cat.children && cat.children.length > 0 && (
            <p className="mt-1 font-hc-mono text-[10.5px] tracking-wide text-hc-ink-soft">
              {cat.children.length} SUBCATEGORIES
            </p>
          )}
        </Link>
      ))}
    </div>
  )
}

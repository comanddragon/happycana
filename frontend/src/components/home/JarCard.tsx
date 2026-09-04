import { memo } from 'react'
import Link from 'next/link'
import { FileText } from 'lucide-react'
import { cn } from '@/lib/utils'

export interface JarProduct {
    name: string
    slug: string
    kind: string | null
    thc: string | null
    terpene: string | null
    effect: string | null
    brand: string | null
    category: string | null
    weight: string | null
    sku: string
    coaUrl: string | null
    price?: string
}

interface Props {
    product: JarProduct
    className?: string
    interactive?: boolean
}

export const JarCard = memo(function JarCard({ product, className, interactive = false }: Props) {
    return (
        <Link
            href={`/shop/products/${product.slug}`}
            className={cn(
                'relative block rounded-[22px] bg-gradient-to-b from-[#fbf7ee] to-hc-paper-2 px-6 pt-7 pb-5 text-hc-ink shadow-[0_30px_60px_-20px_rgba(0,0,0,0.55)]',
                interactive && 'transition-transform duration-300 hover:-translate-y-2 hover:rotate-[-1.2deg] hover:shadow-[0_34px_60px_-18px_rgba(23,20,15,0.3)]',
                className,
            )}
        >
            {/* lid tab — the recurring "jar label" signature */}
            <span className="absolute -top-[11px] left-1/2 h-[22px] w-14 -translate-x-1/2 rounded-full bg-gradient-to-b from-hc-amber-light to-hc-amber" />

            <div className="mt-1.5 flex items-start justify-between gap-3">
                <div className="min-w-0">
                    {product.brand && <p className="mb-1 font-hc-mono text-[10px] uppercase tracking-[0.1em] text-hc-amber-dim">{product.brand}</p>}
                    <span className="font-hc-display text-xl font-medium leading-tight">{product.name}</span>
                </div>
                {product.kind && (
                    <span className="shrink-0 rounded-full bg-hc-canopy px-2.5 py-1 font-hc-mono text-[10.5px] tracking-wide text-hc-sage">
                        {product.kind}
                    </span>
                )}
            </div>

            <div className="mt-4 grid grid-cols-2 gap-x-4 gap-y-3 font-hc-mono text-[10px] uppercase tracking-wide text-hc-ink-soft">
                {product.category && <div><b className="block truncate text-sm normal-case tracking-normal text-hc-ink">{product.category}</b>Category</div>}
                {product.weight && <div><b className="block text-sm normal-case tracking-normal text-hc-ink">{product.weight}</b>Size</div>}
                {product.thc && <div><b className="block text-sm normal-case tracking-normal text-hc-ink">{product.thc}</b>Potency</div>}
                {product.effect && <div><b className="block truncate text-sm normal-case tracking-normal text-hc-ink">{product.effect}</b>Effect</div>}
                {product.terpene && <div><b className="block truncate text-sm normal-case tracking-normal text-hc-ink">{product.terpene}</b>Top terpene</div>}
            </div>

            <div className="my-4 h-px bg-hc-ink/10" />
            <div className="flex items-center justify-between gap-3">
                {product.price && <p className="font-hc-mono text-sm font-semibold text-hc-amber-dim">{product.price}</p>}
                {product.coaUrl && (
                <p className="flex items-center gap-1.5 font-hc-mono text-[10.5px] tracking-wide text-hc-amber-dim">
                    <FileText className="h-3 w-3" />
                    Lab report
                </p>
                )}
            </div>
        </Link>
    )
})

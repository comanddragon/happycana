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
                <span className="font-hc-display text-xl font-medium">{product.name}</span>
                {product.kind && (
                    <span className="shrink-0 rounded-full bg-hc-canopy px-2.5 py-1 font-hc-mono text-[10.5px] tracking-wide text-hc-sage">
                        {product.kind}
                    </span>
                )}
            </div>

            <div className="mt-3.5 flex gap-4 font-hc-mono text-xs text-hc-ink-soft">
                <div><b className="block text-[15px] text-hc-ink">{product.thc ?? '—'}</b>THC</div>
                <div><b className="block text-[15px] text-hc-ink">{product.terpene ?? '—'}</b>TERPENE</div>
                <div><b className="block text-[15px] text-hc-ink">{product.effect ?? '—'}</b>EFFECT</div>
            </div>

            <div className="my-4 h-px bg-hc-ink/10" />
            <p className="font-hc-mono text-[10.5px] tracking-wide text-hc-ink-soft">
                SKU {product.sku}
            </p>

            {product.coaUrl && (
                <p className="mt-2 flex items-center gap-1.5 font-hc-mono text-[10.5px] tracking-wide text-hc-amber-dim">
                    <FileText className="h-3 w-3" />
                    Certificate of analysis available
                </p>
            )}

            {product.price && (
                <>
                    <div className="my-4 h-px bg-hc-ink/10" />
                    <p className="font-hc-mono text-sm font-medium text-hc-amber-dim">{product.price}</p>
                </>
            )}
        </Link>
    )
})

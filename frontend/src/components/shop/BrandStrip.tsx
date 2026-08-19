'use client'

import Link from 'next/link'
import Image from 'next/image'
import { useBrands } from '@/hooks/useApi'
import { ScrollArea, ScrollBar } from '@/components/ui/scroll-area'
import { mediaUrl } from '@/lib/utils'

export function BrandStrip() {
    const { data: brands, isLoading } = useBrands()

    if (isLoading) {
        return (
            <div className="flex gap-3">
                {Array.from({ length: 8 }).map((_, i) => (
                    <div key={i} className="h-20 w-32 shrink-0 animate-pulse rounded-2xl bg-hc-paper-2" />
                ))}
            </div>
        )
    }

    const withLogos = (brands ?? []).filter(b => b.logo_url)
    if (withLogos.length === 0) return null

    return (
        <ScrollArea className="w-full">
            <div className="flex gap-3 pb-2">
                {withLogos.map(brand => (
                    <Link
                        key={brand.id}
                        href={`/shop/products?brand=${brand.slug}`}
                        className="group flex h-20 w-32 shrink-0 flex-col items-center justify-center gap-2 rounded-2xl border border-hc-ink/[0.08] bg-white px-3 transition-all duration-200 hover:-translate-y-1 hover:border-hc-amber hover:shadow-[0_16px_30px_-14px_rgba(23,20,15,0.25)]"
                    >
                        <Image
                            src={mediaUrl(brand.logo_url)!}
                            alt={brand.name}
                            width={80}
                            height={32}
                            unoptimized
                            style={{ width: 'auto', height: 'auto' }}
                            className="h-8 w-auto max-w-[88px] object-contain grayscale transition-all duration-200 group-hover:grayscale-0"
                        />
                        <span className="font-hc-mono text-[10px] tracking-wide text-hc-ink-soft truncate max-w-full">
                            {brand.name}
                        </span>
                    </Link>
                ))}
            </div>
            <ScrollBar orientation="horizontal" />
        </ScrollArea>
    )
}

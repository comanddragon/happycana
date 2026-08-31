'use client'

import Link from 'next/link'
import Image from 'next/image'
import { useBrands } from '@/hooks/useApi'
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

    const CARD_PX = 128 + 12 // w-32 + gap-3
    const MIN_TRACK_PX = 2400 // safely exceeds container width, even on wide screens

    const setPx = withLogos.length * CARD_PX
    const repeats = Math.max(2, Math.ceil(MIN_TRACK_PX / setPx / 2) * 2)
    const track = Array.from({ length: repeats }, () => withLogos).flat()

    const duration = (repeats / 2) * withLogos.length * 4

    return (
        <div className="group/marquee w-full overflow-hidden [mask-image:linear-gradient(to_right,transparent,black_24px,black_calc(100%-24px),transparent)]">
            <div
                className="flex w-max gap-3 pt-2 pb-2 group-hover/marquee:[animation-play-state:paused]"
                style={{ animation: `hc-marquee ${duration}s linear infinite` }}
            >
                {track.map((brand, i) => (
                    <Link
                        key={`${brand.id}-${i}`}
                        href={`/shop/products?brand=${brand.slug}`}
                        className="group flex pt-2 h-24 w-32 shrink-0 flex-col items-center justify-center gap-2 rounded-2xl border border-hc-ink/[0.08] bg-white px-3 transition-all duration-200 hover:-translate-y-1 hover:border-hc-amber hover:shadow-[0_16px_30px_-14px_rgba(23,20,15,0.25)]"
                    >
                        <Image
                            src={mediaUrl(brand.logo_url)!}
                            alt={brand.name}
                            width={80}
                            height={32}
                            unoptimized
                            loading="eager"
                            style={{ width: 'auto', height: 'auto' }}
                            className="h-8 w-auto max-w-[88px] object-contain grayscale transition-all duration-200 group-hover:grayscale-0"
                        />
                        <span className="font-hc-mono text-[10px] tracking-wide text-hc-ink-soft truncate max-w-full">
                            {brand.name}
                        </span>
                    </Link>
                ))}
            </div>
        </div>
    )
}

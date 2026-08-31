'use client'

import React, { useEffect, useRef } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { mediaUrl } from '@/lib/utils'
import type { Brand } from '@/types'

export function BrandStripSkeleton() {
    return (
        <div className="flex gap-3">
            {Array.from({ length: 8 }).map((_, i) => (
                <div key={i} className="h-20 w-32 shrink-0 animate-pulse rounded-2xl bg-hc-paper-2" />
            ))}
        </div>
    )
}

const CARD_PX = 128 + 12 // w-32 + gap-3
const MIN_TRACK_PX = 2400 // safely exceeds container width, even on wide screens
const AUTO_SCROLL_PX_PER_SEC = 75 // marquee speed
const DRAG_CLICK_THRESHOLD_PX = 5 // pointer movement beyond this counts as a drag, not a click

export function BrandStrip({ brands }: { brands: Brand[] }) {
    const withLogos = brands.filter(b => b.logo_url)

    const trackRef = useRef<HTMLDivElement>(null)
    const halfWidthRef = useRef(0) // px the track shifts over one full animation pass
    const durationRef = useRef(0) // seconds for one full pass
    const draggedRef = useRef(false) // true once a drag has moved past the click threshold

    const setPx = withLogos.length * CARD_PX
    // Always even, so the CSS animation's -50% midpoint lands exactly on a
    // repeat boundary — that's what makes the loop invisible.
    const repeats = Math.max(4, Math.ceil(MIN_TRACK_PX / setPx / 2) * 2)
    const track = withLogos.length > 0 ? Array.from({ length: repeats }, () => withLogos).flat() : []

    const halfWidth = (repeats / 2) * setPx
    const duration = halfWidth / AUTO_SCROLL_PX_PER_SEC // seconds, keeps a constant visual speed regardless of brand count

    useEffect(() => {
        halfWidthRef.current = halfWidth
        durationRef.current = duration
    }, [halfWidth, duration])

    if (withLogos.length === 0) return null

    const handlePointerDown = (e: React.PointerEvent<HTMLDivElement>) => {
        const el = trackRef.current
        if (!el) return
        // Without this, the browser's native "drag this link" / text-selection
        // gesture takes over the pointerdown and our pointermove handler never
        // sees the movement.
        e.preventDefault()

        // Freeze wherever the CSS animation currently is, expressed as a real
        // translateX in px, so the drag can pick up from that exact spot.
        const matrix = new DOMMatrixReadOnly(getComputedStyle(el).transform)
        let x = matrix.m41

        draggedRef.current = false
        const startX = e.clientX
        let lastX = startX

        el.style.animation = 'none'
        el.style.transform = `translateX(${x}px)`

        const handleMove = (ev: PointerEvent) => {
            const node = trackRef.current
            if (!node) return
            if (Math.abs(ev.clientX - startX) > DRAG_CLICK_THRESHOLD_PX) draggedRef.current = true

            const dx = ev.clientX - lastX
            lastX = ev.clientX
            x += dx

            const half = halfWidthRef.current
            if (half > 0) {
                const mag = ((-x % half) + half) % half
                x = -mag
            }
            node.style.transform = `translateX(${x}px)`
        }

        const handleUp = () => {
            const node = trackRef.current
            window.removeEventListener('pointermove', handleMove)
            window.removeEventListener('pointerup', handleUp)
            window.removeEventListener('pointercancel', handleUp)
            if (!node) return

            const half = halfWidthRef.current
            const dur = durationRef.current
            const elapsed = half > 0 ? dur * (Math.abs(x) / half) : 0
            node.style.animation = ''
            node.style.transform = ''
            node.style.animationDelay = `-${elapsed}s`
        }

        window.addEventListener('pointermove', handleMove)
        window.addEventListener('pointerup', handleUp)
        window.addEventListener('pointercancel', handleUp)
    }

    return (
        <div className="w-full overflow-hidden [mask-image:linear-gradient(to_right,transparent,black_24px,black_calc(100%-24px),transparent)]">
            <div
                ref={trackRef}
                onPointerDown={handlePointerDown}
                className="hc-marquee-track select-none gap-3 pt-2 pb-2 [touch-action:pan-y] active:cursor-grabbing"
                style={{ '--hc-marquee-duration': `${duration}s` } as React.CSSProperties}
            >
                {track.map((brand, i) => (
                    <Link
                        key={`${brand.id}-${i}`}
                        href={`/shop/products?brand=${brand.slug}`}
                        draggable={false}
                        onClick={(e) => { if (draggedRef.current) e.preventDefault() }}
                        className="group flex pt-2 h-24 w-32 shrink-0 flex-col items-center justify-center gap-2 rounded-2xl border border-hc-ink/[0.08] bg-white px-3 transition-all duration-200 hover:-translate-y-1 hover:border-hc-amber hover:shadow-[0_16px_30px_-14px_rgba(23,20,15,0.25)]"
                    >
                        <Image
                            src={mediaUrl(brand.logo_url)!}
                            alt={brand.name}
                            width={80}
                            height={32}
                            unoptimized
                            loading="eager"
                            draggable={false}
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

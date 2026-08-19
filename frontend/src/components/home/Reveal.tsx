'use client'

import { useEffect, useRef, useState, type ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface Props {
    children: ReactNode
    className?: string
    /** Stagger delay in ms, useful for sibling reveals in a grid */
    delay?: number
}

/**
 * Fades + lifts children into view the first time they cross the viewport.
 * Falls back to instantly-visible when IntersectionObserver isn't available
 * or the user has requested reduced motion.
 */
export function Reveal({ children, className, delay = 0 }: Props) {
    const ref = useRef<HTMLDivElement>(null)
    const [visible, setVisible] = useState(false)

    useEffect(() => {
        const node = ref.current
        if (!node) return

        const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
        if (prefersReduced || !('IntersectionObserver' in window)) {
            const id = requestAnimationFrame(() => setVisible(true))
            return () => cancelAnimationFrame(id)
        }

        const io = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting) {
                    setVisible(true)
                    io.unobserve(node)
                }
            },
            { threshold: 0.15 },
        )
        io.observe(node)
        return () => io.disconnect()
    }, [])

    return (
        <div
            ref={ref}
            style={{ transitionDelay: visible ? `${delay}ms` : '0ms' }}
            className={cn(
                'transition-all duration-700 ease-out motion-reduce:transition-none',
                visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4',
                className,
            )}
        >
            {children}
        </div>
    )
}

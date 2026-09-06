'use client'

import Image from 'next/image'
import Link from 'next/link'
import { useStorefront } from '@/storefront/StorefrontProvider'

const VARIANTS = {
    'dark-bg': {
        src: '/brand/logo-lockup-dark-bg.png',
        aspect: 560 / 150,
    },
    'light-bg': {
        src: '/brand/logo-lockup-light-bg.png',
        aspect: 560 / 150,
    },
} as const

export function Logo({
                         variant = 'dark-bg',
                         height = 28,
                         href = '/',
                         priority = false,
                     }: {
    variant?: keyof typeof VARIANTS
    height?: number
    href?: string
    priority?: boolean
}) {
    const { storefront } = useStorefront()
    const fallback = VARIANTS[variant]
    const src = storefront.logo_url || fallback.src
    const aspect = storefront.logo_url ? 560 / 150 : fallback.aspect

    return (
        <Link href={href} className="flex shrink-0 items-center">
            <Image
                src={src}
                alt={storefront.name}
                height={height}
                width={Math.round(height * aspect)}
                priority={priority}
                loading={priority ? 'eager' : undefined}
                unoptimized
            />
        </Link>
    )
}

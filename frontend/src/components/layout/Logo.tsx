import Image from 'next/image'
import Link from 'next/link'

const VARIANTS = {
    'dark-bg': { src: '/brand/logo-lockup-dark-bg.png', aspect: 560 / 150 },
    'light-bg': { src: '/brand/logo-lockup-light-bg.png', aspect: 560 / 150 },
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
    const { src, aspect } = VARIANTS[variant]
    return (
        <Link href={href} className="flex shrink-0 items-center">
            <Image
                src={src}
                alt="HappyCana"
                height={height}
                width={Math.round(height * aspect)}
                priority={priority}
            />
        </Link>
    )
}

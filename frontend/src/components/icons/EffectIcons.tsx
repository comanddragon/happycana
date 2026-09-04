// components/icons/EffectIcons.tsx
// Small face-based icon per effect slug so "Creative", "Sleepy", "Hungry"
// etc. read as distinct moods at a glance instead of an identical dot.
// Every icon shares the same face circle and 24x24 proportions so they
// drop into the same badge size across the home strip and shop pills.
// Unrecognized slugs (any future effect added on the backend) fall back
// to a neutral face rather than breaking.

import type { ReactNode, SVGProps } from 'react'

type IconProps = SVGProps<SVGSVGElement>

const base = {
    viewBox: '0 0 24 24',
    fill: 'none',
    stroke: 'currentColor',
    strokeWidth: 1.5,
    strokeLinecap: 'round' as const,
    strokeLinejoin: 'round' as const,
}

function Face({ children, ...props }: IconProps & { children: ReactNode }) {
    return (
        <svg {...base} {...props}>
            <circle cx="12" cy="12" r="9" />
            {children}
        </svg>
    )
}

export function HappyEffectIcon(props: IconProps) {
    return (
        <Face {...props}>
            <circle cx="9" cy="10" r="1" fill="currentColor" stroke="none" />
            <circle cx="15" cy="10" r="1" fill="currentColor" stroke="none" />
            <path d="M8.2 14c1.1 1.6 2.6 2.4 3.8 2.4s2.7-.8 3.8-2.4" />
        </Face>
    )
}

export function RelaxedEffectIcon(props: IconProps) {
    return (
        <Face {...props}>
            <path d="M7.4 10.2c.7-.7 1.9-.7 2.6 0" />
            <path d="M14 10.2c.7-.7 1.9-.7 2.6 0" />
            <path d="M9 15.2c1 .6 2 .9 3 .9s2-.3 3-.9" />
        </Face>
    )
}

export function SleepyEffectIcon(props: IconProps) {
    return (
        <Face {...props}>
            <path d="M7.4 10.6c.7.7 1.9.7 2.6 0" />
            <path d="M14 10.6c.7.7 1.9.7 2.6 0" />
            <path d="M10.5 15.4h3" />
            <path d="M17 5h3l-3 3h3" />
        </Face>
    )
}

export function EnergizedEffectIcon(props: IconProps) {
    return (
        <Face {...props}>
            <path d="M7 8.8l2.2-1" />
            <path d="M17 8.8l-2.2-1" />
            <circle cx="9" cy="11" r="1.2" fill="currentColor" stroke="none" />
            <circle cx="15" cy="11" r="1.2" fill="currentColor" stroke="none" />
            <ellipse cx="12" cy="15" rx="1.6" ry="1.3" fill="currentColor" stroke="none" />
            <path d="M18 4l-2 3.5h1.6l-1.8 3.5" />
        </Face>
    )
}

export function CreativeEffectIcon(props: IconProps) {
    return (
        <Face {...props}>
            <path d="M8.2 9.6c1.1-.7 2.1.1 1.7 1-.3.7-1.3.7-1.3-.1" />
            <path d="M14.4 9.6c1.1-.7 2.1.1 1.7 1-.3.7-1.3.7-1.3-.1" />
            <path d="M9 15c1 .5 2 .8 3 .8s2-.3 3-.8" />
        </Face>
    )
}

export function InspiredEffectIcon(props: IconProps) {
    return (
        <Face {...props}>
            <circle cx="9" cy="10" r="1" fill="currentColor" stroke="none" />
            <circle cx="15" cy="10" r="1" fill="currentColor" stroke="none" />
            <path d="M8.2 14c1.1 1.6 2.6 2.4 3.8 2.4s2.7-.8 3.8-2.4" />
            <path d="M18 3.5l.6 1.7 1.7.6-1.7.6-.6 1.7-.6-1.7-1.7-.6 1.7-.6z" fill="currentColor" stroke="none" />
        </Face>
    )
}

export function HungryEffectIcon(props: IconProps) {
    return (
        <Face {...props}>
            <circle cx="9" cy="10" r="1" fill="currentColor" stroke="none" />
            <circle cx="15" cy="10" r="1" fill="currentColor" stroke="none" />
            <ellipse cx="12" cy="15.2" rx="2.2" ry="1.9" />
            <path d="M17 4.5v3" />
            <path d="M18 4.5v3" />
            <path d="M19 4.5v3" />
            <path d="M18 7.5v3.5" />
        </Face>
    )
}

export function NeutralEffectIcon(props: IconProps) {
    return (
        <Face {...props}>
            <circle cx="9" cy="10" r="1" fill="currentColor" stroke="none" />
            <circle cx="15" cy="10" r="1" fill="currentColor" stroke="none" />
            <path d="M9 15h6" />
        </Face>
    )
}

const EFFECT_ICONS: Record<string, (props: IconProps) => JSX.Element> = {
    happy: HappyEffectIcon,
    relaxed: RelaxedEffectIcon,
    sleepy: SleepyEffectIcon,
    energized: EnergizedEffectIcon,
    creative: CreativeEffectIcon,
    inspired: InspiredEffectIcon,
    hungry: HungryEffectIcon,
}

export function EffectIcon({ slug, ...props }: IconProps & { slug: string }) {
    const Icon = EFFECT_ICONS[slug] ?? NeutralEffectIcon
    return <Icon {...props} />
}

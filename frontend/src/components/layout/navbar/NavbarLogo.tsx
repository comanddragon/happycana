import Link from 'next/link'
import { AMBER_DOT } from './constants'

export function NavbarLogo({ size = 22 }: { size?: number }) {
    return (
        <Link href="/" className="flex items-center gap-2.5 shrink-0">
            <span className="rounded-full" style={{ ...AMBER_DOT, height: size, width: size }} />
            <span className="font-hc-display italic text-xl font-medium text-hc-paper">HappyCana</span>
        </Link>
    )
}

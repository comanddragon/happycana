import { Logo } from '../Logo'

export function NavbarLogo({ size = 56 }: { size?: number }) {
    return <Logo height={size} priority />
}

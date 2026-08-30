import { Logo } from '../Logo'

export function NavbarLogo({ size = 44 }: { size?: number }) {
    return <Logo height={size} priority />
}

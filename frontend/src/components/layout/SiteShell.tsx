'use client'

import { usePathname } from 'next/navigation'
import { Navbar } from './navbar/Navbar'
import { Footer } from './Footer'

const hiddenRoutes = [
    '/shop/checkout',
    '/login',
    '/register',
]
export function SiteShell({ children }: { children: React.ReactNode }) {
    const pathname = usePathname()
    const hide = hiddenRoutes.some(route =>
        pathname.startsWith(route)
    )
    return (
        <>
            {!hide && <Navbar />}
            {children}
            {!hide && <Footer />}
        </>
    )
}
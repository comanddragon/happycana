// noinspection DuplicatedCode

'use client'

import React, { useState, useSyncExternalStore } from 'react'
import { usePathname, useRouter } from 'next/navigation'
import { useCartStore } from '@/store/cart'
import { useAuthStore } from '@/store/auth'
import { useNotifications, useMarkNotificationRead } from '@/hooks/useApi'
import { useNotificationsWS } from '@/hooks/useWebSocket'
import { authService } from '@/lib/services'
import Cookies from 'js-cookie'

import { NavbarLogo } from '@/components/layout/navbar/NavbarLogo'
import { NavbarDesktopLinks } from '@/components/layout/navbar/NavbarDesktopLinks'
import { NavbarSearch } from '@/components/layout/navbar/NavbarSearch'
import { NavbarNotifications } from '@/components/layout/navbar/NavbarNotifications'
import { NavbarCartButton } from '@/components/layout/navbar/NavbarCartButton'
import { NavbarUserMenu } from '@/components/layout/navbar/NavbarUserMenu'
import { NavbarMobileMenu } from '@/components/layout/navbar/NavbarMobileMenu'

export function Navbar() {
    const pathname = usePathname()
    const router = useRouter()
    const [search, setSearch] = useState('')
    const [searchOpen, setSearchOpen] = useState(false)
    const [mobileOpen, setMobileOpen] = useState(false)

    // useSyncExternalStore is the correct pattern for SSR-safe client detection.
    // Returns false during SSR/hydration, true on the client — no effect needed.
    const mounted = useSyncExternalStore(
        () => () => {},  // subscribe: nothing external to listen to
        () => true,      // getSnapshot (client)
        () => false,     // getServerSnapshot
    )

    const itemCount = useCartStore(s => s.itemCount())
    const toggleCart = useCartStore(s => s.toggleCart)
    const { user, isAuthenticated, isGuest, logout } = useAuthStore()
    // Guests hold a real JWT (so cart/chat "just work") but shouldn't look
    // signed in — the account menu and notifications bell stay hidden for them.
    const showAccountUI = isAuthenticated && !isGuest
    const { data: notifData } = useNotifications()
    const markRead = useMarkNotificationRead()
    useNotificationsWS()

    const unread = notifData?.results.filter(n => !n.is_read).length ?? 0

    const handleLogout = async () => {
        const refresh = Cookies.get('refresh_token') ?? ''
        try { await authService.logout(refresh) } catch {}
        logout()
    }

    const handleSearch = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter' && search.trim()) {
            router.push(`/shop/products?search=${encodeURIComponent(search.trim())}`)
            setSearchOpen(false)
            setSearch('')
        }
    }

    return (
        <header className="sticky top-0 z-40 border-b border-hc-paper/[0.08] bg-hc-canopy/[0.92] backdrop-blur-md">
            <div className="mx-auto max-w-[1180px] px-4 sm:px-6 lg:px-7">
                <div className="flex h-16 items-center justify-between gap-4">

                    <NavbarLogo />

                    <NavbarDesktopLinks pathname={pathname} />

                    <NavbarSearch
                        search={search}
                        setSearch={setSearch}
                        searchOpen={searchOpen}
                        setSearchOpen={setSearchOpen}
                        onKeyDown={handleSearch}
                    />

                    {/* Right actions */}
                    <div className="flex items-center gap-1">

                        {mounted && showAccountUI && (
                            <NavbarNotifications
                                notifications={notifData?.results}
                                unread={unread}
                                onMarkRead={id => markRead.mutate(id)}
                            />
                        )}

                        <NavbarCartButton itemCount={itemCount} mounted={mounted} onClick={toggleCart} />

                        <NavbarUserMenu
                            mounted={mounted}
                            isAuthenticated={showAccountUI}
                            user={user}
                            onLogout={handleLogout}
                        />

                        <NavbarMobileMenu
                            open={mobileOpen}
                            setOpen={setMobileOpen}
                            search={search}
                            setSearch={setSearch}
                            onKeyDown={handleSearch}
                            isAuthenticated={mounted && showAccountUI}
                        />
                    </div>
                </div>
            </div>
        </header>
    )
}

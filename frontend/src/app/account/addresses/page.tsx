'use client'

import Link from 'next/link'
import React, { useState } from 'react'
import { usePathname, useRouter } from 'next/navigation'
import { ShoppingBag, Search, Bell, Menu, X, LogOut, Package, MapPin, Settings } from 'lucide-react'
import { cn, formatRelativeDate } from '@/lib/utils'
import { useCartStore } from '@/store/cart'
import { useAuthStore } from '@/store/auth'
import { useNotifications, useMarkNotificationRead } from '@/hooks/useApi'
import { useNotificationsWS } from '@/hooks/useWebSocket'
import { useMounted } from '@/hooks/useMounted'
import { authService } from '@/lib/services'
import Cookies from 'js-cookie'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Sheet, SheetContent, SheetTrigger, SheetTitle, SheetDescription } from '@/components/ui/sheet'
import {
    DropdownMenu, DropdownMenuContent, DropdownMenuItem,
    DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'

const NAV_LINKS = [
    { href: '/shop', label: 'Shop' },
    { href: '/shop/products', label: 'Products' },
]

export default function Navbar() {
    const pathname  = usePathname()
    const router    = useRouter()
    const mounted = useMounted()
    const [search, setSearch]         = useState('')
    const [searchOpen, setSearchOpen] = useState(false)

    const itemCount  = useCartStore(s => s.itemCount())
    const toggleCart = useCartStore(s => s.toggleCart)
    const { user, isAuthenticated, logout } = useAuthStore()
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
        <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-xl border-b border-border">
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                <div className="flex h-16 items-center justify-between gap-4">

                    {/* Logo */}
                    <Link href="/" className="flex items-center gap-2 shrink-0">
                        <div className="h-8 w-8 rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center">
                            <ShoppingBag className="h-4 w-4 text-white" />
                        </div>
                        <span className="font-display text-xl font-semibold tracking-tight">ShopForge</span>
                    </Link>

                    {/* Desktop nav */}
                    <nav className="hidden md:flex items-center gap-1">
                        {NAV_LINKS.map(({ href, label }) => (
                            <Link key={href} href={href}>
                                <Button variant={pathname.startsWith(href) ? 'secondary' : 'ghost'} size="sm">
                                    {label}
                                </Button>
                            </Link>
                        ))}
                    </nav>

                    {/* Search */}
                    <div className={cn('hidden md:flex items-center transition-all duration-200', searchOpen ? 'flex-1 max-w-sm' : '')}>
                        {searchOpen ? (
                            <div className="flex items-center gap-2 w-full">
                                <Input autoFocus placeholder="Search products…" value={search}
                                       onChange={e => setSearch(e.target.value)} onKeyDown={handleSearch} />
                                <Button variant="ghost" size="icon" onClick={() => { setSearchOpen(false); setSearch('') }}>
                                    <X className="h-4 w-4" />
                                </Button>
                            </div>
                        ) : (
                            <Button variant="ghost" size="icon" onClick={() => setSearchOpen(true)} aria-label="Search">
                                <Search className="h-4 w-4" />
                            </Button>
                        )}
                    </div>

                    {/* Right actions */}
                    <div className="flex items-center gap-1">

                        {/* Notifications */}
                        {mounted && isAuthenticated && (
                            <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                    <Button variant="ghost" size="icon" className="relative">
                                        <Bell className="h-4 w-4" />
                                        {unread > 0 && (
                                            <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-brand-500 ring-2 ring-white" />
                                        )}
                                    </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end" className="w-80 p-0">
                                    <div className="flex items-center justify-between px-4 py-3 border-b">
                                        <span className="text-sm font-medium">Notifications</span>
                                        {unread > 0 && <Badge variant="secondary">{unread} new</Badge>}
                                    </div>
                                    <ScrollArea className="max-h-80">
                                        {!notifData?.results.length && (
                                            <p className="p-4 text-sm text-muted-foreground text-center">No notifications</p>
                                        )}
                                        {notifData?.results.slice(0, 8).map(n => (
                                            <button key={n.id} onClick={() => markRead.mutate(n.id)}
                                                    className={cn('w-full text-left px-4 py-3 hover:bg-muted transition-colors border-b last:border-0',
                                                        !n.is_read && 'bg-brand-50/40')}>
                                                <div className="flex gap-3">
                                                    {!n.is_read && <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-brand-500" />}
                                                    <div className={cn(!n.is_read ? '' : 'ml-5')}>
                                                        <p className="text-sm font-medium">{n.title}</p>
                                                        <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">{n.body}</p>
                                                        <p className="text-xs text-muted-foreground/60 mt-1">{formatRelativeDate(n.created_at)}</p>
                                                    </div>
                                                </div>
                                            </button>
                                        ))}
                                    </ScrollArea>
                                </DropdownMenuContent>
                            </DropdownMenu>
                        )}

                        {/* Cart */}
                        <Button variant="ghost" size="icon" className="relative" onClick={toggleCart} aria-label="Cart">
                            <ShoppingBag className="h-4 w-4" />
                            {mounted && itemCount > 0 && (
                                <span className="absolute -top-0.5 -right-0.5 h-4 w-4 rounded-full bg-brand-600 text-white text-[10px] font-bold flex items-center justify-center">
                  {itemCount > 9 ? '9+' : itemCount}
                </span>
                            )}
                        </Button>

                        {/* User menu */}
                        {mounted && isAuthenticated ? (
                            <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                    <Button variant="ghost" className="gap-2 px-2">
                                        <Avatar className="h-7 w-7">
                                            <AvatarFallback className="bg-gradient-to-br from-brand-400 to-brand-600 text-white text-xs">
                                                {user?.first_name?.[0] ?? user?.email?.[0]?.toUpperCase() ?? 'U'}
                                            </AvatarFallback>
                                        </Avatar>
                                        <span className="hidden lg:block max-w-[100px] truncate text-sm">
                      {user?.first_name || user?.email?.split('@')[0]}
                    </span>
                                    </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end" className="w-52">
                                    <DropdownMenuLabel className="text-xs font-normal text-muted-foreground truncate">
                                        {user?.email}
                                    </DropdownMenuLabel>
                                    <DropdownMenuSeparator />
                                    <DropdownMenuItem asChild>
                                        <Link href="/account/profile" className="flex items-center gap-2 cursor-pointer">
                                            <Settings className="h-4 w-4" /> Profile
                                        </Link>
                                    </DropdownMenuItem>
                                    <DropdownMenuItem asChild>
                                        <Link href="/account/orders" className="flex items-center gap-2 cursor-pointer">
                                            <Package className="h-4 w-4" /> Orders
                                        </Link>
                                    </DropdownMenuItem>
                                    <DropdownMenuItem asChild>
                                        <Link href="/account/addresses" className="flex items-center gap-2 cursor-pointer">
                                            <MapPin className="h-4 w-4" /> Addresses
                                        </Link>
                                    </DropdownMenuItem>
                                    <DropdownMenuSeparator />
                                    <DropdownMenuItem onClick={handleLogout} className="text-destructive focus:text-destructive cursor-pointer">
                                        <LogOut className="h-4 w-4 mr-2" /> Sign out
                                    </DropdownMenuItem>
                                </DropdownMenuContent>
                            </DropdownMenu>
                        ) : mounted ? (
                            <Button asChild size="sm">
                                <Link href="/login">Sign in</Link>
                            </Button>
                        ) : null}

                        {/* Mobile menu */}
                        <Sheet>
                            <SheetTrigger asChild>
                                <Button variant="ghost" size="icon" className="md:hidden">
                                    <Menu className="h-4 w-4" />
                                </Button>
                            </SheetTrigger>
                            <SheetContent side="left" className="w-72 p-0">
                                <SheetTitle className="sr-only">Navigation menu</SheetTitle>
                                <SheetDescription className="sr-only">Browse site navigation and search</SheetDescription>
                                <div className="flex items-center gap-2 p-4 border-b">
                                    <div className="h-7 w-7 rounded-lg bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center">
                                        <ShoppingBag className="h-3.5 w-3.5 text-white" />
                                    </div>
                                    <span className="font-display font-semibold">ShopForge</span>
                                </div>
                                <div className="p-4 space-y-1">
                                    <Input placeholder="Search products…" className="mb-3"
                                           value={search} onChange={e => setSearch(e.target.value)} onKeyDown={handleSearch} />
                                    {NAV_LINKS.map(({ href, label }) => (
                                        <Link key={href} href={href}>
                                            <Button variant={pathname.startsWith(href) ? 'secondary' : 'ghost'}
                                                    className="w-full justify-start">{label}</Button>
                                        </Link>
                                    ))}
                                </div>
                            </SheetContent>
                        </Sheet>
                    </div>
                </div>
            </div>
        </header>
    )
}
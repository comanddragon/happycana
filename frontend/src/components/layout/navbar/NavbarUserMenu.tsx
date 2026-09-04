import Link from 'next/link'
import { Mail, LogOut, Package, MapPin, Settings } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import {
    DropdownMenu, DropdownMenuContent, DropdownMenuItem,
    DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { AMBER_DOT, AMBER_BUTTON, AMBER_BUTTON_STYLE } from './constants'

interface NavbarUserMenuProps {
    mounted: boolean
    isAuthenticated: boolean
    user: { first_name?: string; email?: string } | null | undefined
    onLogout: () => void
}

export function NavbarUserMenu({ mounted, isAuthenticated, user, onLogout }: NavbarUserMenuProps) {
    if (!mounted) return null

    if (!isAuthenticated) {
        return (
            <div className="hidden md:block">
                <Button asChild size="sm" className={AMBER_BUTTON} style={AMBER_BUTTON_STYLE}>
                    <Link href="/login">Sign in</Link>
                </Button>
            </div>
        )
    }

    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="gap-2 px-2 text-hc-sage hover:bg-hc-paper/10 hover:text-hc-paper">
                    <Avatar className="h-7 w-7">
                        <AvatarFallback className="text-white text-xs" style={AMBER_DOT}>
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
                    <Link href="/account/chat" className="flex items-center gap-2 cursor-pointer">
                        <Mail className="h-4 w-4" /> Chat
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
                <DropdownMenuItem onClick={onLogout} className="text-destructive focus:text-destructive cursor-pointer">
                    <LogOut className="h-4 w-4 mr-2" /> Sign out
                </DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>
    )
}

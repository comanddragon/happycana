import Link from 'next/link'
import { Menu, X } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Sheet, SheetContent, SheetTrigger, SheetTitle, SheetDescription } from '@/components/ui/sheet'
import { NAV_LINKS } from './constants'
import { Logo } from '../Logo'
import { useCategoriesMenuTree } from '@/hooks/useCategoriesMenuTree'
import { NavMobileTreeItem } from '@/components/layout/navbar/NavMobileTreeItem'
import { AMBER_BUTTON, AMBER_BUTTON_STYLE } from './constants'
import React from "react";

interface NavbarMobileMenuProps {
    open: boolean
    setOpen: (open: boolean) => void
    search: string
    setSearch: (value: string) => void
    onKeyDown: (e: React.KeyboardEvent<HTMLInputElement>) => void
    isAuthenticated: boolean
}

export function NavbarMobileMenu({
                                     open,
                                     setOpen,
                                     search,
                                     setSearch,
                                     onKeyDown,
                                     isAuthenticated,
                                 }: NavbarMobileMenuProps) {
    const { rootNodes } = useCategoriesMenuTree()

    return (
        <Sheet open={open} onOpenChange={setOpen}>
            <SheetTrigger asChild>
                <button
                    className="md:hidden flex h-8 w-8 items-center justify-center text-hc-sage hover:text-hc-paper"
                    aria-label={open ? 'Close menu' : 'Open menu'}
                >
                    {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
                </button>
            </SheetTrigger>

            <SheetContent
                side="left"
                className="w-72 p-0 bg-hc-canopy-2 border-hc-paper/10 text-hc-paper"
            >
                <SheetTitle className="sr-only">Navigation menu</SheetTitle>
                <SheetDescription className="sr-only">
                    Browse site navigation and search
                </SheetDescription>

                <div className="flex items-center gap-2.5 p-4 border-b border-hc-paper/10">
                    <Logo height={36} priority />
                </div>

                <div className="flex-1 min-h-0 overflow-y-auto p-4 space-y-1">
                    <Input
                        placeholder="Search the menu…"
                        className="mb-3 border-hc-paper/20 bg-hc-paper/[0.06] text-hc-paper placeholder:text-hc-sage-dim focus-visible:ring-hc-amber-light/40"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        onKeyDown={onKeyDown}
                    />

                    {NAV_LINKS.map((item) => {
                        if (item.dynamic) {
                            return (
                                <NavMobileTreeItem
                                    key={item.label}
                                    node={{ label: item.label, children: rootNodes }}
                                    onNavigateAction={() => setOpen(false)}
                                />
                            )
                        }

                        return (
                            <Link
                                key={item.label}
                                href={item.href!}
                                onClick={() => setOpen(false)}
                                className="block rounded-lg px-3 py-2.5 text-sm font-medium text-hc-sage transition-colors hover:bg-hc-paper/5 hover:text-hc-paper"
                            >
                                {item.label}
                            </Link>
                        )
                    })}
                </div>

                {!isAuthenticated && (
                    <div className="mt-auto border-t border-hc-paper/10 p-4">
                        <Link
                            href="/login"
                            onClick={() => setOpen(false)}
                            className={`${AMBER_BUTTON} w-full`}
                            style={AMBER_BUTTON_STYLE}
                        >
                            Sign in
                        </Link>
                    </div>
                )}
            </SheetContent>
        </Sheet>
    )
}

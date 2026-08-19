'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Menu, X } from 'lucide-react'

const LINKS = [
    { label: 'Flower', href: '#batch' },
    { label: 'Edibles', href: '#batch' },
    { label: 'Vapes', href: '#batch' },
    { label: 'Shop by effect', href: '#effects' },
    { label: 'Lab results', href: '#lab' },
]

export function HcNav() {
    const [open, setOpen] = useState(false)

    return (
        <header className="sticky top-0 z-[100] border-b border-hc-paper/[0.08] bg-hc-canopy/[0.86] backdrop-blur-md">
            <div className="mx-auto max-w-[1180px] px-7">
                <nav className="flex items-center justify-between py-4">
                    <Link href="#top" className="flex items-center gap-2.5">
                        <span
                            className="h-[22px] w-[22px] rounded-full"
                            style={{ background: 'radial-gradient(circle at 32% 28%, var(--color-hc-amber-light), var(--color-hc-amber) 60%, var(--color-hc-amber-dim))' }}
                        />
                        <span className="font-hc-display italic text-xl font-medium text-hc-paper">HappyCana</span>
                    </Link>

                    <ul className="hidden md:flex items-center gap-8">
                        {LINKS.map(link => (
                            <li key={link.label}>
                                <a href={link.href} className="text-sm font-medium text-hc-sage transition-colors hover:text-hc-paper">
                                    {link.label}
                                </a>
                            </li>
                        ))}
                    </ul>

                    <div className="flex items-center gap-4">
                        <a href="#batch" className="hidden sm:flex items-center gap-1.5 font-hc-mono text-[13px] text-hc-paper" aria-label="Cart, 0 items">
                            Cart · 0
                        </a>
                        <button
                            onClick={() => setOpen(o => !o)}
                            className="md:hidden flex h-8 w-8 items-center justify-center text-hc-paper"
                            aria-label={open ? 'Close menu' : 'Open menu'}
                            aria-expanded={open}
                        >
                            {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
                        </button>
                    </div>
                </nav>

                {open && (
                    <ul className="md:hidden flex flex-col gap-1 pb-5">
                        {LINKS.map(link => (
                            <li key={link.label}>
                                <a
                                    href={link.href}
                                    onClick={() => setOpen(false)}
                                    className="block rounded-lg px-2 py-2.5 text-sm font-medium text-hc-sage transition-colors hover:bg-hc-paper/5 hover:text-hc-paper"
                                >
                                    {link.label}
                                </a>
                            </li>
                        ))}
                    </ul>
                )}
            </div>
        </header>
    )
}

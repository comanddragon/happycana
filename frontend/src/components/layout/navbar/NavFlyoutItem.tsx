'use client'

import { useRef, useState } from 'react'
import Link from 'next/link'
import { ChevronRight } from 'lucide-react'
import { cn } from '@/lib/utils'

// Generic tree node — a menu item that may itself contain a nested
// flyout of further items. Works at any depth: Categories → Subcategory
// → Sub-subcategory → ..., or Categories → Brands → a specific brand, etc.
export interface MenuNode {
    label: string
    href?: string
    children?: MenuNode[]
}

const CLOSE_DELAY_MS = 150

export function NavFlyoutItem({ node }: { node: MenuNode }) {
    const [open, setOpen] = useState(false)
    const closeTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

    const hasChildren = !!node.children?.length

    const handleEnter = () => {
        if (closeTimer.current) clearTimeout(closeTimer.current)
        setOpen(true)
    }
    const handleLeave = () => {
        closeTimer.current = setTimeout(() => setOpen(false), CLOSE_DELAY_MS)
    }

    const rowClasses = cn(
        'flex items-center gap-2 rounded-lg px-4 py-2 text-sm text-hc-sage transition-colors',
        'hover:bg-white/5 hover:text-hc-paper',
    )

    return (
        <div
            className="relative"
            onMouseEnter={hasChildren ? handleEnter : undefined}
            onMouseLeave={hasChildren ? handleLeave : undefined}
        >
            {node.href ? (
                <Link href={node.href} className={cn(rowClasses, 'justify-between')}>
                    <span className="truncate">{node.label}</span>
                    {hasChildren && <ChevronRight className="h-3.5 w-3.5 shrink-0 opacity-60" />}
                </Link>
            ) : (
                <div className={cn(rowClasses, 'justify-between cursor-default')}>
                    <span className="truncate">{node.label}</span>
                    {hasChildren && <ChevronRight className="h-3.5 w-3.5 shrink-0 opacity-60" />}
                </div>
            )}

            {hasChildren && open && (
                <div
                    className="absolute left-full top-0 z-50 ml-1 min-w-[200px] max-h-[360px] overflow-y-auto rounded-xl border border-white/10 bg-hc-canopy-2 p-2 shadow-xl"
                    onMouseEnter={handleEnter}
                    onMouseLeave={handleLeave}
                >
                    {node.children!.map((child, i) => (
                        <NavFlyoutItem key={`${child.label}-${child.href ?? i}`} node={child} />
                    ))}
                </div>
            )}
        </div>
    )
}
